"""
Tavily Research Service for Gymshark

Performs comprehensive web research using Tavily for:
- Reddit scraping for Gymshark-related discussions
- SEO page scraping for keyword research
- Google keyword extraction for bidding
- Thrad BERT input generation
- Content idea generation from research
"""

from typing import List, Dict, Optional, Literal
from datetime import datetime
from dataclasses import dataclass, asdict
import re
import json

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("Warning: Tavily not installed. Install with: pip install tavily-python")


@dataclass
class RedditPost:
    """Reddit post data."""
    subreddit: str
    title: str
    author: str
    score: int
    comments_count: int
    url: str
    content: str
    keywords: List[str]
    sentiment: str
    relevance_score: float


@dataclass
class SEOKeyword:
    """SEO keyword extracted from research."""
    keyword: str
    search_volume: Optional[int]
    difficulty: Optional[float]
    intent: str  # informational, transactional, navigational
    source: str  # reddit, seo_page, google_trends
    confidence: float


@dataclass
class GoogleKeyword:
    """Google keyword for bidding."""
    keyword: str
    match_type: str  # broad, phrase, exact
    bid_suggestion: float  # suggested bid amount
    competition: str  # low, medium, high
    relevance_to_gymshark: float
    search_intent: str


@dataclass
class ThradInput:
    """Input for Thrad BERT classification."""
    query: str
    category: str  # H, G, A (High intent, Growth, Awareness)
    confidence: float
    source: str
    context: str


@dataclass
class ContentIdea:
    """Content idea generated from research."""
    topic: str
    angle: str
    target_audience: str
    platform: str
    content_type: str  # video, image, carousel, text
    keywords: List[str]
    reasoning: str
    opportunity_score: float


@dataclass
class ResearchResult:
    """Complete research result."""
    query: str
    timestamp: str
    reddit_posts: List[RedditPost]
    seo_keywords: List[SEOKeyword]
    google_keywords: List[GoogleKeyword]
    thrad_inputs: List[ThradInput]
    content_ideas: List[ContentIdea]
    summary: str


