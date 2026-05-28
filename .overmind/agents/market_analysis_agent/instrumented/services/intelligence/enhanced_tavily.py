"""
Enhanced Tavily Integration for Real-Time Keyword Extraction and Trend Analysis

This module extends the base Tavily client with advanced capabilities:
- Real-time keyword extraction from search results
- Trend analysis and velocity tracking
- Competitor keyword monitoring
- Gap analysis updates
- SEO keyword recommendations
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter
import re
import logging

from .tavily_client import TavilyClient, TavilySearchResult

logger = logging.getLogger(__name__)


@dataclass
class ExtractedKeyword:
    """Keyword extracted from Tavily results."""
    keyword: str
    frequency: int
    source_urls: List[str]
    relevance_score: float
    category: Optional[str] = None


@dataclass
class TrendData:
    """Trend analysis data."""
    topic: str
    current_volume: int
    previous_volume: int
    growth_rate: float
    velocity: str  # increasing, stable, decreasing
    related_topics: List[str]
    sentiment: str  # positive, neutral, negative


@dataclass
class CompetitorKeyword:
    """Keyword used by competitor."""
    competitor: str
    keyword: str
    context: str
    url: str
    first_seen: datetime


class EnhancedTavilyClient:
    """
    Enhanced Tavily client with keyword extraction and trend analysis.
    
    Builds on the base TavilyClient to add advanced intelligence capabilities.
    """
    
    def __init__(self, tavily_client: TavilyClient):
        """
        Initialize enhanced Tavily client.
        
        Args:
            tavily_client: Base Tavily client instance
        """
        self.tavily_client = tavily_client
        
        # Common stop words to filter out
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare", "ought",
            "used", "to", "it", "this", "that", "these", "those", "i", "you", "he",
            "she", "we", "they", "what", "which", "who", "whom", "when", "where", "why",
            "how", "all", "each", "every", "both", "few", "more", "most", "other",
            "some", "such", "no", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "also", "now", "here", "there", "then", "once", "here"
        }
    
    async def extract_keywords_from_results(
        self,
        results: List[TavilySearchResult],
        max_keywords: int = 50,
        min_frequency: int = 2
    ) -> List[ExtractedKeyword]:
        """
        Extract keywords from Tavily search results.
        
        Args:
            results: List of Tavily search results
            max_keywords: Maximum number of keywords to return
            min_frequency: Minimum frequency for a keyword to be included
        
        Returns:
            List of extracted keywords with metadata
        """
        keyword_data = {}
        
        for result in results:
            # Extract keywords from title and content
            text = f"{result.title} {result.content}".lower()
            
            # Extract phrases (2-3 word combinations)
            phrases = self._extract_phrases(text)
            
            for phrase in phrases:
                if phrase in self.stop_words or len(phrase) < 3:
                    continue
                
                if phrase not in keyword_data:
                    keyword_data[phrase] = {
                        "frequency": 0,
                        "source_urls": [],
                        "relevance_score": 0.0
                    }
                
                keyword_data[phrase]["frequency"] += 1
                keyword_data[phrase]["source_urls"].append(result.url)
                keyword_data[phrase]["relevance_score"] += result.score
        
        # Filter by minimum frequency
        filtered_keywords = {
            k: v for k, v in keyword_data.items() 
            if v["frequency"] >= min_frequency
        }
        
        # Calculate final relevance scores
        for keyword_data in filtered_keywords.values():
            keyword_data["relevance_score"] = round(
                keyword_data["relevance_score"] / keyword_data["frequency"],
                3
            )
        
        # Sort by frequency and relevance
        sorted_keywords = sorted(
            filtered_keywords.items(),
            key=lambda x: (x[1]["frequency"], x[1]["relevance_score"]),
            reverse=True
        )
        
        # Convert to ExtractedKeyword objects
        extracted_keywords = []
        for keyword, data in sorted_keywords[:max_keywords]:
            extracted_keywords.append(ExtractedKeyword(
                keyword=keyword,
                frequency=data["frequency"],
                source_urls=data["source_urls"],
                relevance_score=data["relevance_score"],
                category=self._categorize_keyword(keyword)
            ))
        
        return extracted_keywords
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract phrases from text."""
        # Remove special characters and split into words
        words = re.findall(r'\b\w+\b', text)
        
        phrases = []
        
        # Single words
        phrases.extend(words)
        
        # Two-word phrases
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
        
        # Three-word phrases
        for i in range(len(words) - 2):
            phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return phrases
    
    def _categorize_keyword(self, keyword: str) -> Optional[str]:
        """Categorize keyword into topic categories."""
        keyword_lower = keyword.lower()
        
        categories = {
            "sustainability": ["sustainable", "eco", "green", "environmental", "recycled", "organic"],
            "fashion": ["fashion", "style", "clothing", "apparel", "wear", "outfit", "trend"],
            "technology": ["tech", "digital", "software", "app", "online", "smart", "ai"],
            "lifestyle": ["lifestyle", "living", "wellness", "health", "fitness", "home"],
            "business": ["business", "company", "brand", "market", "industry", "commercial"]
        }
        
        for category, terms in categories.items():
            if any(term in keyword_lower for term in terms):
                return category
        
        return None
    
    async def analyze_trends(
        self,
        topic: str,
        days: int = 30,
        compare_days: int = 30
    ) -> List[TrendData]:
        """
        Analyze trends for a topic over time.
        
        Args:
            topic: Topic to analyze
            days: Number of recent days to analyze
            compare_days: Number of days to compare against
        
        Returns:
            List of trend data for related topics
        """
        # Get current period data
        current_results = await self.tavily_client.search_and_answer(
            query=f"{topic} trends recent",
            max_results=20,
            days=days,
            search_depth="advanced"
        )
        
        # Get comparison period data
        comparison_results = await self.tavily_client.search_and_answer(
            query=f"{topic} trends",
            max_results=20,
            days=compare_days,
            search_depth="advanced"
        )
        
        # Extract keywords from both periods
        current_keywords = await self.extract_keywords_from_results(current_results.results)
        comparison_keywords = await self.extract_keywords_from_results(comparison_results.results)
        
        # Create keyword frequency maps
        current_freq = {k.keyword: k.frequency for k in current_keywords}
        comparison_freq = {k.keyword: k.frequency for k in comparison_keywords}
        
        # Analyze trends
        all_keywords = set(current_freq.keys()) | set(comparison_freq.keys())
        trend_data = []
        
        for keyword in all_keywords:
            current_vol = current_freq.get(keyword, 0)
            previous_vol = comparison_freq.get(keyword, 0)
            
            if previous_vol == 0:
                growth_rate = float('inf') if current_vol > 0 else 0.0
            else:
                growth_rate = ((current_vol - previous_vol) / previous_vol) * 100
            
            # Determine velocity
            if growth_rate > 10:
                velocity = "increasing"
            elif growth_rate < -10:
                velocity = "decreasing"
            else:
                velocity = "stable"
            
            # Find related topics
            related = self._find_related_topics(keyword, current_keywords)
            
            trend_data.append(TrendData(
                topic=keyword,
                current_volume=current_vol,
                previous_volume=previous_vol,
                growth_rate=round(growth_rate, 2) if growth_rate != float('inf') else 999.0,
                velocity=velocity,
                related_topics=related[:5],
                sentiment="neutral"  # Would need sentiment analysis
            ))
        
        # Sort by growth rate
        trend_data.sort(key=lambda x: x.growth_rate, reverse=True)
        
        return trend_data[:20]  # Return top 20 trends
    
    def _find_related_topics(
        self,
        keyword: str,
        all_keywords: List[ExtractedKeyword]
    ) -> List[str]:
        """Find topics related to the given keyword."""
        keyword_words = set(keyword.lower().split())
        related = []
        
        for kw in all_keywords:
            if kw.keyword.lower() == keyword.lower():
                continue
            
            kw_words = set(kw.keyword.lower().split())
            
            # Find keywords with word overlap
            overlap = keyword_words & kw_words
            if overlap:
                related.append(kw.keyword)
        
        return related
    
    async def monitor_competitor_keywords(
        self,
        competitors: List[str],
        industry: str,
        days: int = 7
    ) -> List[CompetitorKeyword]:
        """
        Monitor keywords used by competitors.
        
        Args:
            competitors: List of competitor names
            industry: Industry context
            days: Number of days to monitor
        
        Returns:
            List of competitor keywords
        """
        competitor_keywords = []
        
        for competitor in competitors:
            try:
                results = await self.tavily_client.search_and_answer(
                    query=f"{competitor} {industry} keywords marketing",
                    max_results=10,
                    days=days,
                    search_depth="advanced"
                )
                
                extracted_keywords = await self.extract_keywords_from_results(results.results)
                
                for kw in extracted_keywords[:10]:  # Top 10 keywords per competitor
                    competitor_keywords.append(CompetitorKeyword(
                        competitor=competitor,
                        keyword=kw.keyword,
                        context=kw.keyword,
                        url=kw.source_urls[0] if kw.source_urls else "",
                        first_seen=datetime.now()
                    ))
            
            except Exception as e:
                logger.error(f"Error monitoring competitor {competitor}: {e}")
        
        return competitor_keywords
    
    async def generate_seo_keywords(
        self,
        topic: str,
        location: Optional[str] = None,
        language: str = "en"
    ) -> Tuple[List[str], List[str]]:
        """
        Generate SEO keywords based on Tavily intelligence.
        
        Args:
            topic: Topic to generate keywords for
            location: Geographic location
            language: Language code
        
        Returns:
            Tuple of (positive keywords, negative keywords)
        """
        # Search for topic-related content
        query = f"{topic} SEO keywords search volume"
        if location:
            query += f" {location}"
        
        results = await self.tavily_client.search_and_answer(
            query=query,
            max_results=15,
            days=30,
            search_depth="advanced"
        )
        
        # Extract keywords
        extracted_keywords = await self.extract_keywords_from_results(results.results)
        
        # Generate positive keywords (high relevance, good frequency)
        positive_keywords = [
            kw.keyword for kw in extracted_keywords
            if kw.relevance_score > 0.5 and kw.frequency >= 2
        ]
        
        # Generate negative keywords (low relevance or irrelevant context)
        negative_keywords = [
            "free", "cheap", "wholesale", "used", "second hand",
            "repair", "diy", "how to", "vs", "review", "best",
            "top", "comparison"
        ]
        
        # Add topic-specific negative keywords
        topic_lower = topic.lower()
        if "fashion" in topic_lower or "clothing" in topic_lower:
            negative_keywords.extend(["costume", "kids", "children", "plus size"])
        elif "software" in topic_lower or "app" in topic_lower:
            negative_keywords.extend(["crack", "hack", "free download", "pirate"])
        
        return positive_keywords[:30], list(set(negative_keywords))
    
    async def update_gap_analysis(
        self,
        brand_keywords: List[str],
        market_keywords: List[str],
        competitor_keywords: List[str]
    ) -> Dict[str, List[str]]:
        """
        Update gap analysis with real-time keyword data.
        
        Args:
            brand_keywords: Keywords brand currently targets
            market_keywords: Keywords with high market demand
            competitor_keywords: Keywords competitors target
        
        Returns:
            Dictionary with gap categories:
            - gap: Market demand but no brand/competitor presence
            - contested: High competitor presence
            - owned: Brand has strong presence
            - opportunity: Market demand, low competition
        """
        brand_set = set(kw.lower() for kw in brand_keywords)
        market_set = set(kw.lower() for kw in market_keywords)
        competitor_set = set(kw.lower() for kw in competitor_keywords)
        
        gap_analysis = {
            "gap": [],
            "contested": [],
            "owned": [],
            "opportunity": []
        }
        
        for keyword in market_set:
            if keyword in brand_set and keyword in competitor_set:
                gap_analysis["contested"].append(keyword)
            elif keyword in brand_set:
                gap_analysis["owned"].append(keyword)
            elif keyword in competitor_set:
                gap_analysis["gap"].append(keyword)
            else:
                gap_analysis["opportunity"].append(keyword)
        
        return gap_analysis
    
    async def real_time_crawl(
        self,
        query: str,
        platforms: Optional[List[str]] = None,
        max_results: int = 100,
        callback: Optional[callable] = None
    ) -> List[TavilySearchResult]:
        """
        Perform real-time crawling with optional callback for streaming results.
        
        Args:
            query: Search query
            platforms: Social media platforms to focus on
            max_results: Maximum results to return
            callback: Optional callback function for streaming results
        
        Returns:
            List of search results
        """
        if platforms is None:
            platforms = ["reddit", "twitter", "linkedin", "instagram"]
        
        results = await self.tavily_client.social_media_search(
            query=query,
            platforms=platforms,
            max_results=max_results,
            days=1  # Last 24 hours for real-time
        )
        
        # Call callback if provided
        if callback:
            for result in results:
                callback(result)
        
        return results