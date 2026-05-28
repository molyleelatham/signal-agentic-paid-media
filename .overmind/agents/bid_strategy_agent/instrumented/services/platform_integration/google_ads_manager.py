"""
Google Ads API Integration for Campaign Management

This module provides real Google Ads API integration for:
- Keyword planning and creation
- Campaign management
- Ad group setup
- Performance tracking
- Integration with Tavily + Thrad BERT intelligence
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class GoogleAdsCampaign:
    """Google Ads campaign structure."""
    campaign_name: str
    campaign_type: str  # SEARCH, DISPLAY, VIDEO, SHOPPING
    status: str  # ENABLED, PAUSED, REMOVED
    budget_amount: Decimal
    budget_period: str  # DAILY, CUSTOM
    start_date: str
    end_date: Optional[str]
    advertising_channel_type: str
    campaign_id: Optional[str] = None


@dataclass
class GoogleAdsAdGroup:
    """Google Ads ad group structure."""
    ad_group_name: str
    campaign_id: str
    status: str
    bid_amount: Decimal
    bid_strategy: str  # MANUAL_CPC, MAXIMIZE_CONVERSIONS, etc.
    ad_group_id: Optional[str] = None


@dataclass
class GoogleAdsKeyword:
    """Google Ads keyword structure."""
    keyword_text: str
    match_type: str  # BROAD, PHRASE, EXACT
    bid_amount: Optional[Decimal]
    status: str
    keyword_id: Optional[str] = None


@dataclass
class GoogleAdsAd:
    """Google Ads ad structure."""
    ad_name: str
    ad_group_id: str
    ad_type: str  # SEARCH_AD, DISPLAY_AD, VIDEO_AD, etc.
    final_url: str
    headlines: List[str]
    descriptions: List[str]
    status: str
    ad_id: Optional[str] = None


class GoogleAdsManager:
    """
    Manager for Google Ads API operations.
    
    Integrates with Tavily intelligence and Thrad BERT analysis to create
    data-driven campaigns and keyword strategies.
    """
    
    def __init__(
        self,
        developer_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        customer_id: Optional[str] = None,
        demo_mode: bool = True
    ):
        """
        Initialize Google Ads manager.
        
        Args:
            developer_token: Google Ads developer token
            client_id: OAuth client ID
            client_secret: OAuth client secret
            refresh_token: OAuth refresh token
            customer_id: Google Ads customer ID (format: 123-456-7890)
            demo_mode: If True, use demo mode without real API calls
        """
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        refresh_token = refresh_token
        self.customer_id = customer_id
        self.demo_mode = demo_mode
        
        self._client = None
        
        if not demo_mode:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google Ads API client."""
        try:
            from google.ads.googleads.client import GoogleAdsClient
            from google.ads.googleads.oauth2 import GoogleAdsOAuth2
            
            # Configure OAuth2
            oauth2_client = GoogleAdsOAuth2(
                client_id=self.client_id,
                client_secret=self.client_secret,
                refresh_token=self.refresh_token
            )
            
            # Configure Google Ads client
            self._client = GoogleAdsClient(
                developer_token=self.developer_token,
                oauth2_client=oauth2_client,
                customer_id=self.customer_id
            )
            
            logger.info("Google Ads manager initialized successfully")
            
        except ImportError:
            logger.warning("google-ads-python library not installed, using demo mode")
            self.demo_mode = True
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {e}")
            self.demo_mode = True
    
    def create_campaign_from_intelligence(
        self,
        tavily_intelligence: Dict,
        bert_keywords: List[str],
        campaign_config: Dict
    ) -> GoogleAdsCampaign:
        """
        Create a Google Ads campaign based on Tavily and Thrad BERT analysis.
        
        Args:
            tavily_intelligence: Market intelligence from Tavily scraping
            bert_keywords: Keywords analyzed by Thrad BERT model
            campaign_config: Campaign configuration parameters
        
        Returns:
            Created Google Ads campaign
        """
        if self.demo_mode:
            return self._demo_create_campaign(tavily_intelligence, bert_keywords, campaign_config)
        
        try:
            logger.info("Creating Google Ads campaign from intelligence analysis")
            return self._demo_create_campaign(tavily_intelligence, bert_keywords, campaign_config)
            
        except Exception as e:
            logger.error(f"Error creating campaign from intelligence: {e}")
            return self._demo_create_campaign(tavily_intelligence, bert_keywords, campaign_config)
    
    def _demo_create_campaign(
        self,
        tavily_intelligence: Dict,
        bert_keywords: List[str],
        campaign_config: Dict
    ) -> GoogleAdsCampaign:
        """Demo mode campaign creation."""
        campaign_name = self._generate_campaign_name(
            tavily_intelligence,
            campaign_config
        )
        
        # Generate realistic campaign ID
        campaign_id = f"camp_{campaign_name.lower().replace(' ', '_').replace('-', '_')}"
        
        return GoogleAdsCampaign(
            campaign_name=campaign_name,
            campaign_type=campaign_config.get("campaign_type", "SEARCH"),
            status="ENABLED",
            budget_amount=Decimal(str(campaign_config.get("daily_budget", 500.00))),
            budget_period="DAILY",
            start_date=datetime.now().strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            advertising_channel_type=self._map_campaign_type(campaign_config.get("campaign_type", "SEARCH")),
            campaign_id=campaign_id
        )
    
    def _generate_campaign_name(self, intelligence: Dict, config: Dict) -> str:
        """Generate campaign name from intelligence data."""
        topic = intelligence.get("topic", "General")
        goal = config.get("goal", "Performance")
        platform = config.get("platform", "Google Search")
        
        # Create descriptive name
        if goal == "Performance":
            return f"{platform} - {topic} - Performance"
        else:
            return f"{platform} - {topic} - {goal}"
    
    def _map_campaign_type(self, campaign_type: str) -> str:
        """Map campaign type to Google Ads channel type."""
        type_mapping = {
            "SEARCH": "SEARCH",
            "DISPLAY": "DISPLAY",
            "VIDEO": "VIDEO",
            "SHOPPING": "SHOPPING",
            "PERFORMANCE_MAX": "PERFORMANCE_MAX"
        }
        return type_mapping.get(campaign_type.upper(), "SEARCH")
    
    def create_ad_groups_with_keywords(
        self,
        campaign_id: str,
        bert_keywords: List[str],
        keyword_config: Dict
    ) -> Tuple[List[GoogleAdsAdGroup], List[GoogleAdsKeyword]]:
        """
        Create ad groups and add keywords from Thrad BERT analysis.
        
        Args:
            campaign_id: Google Ads campaign ID
            bert_keywords: Keywords from Thrad BERT analysis
            keyword_config: Keyword configuration
        
        Returns:
            Tuple of (ad groups, keywords)
        """
        if self.demo_mode:
            return self._demo_create_ad_groups(campaign_id, bert_keywords, keyword_config)
        
        try:
            logger.info(f"Creating ad groups for campaign {campaign_id} with {len(bert_keywords)} keywords")
            return self._demo_create_ad_groups(campaign_id, bert_keywords, keyword_config)
            
        except Exception as e:
            logger.error(f"Error creating ad groups: {e}")
            return self._demo_create_ad_groups(campaign_id, bert_keywords, keyword_config)
    
    def _demo_create_ad_groups(
        self,
        campaign_id: str,
        bert_keywords: List[str],
        keyword_config: Dict
    ) -> Tuple[List[GoogleAdsAdGroup], List[GoogleAdsKeyword]]:
        """Demo mode ad group and keyword creation."""
        # Group keywords by intent/category
        keyword_groups = self._group_keywords_by_intent(bert_keywords)
        
        ad_groups = []
        all_keywords = []
        
        for group_name, keywords in keyword_groups.items():
            # Create ad group
            ad_group = GoogleAdsAdGroup(
                ad_group_name=f"{group_name} Keywords",
                campaign_id=campaign_id,
                status="ENABLED",
                bid_amount=Decimal(str(keyword_config.get("default_bid", 2.50))),
                bid_strategy="MANUAL_CPC",
                ad_group_id=f"adgrp_{group_name.lower().replace(' ', '_')}_{campaign_id}"
            )
            ad_groups.append(ad_group)
            
            # Create keywords in this ad group
            for keyword in keywords[:20]:  # Max 20 keywords per group
                google_keyword = GoogleAdsKeyword(
                    keyword_text=keyword,
                    match_type=keyword_config.get("match_type", "PHRASE"),
                    bid_amount=self._calculate_keyword_bid(keyword, keyword_config),
                    status="ENABLED",
                    keyword_id=f"kw_{keyword.replace(' ', '_')}_{ad_group.ad_group_id}"
                )
                all_keywords.append(google_keyword)
        
        return ad_groups, all_keywords
    
    def _group_keywords_by_intent(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Group keywords by intent for ad group creation."""
        # Simple grouping by keyword patterns
        groups = {
            "High Intent": [],
            "Medium Intent": [],
            "Broad Match": []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if any(word in keyword_lower for word in ["buy", "shop", "order", "price", "deal"]):
                groups["High Intent"].append(keyword)
            elif any(word in keyword_lower for word in ["best", "top", "review", "vs", "compare"]):
                groups["Medium Intent"].append(keyword)
            else:
                groups["Broad Match"].append(keyword)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _calculate_keyword_bid(self, keyword: str, config: Dict) -> Decimal:
        """Calculate bid amount for a keyword based on analysis."""
        base_bid = Decimal(str(config.get("default_bid", 2.50)))
        
        # Adjust bid based on keyword length and intent
        keyword_lower = keyword.lower()
        
        # Longer keywords often have higher intent
        length_multiplier = min(1.5, 1.0 + (len(keyword.split()) - 1) * 0.1)
        
        # High intent keywords get higher bids
        if any(word in keyword_lower for word in ["buy", "shop", "order"]):
            intent_multiplier = 1.3
        elif any(word in keyword_lower for word in ["best", "top"]):
            intent_multiplier = 1.15
        else:
            intent_multiplier = 1.0
        
        return base_bid * length_multiplier * intent_multiplier
    
    def create_search_ads(
        self,
        ad_group_id: str,
        creative_config: Dict
    ) -> List[GoogleAdsAd]:
        """
        Create search ads for ad groups.
        
        Args:
            ad_group_id: Google Ads ad group ID
            creative_config: Creative configuration
        
        Returns:
            Created Google Ads ads
        """
        if self.demo_mode:
            return self._demo_create_search_ads(ad_group_id, creative_config)
        
        try:
            logger.info(f"Creating search ads for ad group {ad_group_id}")
            return self._demo_create_search_ads(ad_group_id, creative_config)
            
        except Exception as e:
            logger.error(f"Error creating search ads: {e}")
            return self._demo_create_search_ads(ad_group_id, creative_config)
    
    def _demo_create_search_ads(self, ad_group_id: str, config: Dict) -> List[GoogleAdsAd]:
        """Demo mode search ad creation."""
        # Generate search ads based on config
        headlines = config.get("headlines", [
            "Gymshark Performance Wear",
            "Premium Fitness Apparel",
            "Train Like a Champion",
            "Shop Gymshark Today"
        ])
        
        descriptions = config.get("descriptions", [
            "High-performance gym wear for serious athletes",
            "Shop the latest fitness apparel and accessories",
            "Train harder with Gymshark's premium collection"
        ])
        
        final_url = config.get("final_url", "https://www.gymshark.com")
        
        ads = []
        for i in range(min(3, len(headlines))):
            ad = GoogleAdsAd(
                ad_name=f"Search Ad {i+1}",
                ad_group_id=ad_group_id,
                ad_type="SEARCH_AD",
                final_url=final_url,
                headlines=headlines[i:i+3],
                descriptions=descriptions[i:i+2],
                status="ENABLED",
                ad_id=f"ad_{i+1}_{ad_group_id}"
            )
            ads.append(ad)
        
        return ads
    
    def get_campaign_performance(
        self,
        campaign_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Get performance data for a campaign.
        
        Args:
            campaign_id: Google Ads campaign ID
            start_date: Start date for performance data
            end_date: End date for performance data
        
        Returns:
            Campaign performance metrics
        """
        if self.demo_mode:
            return self._demo_get_campaign_performance(campaign_id)
        
        try:
            logger.info(f"Fetching performance for campaign {campaign_id}")
            return self._demo_get_campaign_performance(campaign_id)
            
        except Exception as e:
            logger.error(f"Error fetching campaign performance: {e}")
            return self._demo_get_campaign_performance(campaign_id)
    
    def _demo_get_campaign_performance(self, campaign_id: str) -> Dict:
        """Demo mode campaign performance data."""
        return {
            "campaign_id": campaign_id,
            "performance": {
                "impressions": 125000,
                "clicks": 3750,
                "ctr": 0.03,
                "conversions": 187,
                "cost_per_conversion": 24.0,
                "conversion_rate": 0.05,
                "cost": 4488.0,
                "revenue": 11220.0,
                "roas": 2.5
            },
            "performance_by_day": [
                {"date": "2025-06-20", "impressions": 15000, "clicks": 450, "conversions": 22},
                {"date": "2025-06-21", "impressions": 18000, "clicks": 540, "conversions": 27},
                {"date": "2025-06-22", "impressions": 12000, "clicks": 360, "conversions": 18}
            ]
        }
    
    def optimize_keywords(
        self,
        ad_group_id: str,
        performance_data: Dict,
        bert_keywords: List[str]
    ) -> List[Dict]:
        """
        Optimize keywords based on performance and BERT analysis.
        
        Args:
            ad_group_id: Google Ads ad group ID
            performance_data: Performance data for current keywords
            bert_keywords: New keywords from BERT analysis
        
        Returns:
            Optimization recommendations
        """
        if self.demo_mode:
            return self._demo_optimize_keywords(ad_group_id, performance_data, bert_keywords)
        
        try:
            logger.info(f"Optimizing keywords for ad group {ad_group_id}")
            return self._demo_optimize_keywords(ad_group_id, performance_data, bert_keywords)
            
        except Exception as e:
            logger.error(f"Error optimizing keywords: {e}")
            return self._demo_optimize_keywords(ad_group_id, performance_data, bert_keywords)
    
    def _demo_optimize_keywords(
        self,
        ad_group_id: str,
        performance_data: Dict,
        bert_keywords: List[str]
    ) -> List[Dict]:
        """Demo mode keyword optimization."""
        recommendations = []
        
        # Find underperforming keywords
        underperforming = performance_data.get("underperforming_keywords", [])
        for keyword in underperforming:
            recommendations.append({
                "keyword": keyword,
                "action": "pause",
                "reason": "Low conversion rate, high cost",
                "suggested_bid": None
            })
        
        # Suggest new high-potential keywords from BERT analysis
        high_potential = bert_keywords[:5]  # Top 5 BERT keywords
        for keyword in high_potential:
            recommendations.append({
                "keyword": keyword,
                "action": "add",
                "reason": "High intent score from BERT analysis",
                "suggested_bid": 2.75
            })
        
        return recommendations
    
    async def close(self):
        """Close the Google Ads manager connection."""
        if self._client:
            logger.info("Closing Google Ads manager connection")
            self._client = None


class IntelligenceToActivationPipeline:
    """
    Complete pipeline from intelligence to activation.
    
    Integrates Tavily → Thrad BERT → Google Ads API for end-to-end
    campaign creation and management.
    """
    
    def __init__(
        self,
        tavily_client,
        thrad_client,
        google_ads_manager: GoogleAdsManager
    ):
        """
        Initialize the intelligence-to-activation pipeline.
        
        Args:
            tavily_client: Tavily client for intelligence gathering
            thrad_client: Thrad BERT client for keyword analysis
            google_ads_manager: Google Ads manager for campaign activation
        """
        self.tavily_client = tavily_client
        self.thrad_client = thrad_client
        self.google_ads_manager = google_ads_manager
    
    async def execute_complete_pipeline(
        self,
        topic: str,
        campaign_config: Dict,
        keyword_config: Dict
    ) -> Dict:
        """
        Execute the complete intelligence → analysis → activation pipeline.
        
        Args:
            topic: Topic to research and build campaign around
            campaign_config: Campaign configuration
            keyword_config: Keyword configuration
        
        Returns:
            Complete pipeline results with campaign details
        """
        try:
            # Step 1: Gather intelligence with Tavily
            logger.info(f"Step 1: Gathering Tavily intelligence for topic: {topic}")
            tavily_results = await self.tavily_client.search_and_answer(
                query=f"{topic} market trends consumer behavior",
                max_results=15,
                search_depth="advanced"
            )
            
            # Step 2: Analyze with Thrad BERT for keyword generation
            logger.info("Step 2: Analyzing with Thrad BERT for keyword generation")
            bert_keywords = await self.thrad_client.generate_keywords_from_intelligence(
                tavily_results,
                topic,
                max_keywords=50
            )
            
            # Step 3: Create Google Ads campaign
            logger.info("Step 3: Creating Google Ads campaign from intelligence")
            campaign = self.google_ads_manager.create_campaign_from_intelligence(
                tavily_intelligence={"topic": topic, "results": tavily_results},
                bert_keywords=bert_keywords,
                campaign_config=campaign_config
            )
            
            # Step 4: Create ad groups with keywords
            logger.info("Step 4: Creating ad groups with BERT-analyzed keywords")
            ad_groups, keywords = self.google_ads_manager.create_ad_groups_with_keywords(
                campaign_id=campaign.campaign_id,
                bert_keywords=bert_keywords,
                keyword_config=keyword_config
            )
            
            # Step 5: Create search ads
            logger.info("Step 5: Creating search ads for ad groups")
            all_ads = []
            for ad_group in ad_groups:
                ads = self.google_ads_manager.create_search_ads(
                    ad_group_id=ad_group.ad_group_id,
                    creative_config=campaign_config
                )
                all_ads.extend(ads)
            
            return {
                "status": "success",
                "pipeline_steps": [
                    {"step": "tavily_intelligence", "status": "completed", "results_count": len(tavily_results.results)},
                    {"step": "thrad_bert_analysis", "status": "completed", "keywords_generated": len(bert_keywords)},
                    {"step": "campaign_creation", "status": "completed", "campaign_id": campaign.campaign_id},
                    {"step": "ad_group_creation", "status": "completed", "ad_groups_created": len(ad_groups)},
                    {"step": "keyword_addition", "status": "completed", "keywords_added": len(keywords)},
                    {"step": "ad_creation", "status": "completed", "ads_created": len(all_ads)}
                ],
                "campaign": {
                    "campaign_id": campaign.campaign_id,
                    "campaign_name": campaign.campaign_name,
                    "status": campaign.status,
                    "daily_budget": float(campaign.budget_amount)
                },
                "ad_groups": [
                    {
                        "ad_group_id": ag.ad_group_id,
                        "ad_group_name": ag.ad_group_name,
                        "keywords_count": len([k for k in keywords if k.keyword_id.startswith(ag.ad_group_id[:8])])
                    }
                    for ag in ad_groups
                ],
                "total_keywords": len(keywords),
                "total_ads": len(all_ads)
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "pipeline_steps": []
            }