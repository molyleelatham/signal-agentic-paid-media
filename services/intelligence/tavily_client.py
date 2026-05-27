"""
Tavily client for market intelligence ingestion.
"""
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from shared.utils.settings import settings


class TavilySearchResult(BaseModel):
    """Model for Tavily search results."""
    
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None


class TavilySearchResponse(BaseModel):
    """Model for Tavily search API response."""
    
    answer: str
    query: str
    results: List[TavilySearchResult]
    
    class Config:
        arbitrary_types_allowed = True


class TavilyClient:
    """Client for Tavily API interactions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily client.
        
        Args:
            api_key: Tavily API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.tavily_api_key
        if not self.api_key:
            raise ValueError("Tavily API key is required")
        
        self.base_url = "https://api.tavily.com"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def search_and_answer(
        self,
        query: str,
        max_results: int = 10,
        topic: str = "general",
        days: int = 7,
        max_subqueries: int = 4,
        search_depth: str = "advanced"
    ) -> TavilySearchResponse:
        """
        Perform search and get AI-generated answer.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            topic: Topic category (general, news, finance)
            days: Number of days to search back
            max_subqueries: Maximum number of sub-queries
            search_depth: Search depth (basic, advanced)
        
        Returns:
            TavilySearchResponse with answer and results
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "topic": topic,
            "days": days,
            "max_subqueries": max_subqueries,
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": True
        }
        
        response = await self.client.post(
            f"{self.base_url}/search",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        
        return TavilySearchResponse(
            answer=data.get("answer", ""),
            query=data.get("query", query),
            results=[
                TavilySearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    content=result.get("content", ""),
                    score=result.get("score", 0.0),
                    published_date=result.get("published_date")
                )
                for result in data.get("results", [])
            ]
        )
    
    async def search_dedup(
        self,
        queries: List[str],
        max_results: int = 10,
        search_depth: str = "advanced",
        days: int = 7
    ) -> List[TavilySearchResult]:
        """
        Perform multiple queries and deduplicate results.
        
        Args:
            queries: List of search queries
            max_results: Maximum results per query
            search_depth: Search depth
            days: Number of days to search back
        
        Returns:
            Deduplicated list of search results
        """
        all_results = []
        seen_urls = set()
        
        for query in queries:
            response = await self.search_and_answer(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                days=days
            )
            
            for result in response.results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)
        
        return all_results
    
    async def social_media_search(
        self,
        query: str,
        platforms: List[str] = None,
        max_results: int = 50,
        days: int = 7
    ) -> List[TavilySearchResult]:
        """
        Search social media platforms.
        
        Args:
            query: Search query
            platforms: List of platforms (reddit, twitter, linkedin, etc.)
            max_results: Maximum results
            days: Number of days to search back
        
        Returns:
            List of social media search results
        """
        if platforms is None:
            platforms = ["reddit", "twitter", "linkedin"]
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "days": days,
            "include_domains": [f"{p}.com" for p in platforms],
            "include_raw_content": True
        }
        
        response = await self.client.post(
            f"{self.base_url}/search",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        
        return [
            TavilySearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                score=result.get("score", 0.0),
                published_date=result.get("published_date")
            )
            for result in data.get("results", [])
        ]
    
    async def crawl_and_summarize(
        self,
        urls: List[str],
        max_depth: int = 2,
        max_pages: int = 50
    ) -> Dict[str, str]:
        """
        Crawl URLs and generate summaries.
        
        Args:
            urls: List of URLs to crawl
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to crawl
        
        Returns:
            Dictionary mapping URLs to summaries
        """
        # Note: Tavily doesn't have a dedicated crawl endpoint
        # This is a placeholder for the crawl functionality
        # In production, you might use a dedicated crawler or Tavily's extract endpoint
        
        summaries = {}
        
        for url in urls:
            try:
                payload = {
                    "api_key": self.api_key,
                    "urls": [url],
                    "extract_depth": max_depth
                }
                
                response = await self.client.post(
                    f"{self.base_url}/extract",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("results"):
                    summaries[url] = data["results"][0].get("content", "")
            
            except Exception as e:
                print(f"Error crawling {url}: {e}")
                summaries[url] = ""
        
        return summaries


class MarketScanner:
    """
    Always-on market scanner using Tavily.
    
    This implements Module 1.1 from the technical spec.
    """
    
    def __init__(self, tavily_client: TavilyClient):
        self.tavily_client = tavily_client
    
    async def scan_market(
        self,
        category: str,
        competitors: List[str] = None,
        scan_depth: str = "advanced"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive market scan.
        
        Args:
            category: Market category to scan
            competitors: List of competitor names
            scan_depth: Search depth
        
        Returns:
            Dictionary with scan results including:
            - market_intelligence: General market trends
            - social_sentiment: Social media conversations
            - competitor_activity: Competitor content and campaigns
        """
        if competitors is None:
            competitors = []
        
        # Run searches in parallel
        import asyncio
        
        # Market intelligence
        market_task = self.tavily_client.search_and_answer(
            query=f"what are people asking about {category} right now",
            max_results=10,
            topic="general",
            days=7,
            max_subqueries=4,
            search_depth=scan_depth
        )
        
        # Social media search
        social_task = self.tavily_client.social_media_search(
            query=f"{category} trends opinions",
            max_results=50,
            days=7
        )
        
        # Competitor searches
        competitor_tasks = []
        for competitor in competitors:
            task = self.tavily_client.search_and_answer(
                query=f"{competitor} recent campaigns {category}",
                max_results=5,
                topic="general",
                days=7,
                search_depth=scan_depth
            )
            competitor_tasks.append(task)
        
        # Execute all tasks
        market_intelligence, social_sentiment = await asyncio.gather(
            market_task,
            social_task
        )
        
        competitor_results = []
        if competitor_tasks:
            competitor_results = await asyncio.gather(*competitor_tasks)
        
        # Competitor activity
        competitor_activity = []
        for i, result in enumerate(competitor_results):
            competitor_activity.append({
                "competitor": competitors[i],
                "results": [r.dict() for r in result.results]
            })
        
        return {
            "category": category,
            "market_intelligence": {
                "answer": market_intelligence.answer,
                "results": [r.dict() for r in market_intelligence.results]
            },
            "social_sentiment": [r.dict() for r in social_sentiment],
            "competitor_activity": competitor_activity,
            "scan_timestamp": market_intelligence.results[0].published_date if market_intelligence.results else None
        }
    
    async def generate_intelligence_digest(
        self,
        scan_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate weekly intelligence digest for marketers.
        
        This implements the "What the marketer sees" section from Module 1.1.
        
        Args:
            scan_results: Results from market scan
        
        Returns:
            Structured intelligence digest with three sections:
            1. What your audience is talking about
            2. What competitors published
            3. Where you were mentioned
        """
        # Extract top conversation themes from social sentiment
        social_posts = scan_results.get("social_sentiment", [])
        audience_conversations = self._extract_conversation_themes(social_posts)
        
        # Extract competitor content
        competitor_activity = scan_results.get("competitor_activity", [])
        competitor_content = self._extract_competitor_content(competitor_activity)
        
        # Brand mentions (would need LLM citation data - placeholder)
        brand_mentions = self._extract_brand_mentions(scan_results)
        
        return {
            "audience_conversations": audience_conversations,
            "competitor_content": competitor_content,
            "brand_mentions": brand_mentions,
            "generated_at": scan_results.get("scan_timestamp")
        }
    
    def _extract_conversation_themes(self, social_posts: List[Dict]) -> List[Dict]:
        """Extract top 5 conversation themes from social posts."""
        # In production, this would use topic modeling or LLM summarization
        # For now, return top posts as themes
        return [
            {
                "theme": post.get("title", "Unknown theme"),
                "example_post": post.get("content", ""),
                "engagement_score": post.get("score", 0.0)
            }
            for post in sorted(social_posts, key=lambda x: x.get("score", 0), reverse=True)[:5]
        ]
    
    def _extract_competitor_content(self, competitor_activity: List[Dict]) -> List[Dict]:
        """Extract topics and angles from competitor activity."""
        content = []
        for activity in competitor_activity:
            competitor = activity.get("competitor", "Unknown")
            for result in activity.get("results", []):
                content.append({
                    "competitor": competitor,
                    "topic": result.get("title", ""),
                    "angle": result.get("content", "")[:200],  # First 200 chars
                    "url": result.get("url", "")
                })
        return content
    
    def _extract_brand_mentions(self, scan_results: Dict) -> List[Dict]:
        """Extract brand mentions from scan results."""
        # Placeholder - would integrate with LLM citation tracking
        return []