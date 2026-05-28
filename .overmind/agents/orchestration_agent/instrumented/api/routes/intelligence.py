"""
Intelligence API Routes

Data gathering and analysis endpoints for Tavily crawling,
Thrad BERT analysis, DisBERT classification, and platform integration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict

from services.intelligence.tavily_client import TavilyClient
from services.intelligence.thrad_bert_client import ThradBERTClient
from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator, DisBERTThradClassification
from services.platform_integration.google_ads_manager import GoogleAdsManager, IntelligenceToActivationPipeline

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])


@router.get("/tavily-results")
async def get_tavily_intelligence(
    client_id: str = Query(..., description="Client ID"),
    topic: str = Query(..., description="Topic to research"),
    max_results: int = Query(15, description="Maximum results"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get market intelligence using Tavily scraping.
    
    Returns search results and AI-generated answers.
    """
    tavily_client = TavilyClient()
    
    results = await tavily_client.search_and_answer(
        query=f"{topic} market trends consumer behavior",
        max_results=max_results,
        search_depth="advanced"
    )
    
    return {
        "topic": topic,
        "results_count": len(results.get("results", [])),
        "answer": results.get("answer", ""),
        "query_time": results.get("query_time", 0),
        "results": results.get("results", [])
    }


@router.post("/complete-pipeline")
async def execute_intelligence_pipeline(
    client_id: str = Query(..., description="Client ID"),
    topic: str = Query(..., description="Topic to research and build campaign"),
    campaign_type: str = Query("SEARCH", description="Google Ads campaign type"),
    daily_budget: float = Query(500.0, description="Daily campaign budget"),
    match_type: str = Query("PHRASE", description="Keyword match type"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Execute complete intelligence → analysis → activation pipeline.
    
    Pipeline steps:
    1. Tavily scraping for market intelligence
    2. Thrad BERT analysis for keyword generation
    3. Google Ads campaign creation
    4. Ad group and keyword setup
    5. Search ad creation
    
    Returns complete pipeline results with campaign details.
    """
    tavily_client = TavilyClient()
    thrad_client = ThradBERTClient(demo_mode=True)
    google_ads_manager = GoogleAdsManager(demo_mode=True)
    
    # Create pipeline
    pipeline = IntelligenceToActivationPipeline(
        tavily_client=tavily_client,
        thrad_client=thrad_client,
        google_ads_manager=google_ads_manager
    )
    
    # Campaign configuration
    campaign_config = {
        "campaign_type": campaign_type,
        "daily_budget": daily_budget,
        "goal": "Performance",
        "platform": "Google Search",
        "headlines": [
            "Gymshark Performance Wear",
            "Premium Fitness Apparel",
            "Train Like a Champion"
        ],
        "descriptions": [
            "High-performance gym wear for serious athletes",
            "Shop the latest fitness apparel and accessories"
        ],
        "final_url": "https://www.gymshark.com"
    }
    
    # Keyword configuration
    keyword_config = {
        "match_type": match_type,
        "default_bid": 2.50,
        "max_keywords": 50
    }
    
    # Execute pipeline
    result = await pipeline.execute_complete_pipeline(
        topic=topic,
        campaign_config=campaign_config,
        keyword_config=keyword_config
    )
    
    return result


@router.post("/tavily-to-keywords")
async def tavily_to_keywords(
    client_id: str = Query(..., description="Client ID"),
    topic: str = Query(..., description="Topic to research"),
    max_keywords: int = Query(50, description="Maximum keywords to generate"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Step 1-2: Tavily scraping + Thrad BERT keyword generation.
    
    Returns keywords generated from intelligence analysis.
    """
    tavily_client = TavilyClient()
    thrad_client = ThradBERTClient(demo_mode=True)
    
    # Step 1: Tavily scraping
    tavily_results = await tavily_client.search_and_answer(
        query=f"{topic} market trends consumer behavior",
        max_results=15,
        search_depth="advanced"
    )
    
    # Step 2: Thrad BERT keyword generation
    keywords = await thrad_client.generate_keywords_from_intelligence(
        tavily_results=tavily_results,
        topic=topic,
        max_keywords=max_keywords
    )
    
    # Analyze keywords
    analyzed_keywords = await thrad_client.analyze_keywords(keywords, topic)
    
    # Summarize intelligence
    summary = await thrad_client.summarize_intelligence(tavily_results, topic)
    
    return {
        "topic": topic,
        "tavily_intelligence": {
            "results_count": len(tavily_results.get("results", [])),
            "answer": tavily_results.get("answer", ""),
            "query_time": tavily_results.get("query_time", 0)
        },
        "thrad_bert_analysis": {
            "keywords_generated": len(keywords),
            "analyzed_keywords": [
                {
                    "keyword": kw.keyword,
                    "relevance_score": kw.relevance_score,
                    "intent_score": kw.intent_score,
                    "volume_estimate": kw.volume_estimate,
                    "competition_score": kw.competition_score,
                    "suggested_bid": kw.suggested_bid,
                    "category": kw.category
                }
                for kw in analyzed_keywords[:20]
            ]
        },
        "intelligence_summary": {
            "key_themes": summary.key_themes,
            "trending_concepts": summary.trending_concepts,
            "consumer_insights": summary.consumer_insights,
            "market_opportunities": summary.market_opportunities
        }
    }


@router.post("/create-google-campaign")
async def create_google_campaign_from_keywords(
    client_id: str = Query(..., description="Client ID"),
    topic: str = Query(..., description="Campaign topic"),
    keywords: List[str] = None,
    campaign_type: str = Query("SEARCH", description="Campaign type"),
    daily_budget: float = Query(500.0, description="Daily budget"),
    match_type: str = Query("PHRASE", description="Match type"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Step 3-5: Create Google Ads campaign from keywords.
    
    Creates campaign, ad groups, keywords, and ads.
    """
    if not keywords:
        keywords = [
            "gym wear", "workout clothes", "athletic apparel", "training gear",
            "fitness clothing", "gym outfits", "workout gear", "gym clothes",
            "athletic wear", "fitness apparel", "training clothes", "gym attire"
        ]
    
    google_ads_manager = GoogleAdsManager(demo_mode=True)
    
    campaign_config = {
        "campaign_type": campaign_type,
        "daily_budget": daily_budget,
        "goal": "Performance",
        "platform": "Google Search",
        "headlines": [
            "Gymshark Performance Wear",
            "Premium Fitness Apparel",
            "Train Like a Champion"
        ],
        "descriptions": [
            "High-performance gym wear for serious athletes",
            "Shop the latest fitness apparel and accessories"
        ],
        "final_url": "https://www.gymshark.com"
    }
    
    keyword_config = {
        "match_type": match_type,
        "default_bid": 2.50,
        "max_keywords": len(keywords)
    }
    
    # Create campaign
    campaign = google_ads_manager.create_campaign_from_intelligence(
        tavily_intelligence={"topic": topic},
        bert_keywords=keywords,
        campaign_config=campaign_config
    )
    
    # Create ad groups with keywords
    ad_groups, google_keywords = google_ads_manager.create_ad_groups_with_keywords(
        campaign_id=campaign.campaign_id,
        bert_keywords=keywords,
        keyword_config=keyword_config
    )
    
    # Create search ads
    all_ads = []
    for ad_group in ad_groups:
        ads = google_ads_manager.create_search_ads(
            ad_group_id=ad_group.ad_group_id,
            creative_config=campaign_config
        )
        all_ads.extend(ads)
    
    return {
        "campaign": {
            "campaign_id": campaign.campaign_id,
            "campaign_name": campaign.campaign_name,
            "campaign_type": campaign.campaign_type,
            "status": campaign.status,
            "daily_budget": float(campaign.budget_amount),
            "start_date": campaign.start_date,
            "end_date": campaign.end_date
        },
        "ad_groups": [
            {
                "ad_group_id": ag.ad_group_id,
                "ad_group_name": ag.ad_group_name,
                "status": ag.status,
                "bid_amount": float(ag.bid_amount),
                "bid_strategy": ag.bid_strategy
            }
            for ag in ad_groups
        ],
        "keywords": [
            {
                "keyword_text": kw.keyword_text,
                "match_type": kw.match_type,
                "bid_amount": float(kw.bid_amount) if kw.bid_amount else None,
                "status": kw.status
            }
            for kw in google_keywords[:20]
        ],
        "ads": [
            {
                "ad_name": ad.ad_name,
                "ad_group_id": ad.ad_group_id,
                "ad_type": ad.ad_type,
                "headlines": ad.headlines,
                "descriptions": ad.descriptions,
                "status": ad.status
            }
            for ad in all_ads
        ],
        "summary": {
            "ad_groups_created": len(ad_groups),
            "keywords_added": len(google_keywords),
            "ads_created": len(all_ads)
        }
    }


@router.get("/campaign-performance")
async def get_intelligence_campaign_performance(
    client_id: str = Query(..., description="Client ID"),
    campaign_id: str = Query(..., description="Google Ads campaign ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get performance data for a Google Ads campaign.
    
    Returns impressions, clicks, conversions, ROAS, and other metrics.
    """
    google_ads_manager = GoogleAdsManager(demo_mode=True)
    
    performance = google_ads_manager.get_campaign_performance(campaign_id)
    
    return performance


@router.post("/optimize-keywords")
async def optimize_campaign_keywords(
    client_id: str = Query(..., description="Client ID"),
    ad_group_id: str = Query(..., description="Google Ads ad group ID"),
    topic: str = Query(..., description="Topic for new keyword generation"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Optimize campaign keywords using Thrad BERT analysis.
    
    Analyzes current performance and suggests keyword optimizations.
    """
    google_ads_manager = GoogleAdsManager(demo_mode=True)
    thrad_client = ThradBERTClient(demo_mode=True)
    
    # Mock performance data
    performance_data = {
        "underperforming_keywords": [
            "fitness clothes",
            "gym fashion"
        ]
    }
    
    # Generate new keywords with Thrad BERT
    new_keywords = await thrad_client.generate_keywords_from_intelligence(
        tavily_results={"results": []},
        topic=topic,
        max_keywords=20
    )
    
    # Get optimization recommendations
    recommendations = google_ads_manager.optimize_keywords(
        ad_group_id=ad_group_id,
        performance_data=performance_data,
        bert_keywords=new_keywords
    )
    
    return {
        "ad_group_id": ad_group_id,
        "current_performance": performance_data,
        "new_keywords_from_bert": new_keywords[:10],
        "optimization_recommendations": recommendations,
        "summary": {
            "keywords_to_pause": len([r for r in recommendations if r["action"] == "pause"]),
            "keywords_to_add": len([r for r in recommendations if r["action"] == "add"]),
            "total_recommendations": len(recommendations)
        }
    }


@router.get("/realtime-keywords")
async def get_realtime_keywords(
    client_id: str = Query(..., description="Client ID"),
    topic: str = Query(..., description="Topic to generate keywords for"),
    platform: str = Query("google", description="Platform (google/microsoft)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Generate real-time keywords using enhanced Tavily integration.
    
    Provides SEO keyword suggestions with search volume and competition data.
    """
    from services.intelligence.enhanced_tavily import EnhancedTavilyClient
    from services.platform_integration.google_ads import GoogleAdsClient
    
    tavily_client = TavilyClient()
    enhanced_client = EnhancedTavilyClient(tavily_client)
    google_client = GoogleAdsClient(demo_mode=True)
    
    # Generate keywords using enhanced Tavily
    positive_keywords, negative_keywords = await enhanced_client.generate_seo_keywords(
        topic=topic,
        location="US",
        language="en"
    )
    
    # Initialize Google Ads client for additional data
    google_keywords, google_negatives = await google_client.generate_keyword_suggestions(
        topic=topic,
        location="US",
        language="en"
    )
    
    return {
        "topic": topic,
        "platform": platform,
        "positive_keywords": [
            {
                "keyword": kw.keyword,
                "search_volume": kw.search_volume,
                "competition": kw.competition,
                "avg_cpc": float(kw.avg_cpc),
                "competition_index": kw.competition_index
            }
            for kw in google_keywords[:20]
        ],
        "negative_keywords": google_negatives[:15],
        "keyword_opportunities": [
            {
                "keyword": kw.keyword,
                "opportunity_score": round(kw.relevance_score * 100, 1),
                "frequency": kw.frequency
            }
            for kw in positive_keywords[:10]
        ],
        "total_keywords": len(positive_keywords),
        "generated_at": datetime.now().isoformat()
    }