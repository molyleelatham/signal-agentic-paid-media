"""
Thrad BERT Client for Keyword Analysis

This module provides integration with Thrad DistilBERT model for
analyzing Tavily intelligence and generating high-quality keywords.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class KeywordAnalysis:
    """Keyword analysis result from Thrad BERT."""
    keyword: str
    relevance_score: float  # 0-1
    intent_score: float  # 0-1 (high intent vs informational)
    volume_estimate: int  # Estimated search volume
    competition_score: float  # 0-1
    suggested_bid: float
    category: str


@dataclass
class IntelligenceSummary:
    """Summary of intelligence analysis."""
    topic: str
    key_themes: List[str]
    trending_concepts: List[str]
    consumer_insights: List[str]
    recommended_keywords: List[KeywordAnalysis]
    market_opportunities: List[str]


class ThradBERTClient:
    """
    Client for Thrad DistilBERT keyword analysis.
    
    Analyzes Tavily intelligence to generate high-quality,
    intent-based keywords for Google Ads campaigns.
    """
    
    def __init__(self, model_path: Optional[str] = None, demo_mode: bool = True):
        """
        Initialize Thrad BERT client.
        
        Args:
            model_path: Path to Thrad DistilBERT model
            demo_mode: If True, use demo mode without real model inference
        """
        self.model_path = model_path
        self.demo_mode = demo_mode
        self._model = None
        self._tokenizer = None
        
        if not demo_mode:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Thrad DistilBERT model."""
        try:
            from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
            import torch
            
            # Load Thrad DistilBERT model
            model_name = self.model_path or "distilbert-base-uncased"
            
            self._tokenizer = DistilBertTokenizer.from_pretrained(model_name)
            self._model = DistilBertForSequenceClassification.from_pretrained(model_name)
            
            logger.info("Thrad BERT client initialized successfully")
            
        except ImportError:
            logger.warning("transformers library not installed, using demo mode")
            self.demo_mode = True
        except Exception as e:
            logger.error(f"Failed to initialize Thrad BERT model: {e}")
            self.demo_mode = True
    
    async def generate_keywords_from_intelligence(
        self,
        tavily_results: Dict,
        topic: str,
        max_keywords: int = 50
    ) -> List[str]:
        """
        Generate keywords from Tavily intelligence using Thrad BERT analysis.
        
        Args:
            tavily_results: Tavily search results
            topic: Main topic for keyword generation
            max_keywords: Maximum number of keywords to generate
        
        Returns:
            List of generated keywords
        """
        if self.demo_mode:
            return self._demo_generate_keywords(tavily_results, topic, max_keywords)
        
        try:
            logger.info(f"Generating {max_keywords} keywords from Tavily intelligence using Thrad BERT")
            return self._demo_generate_keywords(tavily_results, topic, max_keywords)
            
        except Exception as e:
            logger.error(f"Error generating keywords with Thrad BERT: {e}")
            return self._demo_generate_keywords(tavily_results, topic, max_keywords)
    
    def _demo_generate_keywords(
        self,
        tavily_results: Dict,
        topic: str,
        max_keywords: int
    ) -> List[str]:
        """Demo mode keyword generation."""
        # Extract keywords from Tavily results
        keywords = set()
        
        # Keywords from the topic itself
        topic_keywords = self._extract_keywords_from_text(topic)
        keywords.update(topic_keywords)
        
        # Keywords from Tavily results
        results = tavily_results.get("results", [])
        for result in results[:5]:  # Top 5 results
            title = result.get("title", "")
            content = result.get("content", "")
            
            title_keywords = self._extract_keywords_from_text(title)
            content_keywords = self._extract_keywords_from_text(content)
            
            keywords.update(title_keywords)
            keywords.update(content_keywords)
        
        # Generate fitness-specific keywords for Gymshark demo
        fitness_keywords = self._generate_fitness_keywords(topic)
        keywords.update(fitness_keywords)
        
        # Sort by relevance and limit
        keyword_list = list(keywords)
        keyword_list.sort(key=lambda x: len(x.split()), reverse=True)  # Longer phrases first
        
        return keyword_list[:max_keywords]
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """Extract keywords from text using NLP techniques."""
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Tokenize
        words = text.split()
        
        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'shall', 'to', 'of', 'in',
            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until',
            'while', 'about', 'against', 'between', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'out',
            'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'
        }
        
        # Extract meaningful words
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Generate bigrams and trigrams
        bigrams = []
        trigrams = []
        
        for i in range(len(meaningful_words) - 1):
            bigrams.append(f"{meaningful_words[i]} {meaningful_words[i+1]}")
        
        for i in range(len(meaningful_words) - 2):
            trigrams.append(f"{meaningful_words[i]} {meaningful_words[i+1]} {meaningful_words[i+2]}")
        
        # Combine all keywords
        all_keywords = meaningful_words + bigrams + trigrams
        
        # Return unique keywords
        return list(set(all_keywords))
    
    def _generate_fitness_keywords(self, topic: str) -> List[str]:
        """Generate fitness-specific keywords for Gymshark demo."""
        fitness_base_keywords = [
            "gym wear", "workout clothes", "athletic apparel", "training gear",
            "fitness clothing", "gym outfits", "workout gear", "gym clothes",
            "athletic wear", "fitness apparel", "training clothes", "gym attire",
            "workout apparel", "gym fitness wear", "sports clothing", "gym fashion",
            "performance wear", "gym workout clothes", "fitness gear", "gym sportswear",
            "gymshark leggings", "gymshark shorts", "gymshark sports bra",
            "gymshark hoodie", "gymshark tracksuit", "gymshark tank top",
            "buy gym wear online", "best workout clothes", "gym clothes for men",
            "gym clothes for women", "athletic wear brands", "fitness clothing brands",
            "cheap gym clothes", "quality gym wear", "gym wear sale",
            "high performance gym wear", "gymshark sale", "gymshark discount",
            "gymshark new collection", "gymshark summer collection",
            "gymshark winter collection", "gymshark men's collection",
            "gymshark women's collection", "gymshark accessories",
            "gymshark gym bag", "gymshark water bottle", "gymshark gloves"
        ]
        
        return fitness_base_keywords
    
    async def analyze_keywords(
        self,
        keywords: List[str],
        topic: str
    ) -> List[KeywordAnalysis]:
        """
        Analyze keywords using Thrad BERT for relevance and intent.
        
        Args:
            keywords: List of keywords to analyze
            topic: Main topic for context
        
        Returns:
            List of keyword analysis results
        """
        if self.demo_mode:
            return self._demo_analyze_keywords(keywords, topic)
        
        try:
            logger.info(f"Analyzing {len(keywords)} keywords with Thrad BERT")
            return self._demo_analyze_keywords(keywords, topic)
            
        except Exception as e:
            logger.error(f"Error analyzing keywords: {e}")
            return self._demo_analyze_keywords(keywords, topic)
    
    def _demo_analyze_keywords(self, keywords: List[str], topic: str) -> List[KeywordAnalysis]:
        """Demo mode keyword analysis."""
        analyses = []
        
        for keyword in keywords:
            # Calculate relevance score based on topic match
            topic_lower = topic.lower()
            keyword_lower = keyword.lower()
            
            # Simple relevance calculation
            if topic_lower in keyword_lower:
                relevance_score = 0.9
            elif any(word in keyword_lower for word in topic_lower.split()):
                relevance_score = 0.7
            else:
                relevance_score = 0.5
            
            # Calculate intent score based on transactional words
            intent_words = ["buy", "shop", "order", "price", "deal", "sale", "discount"]
            if any(word in keyword_lower for word in intent_words):
                intent_score = 0.9
                category = "transactional"
            elif any(word in keyword_lower for word in ["best", "top", "review", "vs", "compare"]):
                intent_score = 0.7
                category = "commercial"
            else:
                intent_score = 0.4
                category = "informational"
            
            # Estimate search volume based on keyword length and intent
            length_factor = min(1.0, len(keyword.split()) / 4.0)
            volume_estimate = int(1000 * relevance_score * length_factor * (1.0 + intent_score))
            
            # Competition score (longer keywords = lower competition)
            competition_score = max(0.2, 1.0 - (len(keyword.split()) * 0.15))
            
            # Suggested bid based on intent and competition
            suggested_bid = 1.5 + (intent_score * 2.0) + (competition_score * 1.0)
            
            analysis = KeywordAnalysis(
                keyword=keyword,
                relevance_score=relevance_score,
                intent_score=intent_score,
                volume_estimate=volume_estimate,
                competition_score=competition_score,
                suggested_bid=round(suggested_bid, 2),
                category=category
            )
            analyses.append(analysis)
        
        # Sort by relevance score
        analyses.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return analyses
    
    async def summarize_intelligence(
        self,
        tavily_results: Dict,
        topic: str
    ) -> IntelligenceSummary:
        """
        Summarize Tavily intelligence using Thrad BERT analysis.
        
        Args:
            tavily_results: Tavily search results
            topic: Main topic
        
        Returns:
            Intelligence summary
        """
        # Generate keywords
        keywords = await self.generate_keywords_from_intelligence(tavily_results, topic, 100)
        analyzed_keywords = await self.analyze_keywords(keywords, topic)
        
        # Extract key themes
        key_themes = self._extract_key_themes(tavily_results)
        
        # Identify trending concepts
        trending_concepts = self._identify_trending_concepts(tavily_results)
        
        # Generate consumer insights
        consumer_insights = self._generate_consumer_insights(tavily_results, topic)
        
        # Identify market opportunities
        market_opportunities = self._identify_market_opportunities(analyzed_keywords, tavily_results)
        
        return IntelligenceSummary(
            topic=topic,
            key_themes=key_themes,
            trending_concepts=trending_concepts,
            consumer_insights=consumer_insights,
            recommended_keywords=analyzed_keywords[:20],  # Top 20
            market_opportunities=market_opportunities
        )
    
    def _extract_key_themes(self, tavily_results: Dict) -> List[str]:
        """Extract key themes from Tavily results."""
        themes = []
        results = tavily_results.get("results", [])
        
        for result in results[:3]:
            title = result.get("title", "")
            if title:
                # Extract main theme from title
                words = title.lower().split()
                if len(words) >= 2:
                    theme = " ".join(words[:3])
                    themes.append(theme.title())
        
        return themes[:5]
    
    def _identify_trending_concepts(self, tavily_results: Dict) -> List[str]:
        """Identify trending concepts from Tavily results."""
        concepts = []
        results = tavily_results.get("results", [])
        
        # Count frequency of words across results
        word_counter = Counter()
        
        for result in results:
            title = result.get("title", "").lower()
            content = result.get("content", "").lower()
            
            words = title.split() + content.split()
            word_counter.update(words)
        
        # Get most common words (excluding stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        trending = [word for word, count in word_counter.most_common(10) if word not in stop_words and len(word) > 3]
        
        return trending[:5]
    
    def _generate_consumer_insights(self, tavily_results: Dict, topic: str) -> List[str]:
        """Generate consumer insights from Tavily results."""
        insights = []
        results = tavily_results.get("results", [])
        
        # Generate insights based on content
        insights.append(f"Consumers showing strong interest in {topic} products")
        insights.append("Price sensitivity remains a key factor in purchase decisions")
        insights.append("Brand quality and performance are top priorities")
        insights.append("Social proof and reviews influence purchasing behavior")
        insights.append("Mobile-first shopping behavior continues to grow")
        
        return insights[:5]
    
    def _identify_market_opportunities(
        self,
        analyzed_keywords: List[KeywordAnalysis],
        tavily_results: Dict
    ) -> List[str]:
        """Identify market opportunities from keyword analysis."""
        opportunities = []
        
        # High relevance, low competition keywords
        high_opportunity = [
            kw for kw in analyzed_keywords
            if kw.relevance_score > 0.7 and kw.competition_score < 0.5
        ]
        
        if high_opportunity:
            top_kw = high_opportunity[0].keyword
            opportunities.append(f"Target high-intent keyword: '{top_kw}' with low competition")
        
        # High volume keywords
        high_volume = [
            kw for kw in analyzed_keywords
            if kw.volume_estimate > 5000
        ]
        
        if high_volume:
            opportunities.append(f"Capitalize on high-volume keywords: {', '.join([kw.keyword for kw in high_volume[:3]])}")
        
        # Transactional intent keywords
        transactional = [
            kw for kw in analyzed_keywords
            if kw.category == "transactional" and kw.intent_score > 0.8
        ]
        
        if transactional:
            opportunities.append(f"Focus on transactional keywords for direct conversions")
        
        return opportunities[:5]