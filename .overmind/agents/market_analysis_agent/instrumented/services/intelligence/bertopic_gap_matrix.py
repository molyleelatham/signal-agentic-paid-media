"""
BERTopic Gap Matrix implementation.

This implements Module 2 from the technical spec:
- Topic clustering using BERTopic
- Three-axis scoring (competitor, intent, brand)
- Zone classification (gap, contested, owned, ignore, monitor)
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import numpy as np
import torch
from bertopic import BERTopic
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from umap import UMAP

from shared.models.topic_cluster import ZoneType


class Document:
    """Document model for topic modeling."""
    
    def __init__(
        self,
        content: str,
        source_type: str,  # competitor, market, social, brand
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        self.content = content
        self.source_type = source_type
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}


class TopicClusterResult:
    """Result of topic clustering."""
    
    def __init__(
        self,
        topic_id: int,
        name: str,
        documents: List[Document],
        competitor_score: float,
        intent_score: float,
        brand_score: float,
        velocity: float,
        zone: str
    ):
        self.topic_id = topic_id
        self.name = name
        self.documents = documents
        self.competitor_score = competitor_score
        self.intent_score = intent_score
        self.brand_score = brand_score
        self.velocity = velocity
        self.zone = zone


class ThradIntentClassifier:
    """
    Local Thrad DistilBERT conversation classifier.
    
    This implements Module 1.2 - Thrad BERT intent signal using the local model.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize Thrad intent classifier with local model.
        
        Args:
            model_path: Path to local Thrad model. If not provided, uses default path.
        """
        if model_path is None:
            model_path = "/Users/molyleelatham/.cache/huggingface/hub/models--Thrad--thrad-distilbert-conversation-classifier/snapshots/9e7eeadcf69c3f9d286729bb8b6a4f88f7e4faa2"
        
        print(f"Loading Thrad model from: {model_path}")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        
        # Move to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Thrad model loaded on device: {self.device}")
        
        # Intent labels (these should match the model's output classes)
        self.intent_labels = [
            "purchase_intent",
            "research_intent", 
            "awareness_intent",
            "brand_specific_intent"
        ]
    
    def classify_intent(self, text: str) -> Dict[str, float]:
        """
        Classify intent of a single text.
        
        Args:
            text: Input text to classify
        
        Returns:
            Dictionary mapping intent types to probabilities
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Classify
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
        
        # Convert to dictionary
        probs = probabilities[0].cpu().numpy()
        
        return {
            label: float(prob)
            for label, prob in zip(self.intent_labels, probs)
        }
    
    def classify_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Classify intent for multiple texts.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of intent probability dictionaries
        """
        # Tokenize batch
        inputs = self.tokenizer(
            texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Classify
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
        
        # Convert to list of dictionaries
        results = []
        probs = probabilities.cpu().numpy()
        
        for prob in probs:
            results.append({
                label: float(p)
                for label, p in zip(self.intent_labels, prob)
            })
        
        return results
    
    def calculate_topic_intent_score(
        self,
        documents: List[Document],
        intent_types: List[str] = None
    ) -> float:
        """
        Calculate aggregate intent score for a topic cluster.
        
        Args:
            documents: Documents in the topic cluster
            intent_types: Intent types to include in score
        
        Returns:
            Normalized intent score (0-1)
        """
        if intent_types is None:
            intent_types = ["purchase_intent", "research_intent"]
        
        if not documents:
            return 0.0
        
        # Classify all documents
        texts = [doc.content for doc in documents]
        intent_results = self.classify_batch(texts)
        
        # Aggregate intent scores
        total_intent_volume = 0.0
        for result in intent_results:
            # Sum relevant intent types
            topic_intent = sum(result.get(intent_type, 0.0) for intent_type in intent_types)
            total_intent_volume += topic_intent
        
        # Normalize by number of documents
        avg_intent = total_intent_volume / len(documents)
        
        return min(1.0, avg_intent)  # Cap at 1.0


class BERTopicGapMatrix:
    """
    BERTopic Gap Matrix implementation.
    
    This implements the full pipeline from Module 2:
    1. Embedding with sentence-transformers
    2. Dimensionality reduction with UMAP
    3. Clustering with HDBSCAN
    4. BERTopic fitting
    5. Temporal slicing for topic velocity
    6. Three-axis scoring (with Thrad intent)
    7. Zone classification
    """
    
    def __init__(
        self,
        embedding_model: str = "all-mpnet-base-v2",
        umap_n_neighbors: int = 15,
        umap_n_components: int = 5,
        umap_min_dist: float = 0.0,
        hdbscan_min_cluster_size: int = 15,
        hdbscan_min_samples: int = 10,
        thrad_model_path: str = None
    ):
        """
        Initialize BERTopic Gap Matrix.
        
        Args:
            embedding_model: Sentence transformer model name
            umap_n_neighbors: UMAP n_neighbors parameter
            umap_n_components: UMAP n_components parameter
            umap_min_dist: UMAP min_dist parameter
            hdbscan_min_cluster_size: HDBSCAN min_cluster_size
            hdbscan_min_samples: HDBSCAN min_samples
            thrad_model_path: Path to local Thrad model
        """
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize UMAP
        self.umap_model = UMAP(
            n_neighbors=umap_n_neighbors,
            n_components=umap_n_components,
            min_dist=umap_min_dist,
            metric='cosine',
            random_state=42
        )
        
        # Initialize HDBSCAN
        self.hdbscan_model = HDBSCAN(
            min_cluster_size=hdbscan_min_cluster_size,
            min_samples=hdbscan_min_samples,
            metric='euclidean',
            cluster_selection_method='eom',
            prediction_data=True
        )
        
        # Initialize Thrad intent classifier
        self.thrad_classifier = ThradIntentClassifier(thrad_model_path)
        
        # BERTopic model (initialized during fit)
        self.topic_model: Optional[BERTopic] = None
        
        # Thresholds for zone classification
        self.thresholds = {
            "high": 0.6,
            "low": 0.3
        }
    
    def fit_transform(
        self,
        documents: List[Document],
        timestamps: Optional[List[datetime]] = None
    ) -> List[TopicClusterResult]:
        """
        Fit BERTopic model and transform documents into topic clusters.
        
        Args:
            documents: List of documents to cluster
            timestamps: Optional timestamps for temporal analysis
        
        Returns:
            List of TopicClusterResult with scoring and zone classification
        """
        if not documents:
            return []
        
        # Extract content and source types
        contents = [doc.content for doc in documents]
        source_types = [doc.source_type for doc in documents]
        
        # Step 1: Embedding
        print("Generating embeddings...")
        embeddings = self.embedding_model.encode(
            contents,
            batch_size=32,
            show_progress_bar=True
        )
        
        # Step 2-4: Fit BERTopic with custom UMAP and HDBSCAN
        print("Fitting BERTopic model...")
        self.topic_model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=self.umap_model,
            hdbscan_model=self.hdbscan_model,
            nr_topics="auto",
            verbose=True
        )
        
        topics, probs = self.topic_model.fit_transform(contents, embeddings)
        
        # Step 5: Temporal slicing (if timestamps provided)
        velocity_scores = {}
        if timestamps and len(timestamps) == len(documents):
            print("Calculating topic velocity...")
            velocity_scores = self._calculate_topic_velocity(
                self.topic_model,
                contents,
                timestamps
            )
        
        # Group documents by topic
        topic_to_docs = {}
        for doc, topic in zip(documents, topics):
            if topic == -1:  # Outliers
                continue
            if topic not in topic_to_docs:
                topic_to_docs[topic] = []
            topic_to_docs[topic].append(doc)
        
        # Step 3: Three-axis scoring and zone classification
        results = []
        for topic_id, topic_docs in topic_to_docs.items():
            print(f"Scoring topic {topic_id} with {len(topic_docs)} documents...")
            
            # Calculate scores
            competitor_score = self._calculate_competitor_score(topic_docs)
            intent_score = self.thrad_classifier.calculate_topic_intent_score(topic_docs)
            brand_score = self._calculate_brand_score(topic_docs)
            velocity = velocity_scores.get(topic_id, 0.0)
            
            # Classify zone
            zone = self._classify_zone(
                competitor_score,
                intent_score,
                brand_score
            )
            
            # Generate topic name
            topic_name = self._generate_topic_name(topic_id, topic_docs)
            
            result = TopicClusterResult(
                topic_id=topic_id,
                name=topic_name,
                documents=topic_docs,
                competitor_score=competitor_score,
                intent_score=intent_score,
                brand_score=brand_score,
                velocity=velocity,
                zone=zone
            )
            results.append(result)
        
        return results
    
    def _calculate_competitor_score(self, documents: List[Document]) -> float:
        """
        Calculate competitor coverage score.
        
        competitor_score = n_competitor_docs / total_cluster_docs
        """
        if not documents:
            return 0.0
        
        competitor_docs = [d for d in documents if d.source_type == "competitor"]
        return len(competitor_docs) / len(documents)
    
    def _calculate_brand_score(self, documents: List[Document]) -> float:
        """
        Calculate brand presence score.
        
        brand_score = n_brand_docs / total_cluster_docs
        """
        if not documents:
            return 0.0
        
        brand_docs = [d for d in documents if d.source_type == "brand"]
        return len(brand_docs) / len(documents)
    
    def _calculate_topic_velocity(
        self,
        topic_model: BERTopic,
        documents: List[str],
        timestamps: List[datetime]
    ) -> Dict[int, float]:
        """
        Calculate topic velocity (rate of change over time).
        
        Uses BERTopic's topics_over_time functionality.
        """
        try:
            topics_over_time = topic_model.topics_over_time(
                docs=documents,
                timestamps=timestamps,
                nr_bins=6,  # Monthly bins, last 6 months
                evolution_tuning=True,
                global_tuning=True
            )
            
            # Calculate velocity as rate of change
            velocity_scores = {}
            for topic_id in topics_over_time['Topic'].unique():
                if topic_id == -1:  # Skip outliers
                    continue
                
                topic_data = topics_over_time[topics_over_time['Topic'] == topic_id]
                if len(topic_data) < 2:
                    velocity_scores[topic_id] = 0.0
                    continue
                
                # Simple velocity: slope of frequency over time
                frequencies = topic_data['Frequency'].values
                if len(frequencies) >= 2:
                    velocity = np.polyfit(range(len(frequencies)), frequencies, 1)[0]
                    velocity_scores[topic_id] = float(velocity)
                else:
                    velocity_scores[topic_id] = 0.0
            
            return velocity_scores
        
        except Exception as e:
            print(f"Error calculating topic velocity: {e}")
            return {}
    
    def _classify_zone(
        self,
        competitor_score: float,
        intent_score: float,
        brand_score: float
    ) -> str:
        """
        Classify topic cluster into strategic zone.
        
        Implements the zone classification logic from Module 2.4:
        - gap: High demand, competitors present, brand absent
        - contested: High demand, competitors present, brand present
        - owned: High demand, competitors absent, brand present
        - ignore: Low demand
        - monitor: Ambiguous
        """
        H = self.thresholds["high"]
        L = self.thresholds["low"]
        
        if competitor_score > H and intent_score > H and brand_score < L:
            return ZoneType.GAP
        elif competitor_score > H and intent_score > H and brand_score >= L:
            return ZoneType.CONTESTED
        elif competitor_score < L and intent_score > H and brand_score > H:
            return ZoneType.OWNED
        elif intent_score < L:
            return ZoneType.IGNORE
        else:
            return ZoneType.MONITOR
    
    def _generate_topic_name(self, topic_id: int, documents: List[Document]) -> str:
        """
        Generate human-readable topic name.
        
        Uses BERTopic's topic labels or generates from documents.
        """
        if self.topic_model is None:
            return f"Topic {topic_id}"
        
        try:
            # Get topic labels from BERTopic
            topic_labels = self.topic_model.get_topic_info()
            topic_info = topic_labels[topic_labels['Topic'] == topic_id]
            
            if not topic_info.empty:
                name = topic_info.iloc[0]['Name']
                # Clean up the name
                return name.replace("_", " ").title()
        
        except Exception as e:
            print(f"Error generating topic name: {e}")
        
        # Fallback: use first few words of first document
        if documents:
            first_words = documents[0].content.split()[:5]
            return " ".join(first_words).title()
        
        return f"Topic {topic_id}"
    
    def get_gap_matrix_visualization_data(self, results: List[TopicClusterResult]) -> List[Dict]:
        """
        Get data for gap matrix visualization.
        
        Returns data for scatter plot with:
        - X axis: competitor coverage
        - Y axis: intent volume
        - Bubble size: brand presence
        - Color: zone
        """
        visualization_data = []
        
        for result in results:
            visualization_data.append({
                "x": result.competitor_score,
                "y": result.intent_score,
                "size": result.brand_score * 100,  # Scale for visibility
                "color": result.zone,
                "label": result.name,
                "topic_id": result.topic_id,
                "velocity": result.velocity
            })
        
        return visualization_data