class GymsharkTavilyResearch:
    """
    Tavily-based research service for Gymshark.
    
    Performs comprehensive web research across multiple sources:
    - Reddit for community discussions
    - SEO pages for keyword research
    - Google Trends for trending keywords
    - Generates inputs for Thrad BERT classification
    - Generates content ideas from research findings
    """
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        """
        Initialize Tavily research service.
        
        Args:
            tavily_api_key: Tavily API key (falls back to env var)
        """
        self.api_key = tavily_api_key
        
        if TAVILLY_AVAILABLE and self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
            self.available = True
        else:
            self.client = None
            self.available = False
            print("Warning: Tavily not available. Install with: pip install tavily-python")
    
    def scrape_reddit(
        self,
        query: str,
        max_results: int = 10,
        time_range: str = "month",
        subreddits: Optional[List[str]] = None
    ) -> List[RedditPost]:
        """
        Scrape Reddit for Gymshark-related discussions.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            time_range: Time range (day, week, month, year)
            subreddits: Specific subreddits to search (optional)
            
        Returns:
            List of Reddit posts with analysis
        """
        if not self.available:
            return []
        
        # Build search query for Reddit
        reddit_query = f"site:reddit.com {query}"
        if subreddits:
            reddit_query += " " + " OR ".join([f"r/{sub}" for sub in subreddits])
        
        try:
            # Search Tavily
            search_result = self.client.search(
                query=reddit_query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                time_range=time_range,
                include_raw_content=True
            )
            
            posts = []
            
            for result in search_result.get("results", []):
                # Extract Reddit-specific data
                post = self._parse_reddit_post(result)
                if post:
                    posts.append(post)
            
            # Sort by score/relevance
            posts.sort(key=lambda x: x.score, reverse=True)
            
            return posts
            
        except Exception as e:
            print(f"Error scraping Reddit: {e}")
            return []
    
    def _parse_reddit_post(self, result: Dict) -> Optional[RedditPost]:
        """Parse a Tavily result into Reddit post data."""
        try:
            # Extract URL to identify subreddit
            url = result.get("url", "")
            subreddit_match = re.search(r"reddit\.com/r/([^/]+)", url)
            subreddit = subreddit_match.group(1) if subreddit_match else "unknown"
            
            # Extract keywords from title and content
            title = result.get("title", "")
            content = result.get("content", "")
            
            keywords = self._extract_keywords(title + " " + content)
            
            # Simple sentiment analysis (keyword-based)
            sentiment = self._analyze_sentiment(title + " " + content)
            
            # Relevance score based on keyword match
            relevance = self._calculate_relevance(title + " " + content, ["gym", "fitness", "workout", "training", "gymshark"])
            
            return RedditPost(
                subreddit=subreddit,
                title=title,
                author=result.get("author", "unknown"),
                score=result.get("score", 0),
                comments_count=result.get("comments_count", 0),
                url=url,
                content=content,
                keywords=keywords,
                sentiment=sentiment,
                relevance_score=relevance
            )
            
        except Exception as e:
            print(f"Error parsing Reddit post: {e}")
            return None
    
    def scrape_seo_pages(
        self,
        query: str,
        max_results: int = 10,
        time_range: str = "month"
    ) -> List[SEOKeyword]:
        """
        Scrape SEO pages for keyword research.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            time_range: Time range
            
        Returns:
            List of SEO keywords with search data
        """
        if not self.available:
            return []
        
        try:
            # Search for SEO-related content
            search_result = self.client.search(
                query=f"{query} SEO keywords",
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                time_range=time_range,
                include_domains=["moz.com", "ahrefs.com", "semrush.com", "searchengineland.com"]
            )
            
            keywords = []
            seen_keywords = set()
            
            for result in search_result.get("results", []):
                # Extract keywords from SEO articles
                article_keywords = self._extract_seo_keywords(result)
                
                for kw in article_keywords:
                    if kw.lower() not in seen_keywords:
                        seen_keywords.add(kw.lower())
                        
                        # Determine intent
                        intent = self._classify_keyword_intent(kw)
                        
                        # Estimate difficulty (simplified)
                        difficulty = self._estimate_keyword_difficulty(kw)
                        
                        keywords.append(SEOKeyword(
                            keyword=kw,
                            search_volume=None,  # Would need additional API for this
                            difficulty=difficulty,
                            intent=intent,
                            source="seo_page",
                            confidence=0.7
                        ))
            
            return keywords
            
        except Exception as e:
            print(f"Error scraping SEO pages: {e}")
            return []
    
    def extract_google_keywords(
        self,
        research_data: List[RedditPost],
        seo_keywords: List[SEOKeyword],
        max_keywords: int = 20
    ) -> List[GoogleKeyword]:
        """
        Extract Google keywords for bidding from research data.
        
        Args:
            research_data: Reddit posts and research
            seo_keywords: SEO keyword data
            max_keywords: Maximum keywords to extract
            
        Returns:
            List of Google keywords with bidding suggestions
        """
        all_keywords = []
        
        # Extract from Reddit posts
        for post in research_data:
            for keyword in post.keywords:
                if self._is_biddable_keyword(keyword):
                    all_keywords.append(keyword)
        
        # Extract from SEO keywords
        for kw in seo_keywords:
            if self._is_biddable_keyword(kw.keyword):
                all_keywords.append(kw.keyword)
        
        # Remove duplicates and sort by frequency
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        
        # Sort by frequency and take top keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        
        google_keywords = []
        
        for keyword, count in sorted_keywords:
            # Determine match type based on keyword structure
            match_type = self._determine_match_type(keyword)
            
            # Suggest bid (simplified logic)
            bid_suggestion = self._suggest_bid(keyword)
            
            # Assess competition (simplified)
            competition = self._assess_competition(keyword)
            
            # Calculate relevance to Gymshark
            relevance = self._calculate_relevance(keyword, ["gym", "fitness", "workout", "training", "gymshark"])
            
            # Determine search intent
            intent = self._classify_keyword_intent(keyword)
            
            google_keywords.append(GoogleKeyword(
                keyword=keyword,
                match_type=match_type,
                bid_suggestion=bid_suggestion,
                competition=competition,
                relevance_to_gymshark=relevance,
                search_intent=intent
            ))
        
        return google_keywords
    
    def generate_thrad_inputs(
        self,
        research_data: List[RedditPost],
        google_keywords: List[GoogleKeyword]
    ) -> List[ThradInput]:
        """
        Generate inputs for Thrad BERT classification.
        
        Args:
            research_data: Research data from Reddit and SEO
            google_keywords: Google keywords for bidding
            
        Returns:
            List of Thrad inputs with classification
        """
        thrad_inputs = []
        
        # Generate from Reddit posts
        for post in research_data[:10]:  # Top 10 posts
            for keyword in post.keywords[:3]:  # Top 3 keywords per post
                # Determine category based on content
                category = self._classify_thrad_category(post.content)
                
                thrad_inputs.append(ThradInput(
                    query=keyword,
                    category=category,
                    confidence=post.relevance_score,
                    source="reddit",
                    context=post.title
                ))
        
        # Generate from Google keywords
        for kw in google_keywords[:10]:
            # Determine category based on intent
            category = self._classify_thrad_category(kw.keyword)
            
            thrad_inputs.append(ThradInput(
                query=kw.keyword,
                category=category,
                confidence=kw.relevance_to_gymshark,
                source="google_keywords",
                context=f"Bidding keyword with {kw.intent} intent"
            ))
        
        # Sort by confidence and deduplicate
        thrad_inputs.sort(key=lambda x: x.confidence, reverse=True)
        
        # Remove duplicates by query
        seen_queries = set()
        unique_inputs = []
        for inp in thrad_inputs:
            if inp.query.lower() not in seen_queries:
                seen_queries.add(inp.query.lower())
                unique_inputs.append(inp)
        
        return unique_inputs
    
    def generate_content_ideas(
        self,
        research_data: List[RedditPost],
        seo_keywords: List[SEOKeyword],
        google_keywords: None
    ) -> List[ContentIdea]:
        """
        Generate content ideas from research findings.
        
        Args:
            research_data: Research data from Reddit
            seo_keywords: SEO keyword data
            google_keywords: Google keywords (optional)
            
        Returns:
            List of content ideas with opportunity scores
        """
        content_ideas = []
        
        # Generate ideas from Reddit discussions
        for post in research_data[:15]:  # Top 15 posts
            # Extract common themes
            themes = self._extract_themes_from_post(post)
            
            for theme in themes[:2]:  # Top 2 themes per post
                # Determine target audience from subreddit
                if post.subreddit in ["fitness", "bodyweight", "Fitness", "Gym"]:
                    audience = "Fitness enthusiasts"
                elif post.subreddit in "gymshark":
                    audience = "Gymshark customers"
                else:
                    audience = "General fitness audience"
                
                # Determine platform based on content
                if "video" in post.content.lower() or "tiktok" in post.content.lower():
                    platform = "tiktok"
                    content_type = "video"
                elif "image" in post.content.lower():
                    platform = "instagram"
                    content_type = "image"
                else:
                    platform = "meta"
                    content_type = "carousel"
                
                # Extract relevant keywords
                keywords = post.keywords[:5]
                
                # Calculate opportunity score
                opportunity = post.relevance_score * 1.2 if post.score > 100 else post.relevance_score
                
                content_ideas.append(ContentIdea(
                    topic=theme,
                    angle=f"Community-driven: {post.title[:50]}",
                    target_audience=audience,
                    platform=platform,
                    content_type=content_type,
                    keywords=keywords,
                    reasoning=f"Based on Reddit discussion with {post.score} upvotes",
                    opportunity_score=min(opportunity, 1.0)
                ))
        
        # Generate ideas from SEO keywords
        for kw in seo_keywords[:10]:
            # Determine content type based on intent
            if kw.intent == "informational":
                content_type = "carousel"
            elif kw.intent == "transactional":
                content_type = "image"
            else:
                content_type = "video"
            
            # Determine platform
            platform = "google" if kw.intent == "transactional" else "meta"
            
            content_ideas.append(ContentIdea(
                topic=kw.keyword,
                angle=f"SEO-optimized: {kw.keyword} content for {kw.intent} intent",
                target_audience="Fitness shoppers",
                platform=platform,
                content_type=content_type,
                keywords=[kw.keyword],
                reasoning=f"SEO keyword with {kw.intent} intent, difficulty: {kw.difficulty}",
                opportunity_score=kw.confidence
            ))
        
        # Sort by opportunity score
        content_ideas.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return content_ideas[:20]  # Top 20 ideas
    
    def perform_comprehensive_research(
        self,
        base_query: str = "Gymshark fitness apparel",
        max_results_per_source: int = 10,
        time_range: str = "month"
    ) -> ResearchResult:
        """
        Perform comprehensive research across all sources.
        
        Args:
            base_query: Base search query
            max_results_per_source: Max results per source
            time_range: Time range for search
            
        Returns:
            Complete research result with all data
        """
        print(f"Starting comprehensive research for: {base_query}")
        
        # Scrape Reddit
        print("Scraping Reddit...")
        reddit_posts = self.scrape_reddit(
            query=base_query,
            max_results=max_results_per_source,
            time_range=time_range,
            subreddits=["fitness", "bodyweight", "Gymshark"]
        )
        print(f"Found {len(reddit_posts)} Reddit posts")
        
        # Scrape SEO pages
        print("Scraping SEO pages...")
        seo_keywords = self.scrape_seo_pages(
            query=base_query,
            max_results=max_results_per_source,
            time_range=time_range
        )
        print(f"Found {len(seo_keywords)} SEO keywords")
        
        # Extract Google keywords
        print("Extracting Google keywords...")
        google_keywords = self.extract_google_keywords(
            research_data=reddit_posts,
            seo_keywords=seo_keywords,
            max_keywords=20
        )
        print(f"Extracted {len(google_keywords)} Google keywords")
        
        # Generate Thrad inputs
        print("Generating Thrad BERT inputs...")
        thrad_inputs = self.generate_thrad_inputs(
            research_data=reddit_posts,
            google_keywords=google_keywords
        )
        print(f"Generated {len(thrad_inputs)} Thrad inputs")
        
        # Generate content ideas
        print("Generating content ideas...")
        content_ideas = self.generate_content_ideas(
            research_data=reddit_posts,
            seo_keywords=seo_keywords,
            google_keywords=google_keywords
        )
        print(f"Generated {len(content_ideas)} content ideas")
        
        # Generate summary
        summary = self._generate_summary(
            reddit_posts=reddit_posts,
            seo_keywords=seo_keywords,
            google_keywords=google_keywords,
            thrad_inputs=thrad_inputs,
            content_ideas=content_ideas
        )
        
        return ResearchResult(
            query=base_query,
            timestamp=datetime.now().isoformat(),
            reddit_posts=reddit_posts,
            seo_keywords=seo_keywords,
            google_keywords=google_keywords,
            thrad_inputs=thrad_inputs,
            content_ideas=content_ideas,
            summary=summary
        )
    
    # ============ HELPER METHODS ============
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Remove special characters and split into words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common stop words
        stop_words = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "her", "was", "one", "our", "out"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment analysis."""
        positive_words = ["good", "great", "love", "best", "amazing", "excellent", "perfect", "recommend", "awesome"]
        negative_words = ["bad", "terrible", "worst", "hate", "dislike", "poor", "awful", "avoid"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_relevance(self, text: str, target_keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matching."""
        text_lower = text.lower()
        matches = sum(1 for keyword in target_keywords if keyword.lower() in text_lower)
        
        # Normalize to 0-1 range
        return min(matches / len(target_keywords), 1.0)
    
    def _extract_seo_keywords(self, result: Dict) -> List[str]:
        """Extract SEO keywords from an article."""
        title = result.get("title", "")
        content = result.get("content", "")
        
        # Look for keyword patterns in SEO articles
        keyword_patterns = [
            r"keyword[s]?\s*[:\s]*([^\n]+)",
            r"rank[s]?\s*for\s*[:\s]*([^\n]+)",
            r"target keyword[s]?\s*[:\s]*([^\n]+)",
            r"search term[s]?\s*[:\s]*([^\n]+)"
        ]
        
        keywords = []
        for pattern in keyword_patterns:
            matches = re.findall(pattern, title + " " + content, re.IGNORECASE)
            for match in matches:
                keywords.append(match.strip())
        
        return list(set(keywords))
    
    def _classify_keyword_intent(self, keyword: str) -> str:
        """Classify keyword intent."""
        transactional_words = ["buy", "purchase", "shop", "order", "price", "cheap", "best", "deal"]
        informational_words = ["how", "what", "why", "guide", "tutorial", "tips", "best way to"]
        navigational_words = ["official", "website", "login", "sign up", "register"]
        
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in transactional_words):
            return "transactional"
        elif any(word in keyword_lower for word in informational_words):
            return "informational"
        elif any(word in keyword_lower for word in navigational_words):
            return "navigational"
        else:
            return "informational"
    
    def _estimate_keyword_difficulty(self, keyword: str) -> float:
        """Estimate keyword difficulty (simplified)."""
        # Longer keywords are generally less competitive
        length_difficulty = max(0.1, 1.0 - (len(keyword) / 20))
        
        # Transactional keywords are more competitive
        intent = self._classify_keyword_intent(keyword)
        if intent == "transactional":
            return 0.8
        elif intent == "informational":
            return 0.4
        else:
            return 0.5
    
    def _is_biddable_keyword(self, keyword: str) -> bool:
        """Check if keyword is suitable for bidding."""
        # Filter out too short or too long keywords
        if len(keyword) < 3 or len(keyword) > 30:
            return False
        
        # Filter out generic words
        generic_words = ["the", "and", "for", "with", "about", "from", "this", "that"]
        if keyword.lower() in generic_words:
            return False
        
        return True
    
    def _determine_match_type(self, keyword: str) -> str:
        """Determine Google Ads match type."""
        if " " in keyword:
            return "phrase"
        elif "-" in keyword:
            return "exact"
        else:
            return "broad"
    
    def _suggest_bid(self, keyword: str) -> float:
        """Suggested bid amount (simplified logic)."""
        # Base bid based on keyword length and type
        base_bid = 2.0
        
        # Adjust based on keyword length
        length_adjust = 1.0 + (len(keyword) * 0.1)
        
        # Adjust based on intent
        intent = self._classify_keyword_intent(keyword)
        if intent == "transactional":
            intent_adjust = 1.5
        else:
            intent_adjust = 1.0
        
        return round(base_bid * length_adjust * intent_adjust, 2)
    
    def _assess_competition(self, keyword: str) -> str:
        """Assess keyword competition (simplified)."""
        # Shorter, transactional keywords are more competitive
        intent = self._classify_keyword_intent(keyword)
        length = len(keyword)
        
        if intent == "transactional" and length < 5:
            return "high"
        elif intent == "transactional" and length >= 5:
            return "medium"
        elif intent == "informational":
            return "low"
        else:
            return "medium"
    
    def _classify_thrad_category(self, text: str) -> str:
        """Classify content for Thrad BERT (H=High intent, G=Growth, A=Awareness)."""
        text_lower = text.lower()
        
        high_intent_keywords = ["buy", "purchase", "shop", "order", "price", "cheap", "deal", "discount"]
        growth_keywords = ["expand", "grow", "scale", "increase", "launch", "new"]
        awareness_keywords = ["what", "how", "guide", "tips", "best", "learn", "discover"]
        
        if any(kw in text_lower for kw in high_intent_keywords):
            return "H"
        elif any(kw in text_lower for kw in growth_keywords):
            return "G"
        else:
            return "A"
    
    def _extract_themes_from_post(self, post: RedditPost) -> List[str]:
        """Extract themes from Reddit post."""
        # Extract noun phrases as themes
        words = post.content.split()
        
        # Simple theme extraction: look for significant phrases
        themes = []
        current_theme = []
        
        for word in words:
            if word[0].isupper():  # Capitalized words might be theme start
                if current_theme:
                    current_theme.append(word)
                else:
                    if current_theme:
                        themes.append(" ".join(current_theme))
                    current_theme = [word]
            else:
                if current_theme:
                    themes.append(" ".join(current_theme))
                    current_theme = []
        
        # Add title as a theme
        themes.append(post.title)
        
        return list(set(themes))
    
    def _generate_summary(
        self,
        reddit_posts: List[RedditPost],
        seo_keywords: List[SEOKeyword],
        google_keywords: List[GoogleKeyword],
        thrad_inputs: List[ThradInput],
        content_ideas: List[ContentIdea]
    ) -> str:
        """Generate summary of research findings."""
        summary_parts = []
        
        summary_parts.append(f"Research found {len(reddit_posts)} Reddit discussions")
        
        if reddit_posts:
            top_post = reddit_posts[0]
            summary_parts.append(f"Top discussion: '{top_post.title[:50]}...' with {top_post.score} upvotes")
        
        summary_parts.append(f"Identified {len(seo_keywords)} SEO keywords from SEO pages")
        summary_parts.append(f"Extracted {len(google_keywords)} Google keywords for bidding")
        summary_parts.append(f"Generated {len(thrad_inputs)} Thrad BERT inputs")
        summary_parts.append(f"Generated {len(content_ideas)} content ideas")
        
        # Top Google keyword
        if google_keywords:
            top_kw = google_keywords[0]
            summary_parts.append(f"Top bidding keyword: '{top_kw.keyword}' ({top_kw.match_type} match, £{top_kw.bid_suggestion} bid)")
        
        # Top content idea
        if content_ideas:
            top_idea = content_ideas[0]
            summary_parts.append(f"Top content idea: '{top_idea.topic}' for {top_idea.platform} (score: {top_idea.opportunity_score:.2f})")
        
        return ". ".join(summary_parts) + "."
    
    def get_research_summary(self, research_result: ResearchResult) -> Dict:
        """Get a summary of the research result."""
        return {
            "query": research_result.query,
            "timestamp": research_result.timestamp,
            "reddit_posts_count": len(research_result.reddit_posts),
            "seo_keywords_count": len(research_result.seo_keywords),
            "google_keywords_count": len(research_result.google_keywords),
            "thrad_inputs_count": len(research_result.thrad_inputs),
            "content_ideas_count": len(research_result.content_ideas),
            "summary": research_result.summary,
            "top_reddit_post": asdict(research_result.reddit_posts[0]) if research_result.reddit_posts else None,
            "top_google_keyword": asdict(research_result.google_keywords[0]) if research_result.google_keywords else None,
            "top_content_idea": asdict(research_result.content_ideas[0]) if research_result.content_ideas else None
        }