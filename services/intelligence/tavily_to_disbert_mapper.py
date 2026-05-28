"""
Tavily to DisBERT Field Mapper

Automatically maps Tavily research fields to DisBERT model segments (A-M).
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from services.intelligence.disbert_thrad_classification import DisBERTThradClassification, DisBERTThradAdIntegrator


@dataclass
class DisBERTSegment:
    """A DisBERT model segment with mapped Tavily fields."""
    classification: DisBERTThradClassification
    classification_name: str
    tavily_fields: List[str]
    mapped_data: Dict
    commercial_intent: float
    ingestion_priority: int
    should_use_as_keywords: bool


class TavilyToDisBERTMapper:
    """
    Automatically maps Tavily research fields to DisBERT segments.
    
    Mapping Logic:
    - A (academic_help): educational content, learning resources
    - B (personal_writing): personal stories, user experiences
    - C (writing_and_editing): content creation, copywriting
    - D (creative_writing): creative content, storytelling
    - E (general_guidance): how-to guides, tutorials
    - F (programming): technical content, code
    - G (creative_ideation): brainstorming, ideas
    - H (purchasable_products): product queries, buy intent
    - I (greetings): conversational, greetings
    - J (relationships): personal reflection, emotions
    - K (media_generation): visual content, media
    - L (other): general content
    - M (obscene): blocked content
    """
    
    def __init__(self):
        self.disbert_integrator = DisBERTThradAdIntegrator()
    
    def map_tavily_research_to_disbert(self, tavily_result: Dict) -> List[DisBERTSegment]:
        """
        Map Tavily research results to DisBERT segments.
        
        Args:
            tavily_result: Dictionary containing Tavily research results
                - reddit_posts: List of Reddit posts
                - seo_keywords: List of SEO keywords
                - google_keywords: List of Google keywords
                - thrad_inputs: List of Thrad inputs
                - content_ideas: List of content ideas
        
        Returns:
            List of DisBERT segments with mapped Tavily fields
        """
        segments = []
        
        # Map Reddit posts to segments
        if 'reddit_posts' in tavily_result:
            reddit_segments = self._map_reddit_posts(tavily_result['reddit_posts'])
            segments.extend(reddit_segments)
        
        # Map SEO keywords to segments
        if 'seo_keywords' in tavily_result:
            seo_segments = self._map_seo_keywords(tavily_result['seo_keywords'])
            segments.extend(seo_segments)
        
        # Map Google keywords to segments
        if 'google_keywords' in tavily_result:
            google_segments = self._map_google_keywords(tavily_result['google_keywords'])
            segments.extend(google_segments)
        
        # Map Thrad inputs to segments
        if 'thrad_inputs' in tavily_result:
            thrad_segments = self._map_thrad_inputs(tavily_result['thrad_inputs'])
            segments.extend(thrad_segments)
        
        # Map content ideas to segments
        if 'content_ideas' in tavily_result:
            content_segments = self._map_content_ideas(tavily_result['content_ideas'])
            segments.extend(content_segments)
        
        return segments
    
    def _map_reddit_posts(self, posts: List[Dict]) -> List[DisBERTSegment]:
        """Map Reddit posts to DisBERT segments."""
        segments = []
        
        if not posts:
            return segments
        
        for post in posts:
            try:
                # Classify based on content and sentiment
                content = str(post.get('content', '')).lower()
                title = str(post.get('title', '')).lower()
                sentiment = str(post.get('sentiment', '')).lower()
                keywords = post.get('keywords', []) or []
                
                combined_text = f"{title} {content} {' '.join(str(k) for k in keywords)}"
                
                # Determine classification
                if any(kw in combined_text for kw in ['buy', 'purchase', 'order', 'shop', 'deal', 'discount']):
                    classification = DisBERTThradClassification.PURCHASABLE_PRODUCTS
                elif any(kw in combined_text for kw in ['how to', 'guide', 'tutorial', 'learn', 'tips']):
                    classification = DisBERTThradClassification.GENERAL_GUIDANCE_INFO
                elif any(kw in combined_text for kw in ['story', 'experience', 'journey', 'my']):
                    classification = DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION
                elif any(kw in combined_text for kw in ['help', 'assist', 'support']):
                    classification = DisBERTThradClassification.ACADEMIC_HELP
                elif any(kw in combined_text for kw in ['create', 'write', 'content', 'blog']):
                    classification = DisBERTThradClassification.WRITING_AND_EDITING
                elif any(kw in combined_text for kw in ['idea', 'brainstorm', 'concept']):
                    classification = DisBERTThradClassification.CREATIVE_IDEATION
                elif any(kw in combined_text for kw in ['video', 'image', 'photo', 'design']):
                    classification = DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS
                elif any(kw in combined_text for kw in ['hi', 'hello', 'hey', 'what\'s up']):
                    classification = DisBERTThradClassification.GREETINGS_CHITCHAT
                else:
                    classification = DisBERTThradClassification.OTHER
                
                # Get strategy from DisBERT integrator
                try:
                    strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(classification)
                except:
                    strategy = type('obj', (object,), {
                        'commercial_intent': 0.5,
                        'use_as_keywords': False
                    })()
                
                segment = DisBERTSegment(
                    classification=classification,
                    classification_name=classification.value,
                    tavily_fields=['reddit_posts'],
                    mapped_data={
                        'post_title': post.get('title', ''),
                        'post_content': post.get('content', ''),
                        'subreddit': post.get('subreddit', ''),
                        'score': post.get('score', 0),
                        'sentiment': sentiment,
                        'keywords': keywords
                    },
                    commercial_intent=getattr(strategy, 'commercial_intent', 0.5),
                    ingestion_priority=self._get_ingestion_priority(classification),
                    should_use_as_keywords=getattr(strategy, 'use_as_keywords', False)
                )
                segments.append(segment)
            except Exception as e:
                print(f"Error mapping reddit post: {e}")
                continue
        
        return segments
    
    def _map_seo_keywords(self, keywords: List[Dict]) -> List[DisBERTSegment]:
        """Map SEO keywords to DisBERT segments."""
        segments = []
        
        if not keywords:
            return segments
        
        for kw in keywords:
            try:
                keyword = str(kw.get('keyword', '')).lower()
                intent = str(kw.get('intent', '')).lower()
                
                # Determine classification based on intent
                if intent == 'transactional':
                    classification = DisBERTThradClassification.PURCHASABLE_PRODUCTS
                elif intent == 'informational':
                    classification = DisBERTThradClassification.GENERAL_GUIDANCE_INFO
                elif intent == 'navigational':
                    classification = DisBERTThradClassification.OTHER
                else:
                    classification = DisBERTThradClassification.OTHER
                
                # Get strategy
                try:
                    strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(classification)
                except:
                    strategy = type('obj', (object,), {
                        'commercial_intent': 0.5,
                        'use_as_keywords': False
                    })()
                
                segment = DisBERTSegment(
                    classification=classification,
                    classification_name=classification.value,
                    tavily_fields=['seo_keywords'],
                    mapped_data={
                        'keyword': keyword,
                        'search_volume': kw.get('search_volume'),
                        'difficulty': kw.get('difficulty'),
                        'intent': intent,
                        'source': kw.get('source'),
                        'confidence': kw.get('confidence')
                    },
                    commercial_intent=getattr(strategy, 'commercial_intent', 0.5),
                    ingestion_priority=self._get_ingestion_priority(classification),
                    should_use_as_keywords=getattr(strategy, 'use_as_keywords', False)
                )
                segments.append(segment)
            except Exception as e:
                print(f"Error mapping seo keyword: {e}")
                continue
        
        return segments
    
    def _map_google_keywords(self, keywords: List[Dict]) -> List[DisBERTSegment]:
        """Map Google keywords to DisBERT segments."""
        segments = []
        
        if not keywords:
            return segments
        
        for kw in keywords:
            try:
                keyword = str(kw.get('keyword', '')).lower()
                search_intent = str(kw.get('search_intent', '')).lower()
                
                # Determine classification
                if search_intent == 'transactional' or any(kw in keyword for kw in ['buy', 'purchase', 'shop']):
                    classification = DisBERTThradClassification.PURCHASABLE_PRODUCTS
                elif search_intent == 'informational':
                    classification = DisBERTThradClassification.GENERAL_GUIDANCE_INFO
                else:
                    classification = DisBERTThradClassification.OTHER
                
                # Get strategy
                try:
                    strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(classification)
                except:
                    strategy = type('obj', (object,), {
                        'commercial_intent': 0.5,
                        'use_as_keywords': False
                    })()
                
                segment = DisBERTSegment(
                    classification=classification,
                    classification_name=classification.value,
                    tavily_fields=['google_keywords'],
                    mapped_data={
                        'keyword': keyword,
                        'match_type': kw.get('match_type'),
                        'bid_suggestion': kw.get('bid_suggestion'),
                        'competition': kw.get('competition'),
                        'relevance': kw.get('relevance_to_gymshark'),
                        'search_intent': search_intent
                    },
                    commercial_intent=getattr(strategy, 'commercial_intent', 0.5),
                    ingestion_priority=self._get_ingestion_priority(classification),
                    should_use_as_keywords=getattr(strategy, 'use_as_keywords', False)
                )
                segments.append(segment)
            except Exception as e:
                print(f"Error mapping google keyword: {e}")
                continue
        
        return segments
    
    def _map_thrad_inputs(self, thrad_inputs: List[Dict]) -> List[DisBERTSegment]:
        """Map Thrad inputs to DisBERT segments."""
        segments = []
        
        if not thrad_inputs:
            return segments
        
        for thrad_input in thrad_inputs:
            try:
                query = str(thrad_input.get('query', '')).lower()
                category = str(thrad_input.get('category', '')).upper()
                
                # Map category to DisBERT classification
                category_map = {
                    'H': DisBERTThradClassification.PURCHASABLE_PRODUCTS,
                    'G': DisBERTThradClassification.CREATIVE_IDEATION,
                    'A': DisBERTThradClassification.ACADEMIC_HELP,
                    'E': DisBERTThradClassification.GENERAL_GUIDANCE_INFO,
                    'J': DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION,
                    'K': DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS,
                }
                
                classification = category_map.get(category, DisBERTThradClassification.OTHER)
                
                # Get strategy
                try:
                    strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(classification)
                except:
                    strategy = type('obj', (object,), {
                        'commercial_intent': 0.5,
                        'use_as_keywords': False
                    })()
                
                segment = DisBERTSegment(
                    classification=classification,
                    classification_name=classification.value,
                    tavily_fields=['thrad_inputs'],
                    mapped_data={
                        'query': query,
                        'category': category,
                        'confidence': thrad_input.get('confidence'),
                        'source': thrad_input.get('source'),
                        'context': thrad_input.get('context')
                    },
                    commercial_intent=getattr(strategy, 'commercial_intent', 0.5),
                    ingestion_priority=self._get_ingestion_priority(classification),
                    should_use_as_keywords=getattr(strategy, 'use_as_keywords', False)
                )
                segments.append(segment)
            except Exception as e:
                print(f"Error mapping thrad input: {e}")
                continue
        
        return segments
    
    def _map_content_ideas(self, content_ideas: List[Dict]) -> List[DisBERTSegment]:
        """Map content ideas to DisBERT segments."""
        segments = []
        
        if not content_ideas:
            return segments
        
        for idea in content_ideas:
            try:
                topic = str(idea.get('topic', '')).lower()
                content_type = str(idea.get('content_type', '')).lower()
                keywords = idea.get('keywords', []) or []
                
                combined_text = f"{topic} {' '.join(str(k) for k in keywords)}"
                
                # Determine classification based on content type
                if content_type in ['video', 'image']:
                    classification = DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS
                elif any(kw in combined_text for kw in ['idea', 'brainstorm', 'concept']):
                    classification = DisBERTThradClassification.CREATIVE_IDEATION
                elif any(kw in combined_text for kw in ['guide', 'how to', 'tutorial']):
                    classification = DisBERTThradClassification.GENERAL_GUIDANCE_INFO
                elif any(kw in combined_text for kw in ['story', 'narrative']):
                    classification = DisBERTThradClassification.CREATIVE_WRITING_ROLE_PLAY
                else:
                    classification = DisBERTThradClassification.WRITING_AND_EDITING
                
                # Get strategy
                try:
                    strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(classification)
                except:
                    strategy = type('obj', (object,), {
                        'commercial_intent': 0.5,
                        'use_as_keywords': False
                    })()
                
                segment = DisBERTSegment(
                    classification=classification,
                    classification_name=classification.value,
                    tavily_fields=['content_ideas'],
                    mapped_data={
                        'topic': topic,
                        'angle': idea.get('angle'),
                        'target_audience': idea.get('target_audience'),
                        'platform': idea.get('platform'),
                        'content_type': content_type,
                        'keywords': keywords,
                        'reasoning': idea.get('reasoning'),
                        'opportunity_score': idea.get('opportunity_score')
                    },
                    commercial_intent=getattr(strategy, 'commercial_intent', 0.5),
                    ingestion_priority=self._get_ingestion_priority(classification),
                    should_use_as_keywords=getattr(strategy, 'use_as_keywords', False)
                )
                segments.append(segment)
            except Exception as e:
                print(f"Error mapping content idea: {e}")
                continue
        
        return segments
    
    def _get_ingestion_priority(self, classification: DisBERTThradClassification) -> int:
        """Get ingestion priority for a classification."""
        priority_map = {
            DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION: 10,  # J - HIGHEST
            DisBERTThradClassification.GENERAL_GUIDANCE_INFO: 8,  # E - HIGH
            DisBERTThradClassification.PURCHASABLE_PRODUCTS: 9,  # H - HIGH VALUE
            DisBERTThradClassification.CREATIVE_IDEATION: 7,
            DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS: 6,
            DisBERTThradClassification.WRITING_AND_EDITING: 5,
            DisBERTThradClassification.CREATIVE_WRITING_ROLE_PLAY: 4,
            DisBERTThradClassification.ACADEMIC_HELP: 3,
            DisBERTThradClassification.PROGRAMMING_DATA_ANALYSIS: 2,
            DisBERTThradClassification.GREETINGS_CHITCHAT: 1,
            DisBERTThradClassification.OTHER: 1,
            DisBERTThradClassification.OTHER_OBSCENE_ILLEGAL: 0,  # BLOCK
        }
        
        return priority_map.get(classification, 1)
    
    def get_segments_by_classification(self, tavily_result: Dict, classification: DisBERTThradClassification) -> List[DisBERTSegment]:
        """
        Get all segments for a specific DisBERT classification.
        
        Args:
            tavily_result: Tavily research results
            classification: DisBERT classification to filter by
        
        Returns:
            List of segments matching the classification
        """
        all_segments = self.map_tavily_research_to_disbert(tavily_result)
        return [seg for seg in all_segments if seg.classification == classification]
    
    def get_high_value_segments(self, tavily_result: Dict) -> List[DisBERTSegment]:
        """
        Get high-value segments (H, J, E classifications).
        
        Args:
            tavily_result: Tavily research results
        
        Returns:
            List of high-value segments
        """
        all_segments = self.map_tavily_research_to_disbert(tavily_result)
        high_value_classifications = [
            DisBERTThradClassification.PURCHASABLE_PRODUCTS,  # H
            DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION,  # J
            DisBERTThradClassification.GENERAL_GUIDANCE_INFO,  # E
        ]
        
        return [seg for seg in all_segments if seg.classification in high_value_classifications]


# Global mapper instance
tavily_to_disbert_mapper = TavilyToDisBERTMapper()