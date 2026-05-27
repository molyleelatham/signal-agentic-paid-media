"""
Demo data script for Acme fashion e-commerce client.
Populates the database with realistic demo data for the hackathon demonstration.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database import get_async_session
from shared.models.client import Client, ClientGoal, ClientPlatform
from shared.models.campaign import Campaign, CampaignPerformance
from shared.models.content import ContentBrief, TopicCluster
from shared.models.analytics import (
    PerformanceMetric, BudgetAllocation, BidResult, 
    AttentionTokenTransaction, EfficiencyMetrics
)
from shared.models.creative import Creative, CreativePlacement


async def create_acme_client(session: AsyncSession) -> Client:
    """Create the Acme fashion e-commerce client."""
    
    client = Client(
        name="Acme Fashion",
        industry="Fashion E-commerce",
        website="https://acmefashion.com",
        company_size="mid_market",
        annual_revenue_range="10m_50m",
        status="active",
        metadata={
            "description": "Premium fashion retailer specializing in sustainable clothing",
            "target_audience": "Fashion-conscious millennials and Gen Z",
            "brand_voice": "Modern, sustainable, inclusive",
            "primary_markets": ["US", "UK", "Germany", "France"],
            "product_categories": ["women", "men", "accessories", "sustainable"]
        }
    )
    session.add(client)
    await session.flush()
    await session.refresh(client)
    
    # Add client goals
    goals = [
        ClientGoal(
            client_id=client.id,
            goal_type="lead_generation",
            target_value=1000,
            timeframe="weekly",
            priority=1,
            current_value=850,
            metadata={"cpl_target": 25.0}
        ),
        ClientGoal(
            client_id=client.id,
            goal_type="customer_acquisition",
            target_value=200,
            timeframe="weekly",
            priority=2,
            current_value=180,
            metadata={"cac_target": 45.0}
        ),
        ClientGoal(
            client_id=client.id,
            goal_type="brand_awareness",
            target_value=500000,
            timeframe="weekly",
            priority=3,
            current_value=420000,
            metadata={"impressions_target": 500000}
        ),
        ClientGoal(
            client_id=client.id,
            goal_type="revenue",
            target_value=50000,
            timeframe="weekly",
            priority=1,
            current_value=42000,
            metadata={"arpu_target": 233.33}
        )
    ]
    session.add_all(goals)
    
    # Add platforms
    platforms = [
        ClientPlatform(
            client_id=client.id,
            platform="meta",
            status="active",
            daily_budget=Decimal("500.00"),
            metadata={
                "ad_account_id": "act_123456789",
                "spend_last_30_days": 15000.00,
                "roas_last_30_days": 3.2
            }
        ),
        ClientPlatform(
            client_id=client.id,
            platform="google",
            status="active",
            daily_budget=Decimal("400.00"),
            metadata={
                "ad_account_id": "AW-987654321",
                "spend_last_30_days": 12000.00,
                "roas_last_30_days": 2.8
            }
        ),
        ClientPlatform(
            client_id=client.id,
            platform="tiktok",
            status="active",
            daily_budget=Decimal("300.00"),
            metadata={
                "ad_account_id": "tiktok_456789123",
                "spend_last_30_days": 9000.00,
                "roas_last_30_days": 2.5
            }
        ),
        ClientPlatform(
            client_id=client.id,
            platform="microsoft",
            status="active",
            daily_budget=Decimal("200.00"),
            metadata={
                "ad_account_id": "ms_789123456",
                "spend_last_30_days": 6000.00,
                "roas_last_30_days": 2.1
            }
        )
    ]
    session.add_all(platforms)
    
    await session.commit()
    return client


async def create_campaigns(session: AsyncSession, client: Client):
    """Create sample campaigns for Acme."""
    
    base_date = datetime.now() - timedelta(days=30)
    
    campaigns = [
        Campaign(
            client_id=client.id,
            name="Summer Collection Launch",
            platform="meta",
            campaign_type="awareness",
            status="active",
            start_date=base_date,
            end_date=base_date + timedelta(days=60),
            daily_budget=Decimal("300.00"),
            total_budget=Decimal("18000.00"),
            target_audience={
                "age_range": ["18-34"],
                "genders": ["female", "male"],
                "interests": ["fashion", "sustainable fashion", "clothing"],
                "locations": ["US", "UK", "Germany"]
            },
            metadata={
                "creative_count": 15,
                "ad_sets": 5
            }
        ),
        Campaign(
            client_id=client.id,
            name="Sustainable Fashion Campaign",
            platform="google",
            campaign_type="conversion",
            status="active",
            start_date=base_date + timedelta(days=7),
            end_date=base_date + timedelta(days=67),
            daily_budget=Decimal("250.00"),
            total_budget=Decimal("15000.00"),
            target_audience={
                "keywords": ["sustainable fashion", "eco clothing", "ethical fashion"],
                "locations": ["US", "UK", "Germany", "France"],
                "device_types": ["mobile", "desktop"]
            },
            metadata={
                "ad_groups": 8,
                "keywords_count": 150
            }
        ),
        Campaign(
            client_id=client.id,
            name="TikTok Trending Styles",
            platform="tiktok",
            campaign_type="engagement",
            status="active",
            start_date=base_date + timedelta(days=14),
            end_date=base_date + timedelta(days=74),
            daily_budget=Decimal("200.00"),
            total_budget=Decimal("12000.00"),
            target_audience={
                "age_range": ["16-24"],
                "interests": ["fashion trends", "tiktok fashion", "style inspiration"],
                "locations": ["US", "UK"]
            },
            metadata={
                "video_count": 20,
                "hashtag_count": 30
            }
        ),
        Campaign(
            client_id=client.id,
            name="Back to School Collection",
            platform="microsoft",
            campaign_type="consideration",
            status="paused",
            start_date=base_date - timedelta(days=7),
            end_date=base_date + timedelta(days=53),
            daily_budget=Decimal("150.00"),
            total_budget=Decimal("9000.00"),
            target_audience={
                "keywords": ["back to school fashion", "college clothing", "student fashion"],
                "locations": ["US"],
                "device_types": ["desktop", "tablet"]
            },
            metadata={
                "ad_groups": 6,
                "keywords_count": 80
            }
        )
    ]
    session.add_all(campaigns)
    await session.flush()
    
    # Create campaign performance data
    for campaign in campaigns:
        for day_offset in range(30):
            perf_date = base_date + timedelta(days=day_offset)
            
            # Generate realistic performance metrics
            if campaign.platform == "meta":
                impressions = 50000 + (day_offset * 1000)
                clicks = int(impressions * 0.025)
                conversions = int(clicks * 0.03)
                spend = Decimal(str(campaign.daily_budget * (0.8 + (day_offset % 5) * 0.05)))
                revenue = Decimal(str(conversions * 150 * (1.2 + (day_offset % 3) * 0.1)))
            elif campaign.platform == "google":
                impressions = 30000 + (day_offset * 800)
                clicks = int(impressions * 0.035)
                conversions = int(clicks * 0.045)
                spend = Decimal(str(campaign.daily_budget * (0.9 + (day_offset % 4) * 0.025)))
                revenue = Decimal(str(conversions * 180 * (1.3 + (day_offset % 2) * 0.15)))
            elif campaign.platform == "tiktok":
                impressions = 80000 + (day_offset * 2000)
                clicks = int(impressions * 0.04)
                conversions = int(clicks * 0.02)
                spend = Decimal(str(campaign.daily_budget * (0.85 + (day_offset % 6) * 0.025)))
                revenue = Decimal(str(conversions * 120 * (1.1 + (day_offset % 4) * 0.05)))
            else:  # microsoft
                impressions = 20000 + (day_offset * 500)
                clicks = int(impressions * 0.03)
                conversions = int(clicks * 0.04)
                spend = Decimal(str(campaign.daily_budget * (0.7 + (day_offset % 3) * 0.1)))
                revenue = Decimal(str(conversions * 160 * (1.15 + (day_offset % 2) * 0.1)))
            
            performance = CampaignPerformance(
                campaign_id=campaign.id,
                date=perf_date,
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                spend=spend,
                revenue=revenue,
                ctr=Decimal(str(clicks / impressions if impressions > 0 else 0)),
                cpa=Decimal(str(spend / conversions if conversions > 0 else 0)),
                roas=Decimal(str(revenue / spend if spend > 0 else 0)),
                metadata={
                    "avg_position": 2.3 if campaign.platform == "google" else None,
                    "engagement_rate": 0.04 if campaign.platform == "tiktok" else None
                }
            )
            session.add(performance)
    
    await session.commit()


async def create_content_briefs(session: AsyncSession, client: Client):
    """Create content briefs based on Tavily intelligence and topic clustering."""
    
    base_date = datetime.now() - timedelta(days=14)
    
    briefs = [
        ContentBrief(
            client_id=client.id,
            title="Sustainable Summer Fashion Trends",
            brief_type="creative",
            status="completed",
            created_at=base_date,
            metadata={
                "source": "tavily_crawling",
                "topic_clusters": ["sustainable fashion", "summer trends", "eco-friendly materials"],
                "target_audience": "Millennials interested in sustainability",
                "key_insights": [
                    "62% increase in searches for 'sustainable summer fashion'",
                    "High engagement on recycled material content",
                    "Growing interest in transparent supply chains"
                ],
                "creative_guidance": {
                    "tone": "aspirational yet practical",
                    "visual_style": "bright, natural lighting",
                    "key_messages": ["sustainability", "quality", "style"]
                },
                "platforms": ["meta", "tiktok", "instagram"],
                "content_types": ["video", "carousel", "story"]
            }
        ),
        ContentBrief(
            client_id=client.id,
            title="Gen Z Fashion Micro-Trends",
            brief_type="creative",
            status="in_progress",
            created_at=base_date + timedelta(days=7),
            metadata={
                "source": "tavily_crawling",
                "topic_clusters": ["gen z fashion", "micro-trends", "tiktok fashion"],
                "target_audience": "Gen Z fashion enthusiasts",
                "key_insights": [
                    "Cottagecore aesthetic trending 340%",
                    "Y2K revival showing strong engagement",
                    "Thrift flip content performing well"
                ],
                "creative_guidance": {
                    "tone": "authentic, relatable",
                    "visual_style": "user-generated content style",
                    "key_messages": ["individuality", "sustainability", "community"]
                },
                "platforms": ["tiktok", "instagram_reels"],
                "content_types": ["short_form_video", "ugc"]
            }
        ),
        ContentBrief(
            client_id=client.id,
            title="Back to Campus Fashion Guide",
            brief_type="creative",
            status="pending",
            created_at=base_date + timedelta(days=10),
            metadata={
                "source": "tavily_crawling",
                "topic_clusters": ["back to school", "campus fashion", "student style"],
                "target_audience": "College students",
                "key_insights": [
                    "Early back-to-school shopping starting in July",
                    "Comfort-focused styles gaining traction",
                    "Budget-friendly options highly searched"
                ],
                "creative_guidance": {
                    "tone": "helpful, relatable",
                    "visual_style": "campus settings, diverse models",
                    "key_messages": ["comfort", "value", "style"]
                },
                "platforms": ["meta", "tiktok", "pinterest"],
                "content_types": ["video", "carousel", "static_image"]
            }
        )
    ]
    session.add_all(briefs)
    
    # Create topic clusters
    clusters = [
        TopicCluster(
            client_id=client.id,
            name="Sustainable Fashion",
            keywords=["sustainable fashion", "eco clothing", "ethical fashion", "recycled materials"],
            search_volume=125000,
            competition_score=0.65,
            trend_direction="up",
            last_updated=base_date,
            metadata={
                "growth_rate": 0.23,
                "seasonal": True,
                "peak_months": [6, 7, 8],
                "related_topics": ["zero waste fashion", "circular fashion", "vegan fashion"]
            }
        ),
        TopicCluster(
            client_id=client.id,
            name="Summer Fashion Trends",
            keywords=["summer fashion", "summer outfits", "beach style", "vacation fashion"],
            search_volume=89000,
            competition_score=0.72,
            trend_direction="up",
            last_updated=base_date + timedelta(days=3),
            metadata={
                "growth_rate": 0.18,
                "seasonal": True,
                "peak_months": [5, 6, 7, 8],
                "related_topics": ["resort wear", "festival fashion", "summer accessories"]
            }
        ),
        TopicCluster(
            client_id=client.id,
            name="Gen Z Fashion",
            keywords=["gen z fashion", "tiktok fashion", "y2k fashion", "cottagecore"],
            search_volume=156000,
            competition_score=0.58,
            trend_direction="up",
            last_updated=base_date + timedelta(days=5),
            metadata={
                "growth_rate": 0.34,
                "seasonal": False,
                "peak_months": [],
                "related_topics": ["micro-trends", "thrift flip", "aesthetic fashion"]
            }
        )
    ]
    session.add_all(clusters)
    
    await session.commit()


async def create_creatives(session: AsyncSession, client: Client):
    """Create sample creatives with placements."""
    
    base_date = datetime.now() - timedelta(days=14)
    
    creatives = [
        Creative(
            client_id=client.id,
            name="Summer Collection Hero Video",
            creative_type="video",
            format="horizontal",
            status="active",
            created_at=base_date,
            metadata={
                "duration": 30,
                "file_url": "https://cdn.acmefashion.com/creatives/summer-hero.mp4",
                "thumbnail_url": "https://cdn.acmefashion.com/creatives/summer-hero-thumb.jpg",
                "dimensions": "1920x1080",
                "file_size_mb": 12.5,
                "tags": ["summer", "collection", "hero", "sustainable"]
            }
        ),
        Creative(
            client_id=client.id,
            name="Sustainable Materials Carousel",
            creative_type="carousel",
            format="square",
            status="active",
            created_at=base_date + timedelta(days=2),
            metadata={
                "card_count": 5,
                "file_url": "https://cdn.acmefashion.com/creatives/sustainable-carousel.zip",
                "thumbnail_url": "https://cdn.acmefashion.com/creatives/sustainable-carousel-thumb.jpg",
                "dimensions": "1080x1080",
                "file_size_mb": 8.2,
                "tags": ["sustainable", "materials", "educational", "carousel"]
            }
        ),
        Creative(
            client_id=client.id,
            name="Gen Z Trend TikTok Video",
            creative_type="video",
            format="vertical",
            status="active",
            created_at=base_date + timedelta(days=5),
            metadata={
                "duration": 15,
                "file_url": "https://cdn.acmefashion.com/creatives/genz-trend.mp4",
                "thumbnail_url": "https://cdn.acmefashion.com/creatives/genz-trend-thumb.jpg",
                "dimensions": "1080x1920",
                "file_size_mb": 6.8,
                "tags": ["gen_z", "tiktok", "trending", "vertical"]
            }
        ),
        Creative(
            client_id=client.id,
            name="Back to School Static Image",
            creative_type="static_image",
            format="horizontal",
            status="pending",
            created_at=base_date + timedelta(days=10),
            metadata={
                "file_url": "https://cdn.acmefashion.com/creatives/back-to-school.jpg",
                "thumbnail_url": "https://cdn.acmefashion.com/creatives/back-to-school-thumb.jpg",
                "dimensions": "1200x628",
                "file_size_mb": 2.1,
                "tags": ["back_to_school", "campus", "students", "fall"]
            }
        )
    ]
    session.add_all(creatives)
    await session.flush()
    
    # Create creative placements
    placements = [
        CreativePlacement(
            creative_id=creatives[0].id,
            platform="meta",
            placement="feed",
            status="active",
            metadata={
                "ad_set_id": "23845678901234567",
                "campaign_id": "23845678901234568",
                "placement_details": "facebook_feed, instagram_feed"
            }
        ),
        CreativePlacement(
            creative_id=creatives[0].id,
            platform="meta",
            placement="story",
            status="active",
            metadata={
                "ad_set_id": "23845678901234567",
                "campaign_id": "23845678901234568",
                "placement_details": "facebook_story, instagram_story"
            }
        ),
        CreativePlacement(
            creative_id=creatives[1].id,
            platform="meta",
            placement="feed",
            status="active",
            metadata={
                "ad_set_id": "23845678901234569",
                "campaign_id": "23845678901234570",
                "placement_details": "instagram_feed"
            }
        ),
        CreativePlacement(
            creative_id=creatives[2].id,
            platform="tiktok",
            placement="in_feed",
            status="active",
            metadata={
                "ad_group_id": "1234567890123456789",
                "campaign_id": "1234567890123456790",
                "placement_details": "tiktok_for_business"
            }
        ),
        CreativePlacement(
            creative_id=creatives[2].id,
            platform="tiktok",
            placement="top_view",
            status="pending",
            metadata={
                "ad_group_id": "1234567890123456789",
                "campaign_id": "1234567890123456790",
                "placement_details": "tiktok_top_view"
            }
        )
    ]
    session.add_all(placements)
    
    await session.commit()


async def create_efficiency_metrics(session: AsyncSession, client: Client):
    """Create efficiency metrics showing improvement over time."""
    
    base_date = datetime.now() - timedelta(days=60)
    
    # Before SIGNAL (first 30 days)
    for day_offset in range(30):
        metric_date = base_date + timedelta(days=day_offset)
        
        # Higher CPL, lower leads (before optimization)
        cpl = Decimal(str(35.0 + (day_offset % 10) * 2.0))
        leads = int(800 + (day_offset % 5) * 20)
        cac = Decimal(str(55.0 + (day_offset % 8) * 3.0))
        customers = int(150 + (day_offset % 4) * 10)
        roas = Decimal(str(2.1 + (day_offset % 6) * 0.2))
        
        metric = PerformanceMetric(
            client_id=client.id,
            date=metric_date,
            metric_type="efficiency",
            value={
                "cpl": float(cpl),
                "leads": leads,
                "cac": float(cac),
                "customers": customers,
                "roas": float(roas),
                "ltv_cac": 3.2,
                "retention_rate": 0.68,
                "cart_abandonment": 0.72
            },
            metadata={"period": "before_signal"}
        )
        session.add(metric)
    
    # After SIGNAL (last 30 days) - showing improvement
    signal_start_date = base_date + timedelta(days=30)
    for day_offset in range(30):
        metric_date = signal_start_date + timedelta(days=day_offset)
        
        # Improvement trend: 20% lower CPL, 40% more leads
        improvement_factor = 1.0 - (day_offset / 30) * 0.2  # CPL decreases
        lead_improvement = 1.0 + (day_offset / 30) * 0.4  # Leads increase
        
        cpl = Decimal(str(35.0 * improvement_factor + (day_offset % 10) * 1.0))
        leads = int(800 * lead_improvement + (day_offset % 5) * 25)
        cac = Decimal(str(55.0 * improvement_factor + (day_offset % 8) * 2.0))
        customers = int(150 * lead_improvement + (day_offset % 4) * 12)
        roas = Decimal(str(2.1 + (day_offset / 30) * 1.2 + (day_offset % 6) * 0.15))
        
        metric = PerformanceMetric(
            client_id=client.id,
            date=metric_date,
            metric_type="efficiency",
            value={
                "cpl": float(cpl),
                "leads": leads,
                "cac": float(cac),
                "customers": customers,
                "roas": float(roas),
                "ltv_cac": 4.1,  # Improved from 3.2
                "retention_rate": 0.78,  # Improved from 0.68
                "cart_abandonment": 0.58  # Improved from 0.72
            },
            metadata={"period": "after_signal"}
        )
        session.add(metric)
    
    # Create efficiency metrics summary
    efficiency = EfficiencyMetrics(
        client_id=client.id,
        period_start=base_date + timedelta(days=30),
        period_end=datetime.now(),
        cpl_reduction=Decimal("0.20"),  # 20% reduction
        lead_increase=Decimal("0.40"),  # 40% increase
        roas_improvement=Decimal("0.55"),  # 55% improvement
        cac_reduction=Decimal("0.18"),  # 18% reduction
        ltv_cac_improvement=Decimal("0.28"),  # 28% improvement
        retention_improvement=Decimal("0.15"),  # 15% improvement
        abandonment_reduction=Decimal("0.19"),  # 19% reduction
        metadata={
            "before_signal": {
                "avg_cpl": 35.0,
                "avg_leads_per_week": 800,
                "avg_roas": 2.1,
                "avg_ltv_cac": 3.2,
                "avg_retention": 0.68,
                "avg_abandonment": 0.72
            },
            "after_signal": {
                "avg_cpl": 28.0,
                "avg_leads_per_week": 1120,
                "avg_roas": 3.25,
                "avg_ltv_cac": 4.1,
                "avg_retention": 0.78,
                "avg_abandonment": 0.58
            }
        }
    )
    session.add(efficiency)
    
    await session.commit()


async def create_budget_allocations(session: AsyncSession, client: Client):
    """Create budget allocation history showing decay-based decisions."""
    
    base_date = datetime.now() - timedelta(days=28)
    
    # Weekly allocation rounds (every 7 days)
    for week in range(4):
        allocation_date = base_date + timedelta(days=week * 7)
        
        # Decay alpha rate affects allocation decisions
        # Earlier weeks have more exploration, later weeks more exploitation
        decay_rate = 0.95 - (week * 0.05)  # Decreasing decay rate
        
        allocation = BudgetAllocation(
            client_id=client.id,
            allocation_date=allocation_date,
            total_budget=Decimal("3500.00"),  # Weekly budget
            allocations={
                "meta": {
                    "budget": Decimal("1000.00"),
                    "percentage": 0.286,
                    "reasoning": "Strong performance on sustainable fashion content"
                },
                "google": {
                    "budget": Decimal("900.00"),
                    "percentage": 0.257,
                    "reasoning": "High intent traffic for summer collection"
                },
                "tiktok": {
                    "budget": Decimal("1000.00"),
                    "percentage": 0.286,
                    "reasoning": "Gen Z engagement driving brand awareness"
                },
                "microsoft": {
                    "budget": Decimal("600.00"),
                    "percentage": 0.171,
                    "reasoning": "Steady performance, lower priority"
                }
            },
            decay_alpha_rate=Decimal(str(decay_rate)),
            decision_type="thompson_sampling",
            metadata={
                "week": week + 1,
                "exploration_budget": Decimal("350.00"),
                "exploitation_budget": Decimal("3150.00"),
                "agent_recommendations": {
                    "market_analysis": "Increase TikTok budget for Gen Z trends",
                    "bid_strategy": "Focus on high-intent keywords on Google",
                    "creative_optimization": "Double down on sustainable content"
                }
            }
        )
        session.add(allocation)
    
    await session.commit()


async def create_attention_token_transactions(session: AsyncSession, client: Client):
    """Create attention token transactions showing rewards and penalties."""
    
    base_date = datetime.now() - timedelta(days=14)
    
    transactions = [
        AttentionTokenTransaction(
            client_id=client.id,
            transaction_type="reward",
            amount=Decimal("150.00"),
            reason="High-performing creative (Summer Collection)",
            metadata={
                "creative_id": "creative_1",
                "performance_score": 0.92,
                "roas": 4.2,
                "agent_bonus": True
            },
            created_at=base_date
        ),
        AttentionTokenTransaction(
            client_id=client.id,
            transaction_type="reward",
            amount=Decimal("120.00"),
            reason="Successful topic cluster targeting (Sustainable Fashion)",
            metadata={
                "topic_cluster": "Sustainable Fashion",
                "engagement_rate": 0.08,
                "conversion_rate": 0.045
            },
            created_at=base_date + timedelta(days=2)
        ),
        AttentionTokenTransaction(
            client_id=client.id,
            transaction_type="penalty",
            amount=Decimal("-30.00"),
            reason="Underperforming creative placement",
            metadata={
                "creative_id": "creative_3",
                "performance_score": 0.45,
                "ctr": 0.015
            },
            created_at=base_date + timedelta(days=4)
        ),
        AttentionTokenTransaction(
            client_id=client.id,
            transaction_type="reward",
            amount=Decimal("200.00"),
            reason="Efficiency milestone achieved (20% CPL reduction)",
            metadata={
                "milestone": "cpl_reduction_20_percent",
                "previous_cpl": 35.0,
                "current_cpl": 28.0
            },
            created_at=base_date + timedelta(days=7)
        ),
        AttentionTokenTransaction(
            client_id=client.id,
            transaction_type="reward",
            amount=Decimal("180.00"),
            reason="Lead generation target exceeded (40% increase)",
            metadata={
                "milestone": "lead_increase_40_percent",
                "target_leads": 1000,
                "actual_leads": 1120
            },
            created_at=base_date + timedelta(days=10)
        ),
        AttentionTokenTransaction(
            client_id=client.id,
            transaction_type="reward",
            amount=Decimal("100.00"),
            reason="Agent optimization quality improvement",
            metadata={
                "agent_type": "bid_strategy",
                "overmind_score": 0.88,
                "optimization_cycles": 5
            },
            created_at=base_date + timedelta(days=12)
        )
    ]
    session.add_all(transactions)
    
    await session.commit()


async def main():
    """Main function to populate demo data."""
    
    print("🎨 Creating Acme Fashion demo data...")
    
    async with get_async_session() as session:
        # Check if client already exists
        result = await session.execute(
            select(Client).where(Client.name == "Acme Fashion")
        )
        existing_client = result.scalar_one_or_none()
        
        if existing_client:
            print("⚠️  Acme Fashion client already exists. Skipping creation.")
            return
        
        # Create client and related data
        client = await create_acme_client(session)
        print(f"✅ Created client: {client.name}")
        
        await create_campaigns(session, client)
        print(f"✅ Created campaigns and performance data")
        
        await create_content_briefs(session, client)
        print(f"✅ Created content briefs and topic clusters")
        
        await create_creatives(session, client)
        print(f"✅ Created creatives and placements")
        
        await create_efficiency_metrics(session, client)
        print(f"✅ Created efficiency metrics")
        
        await create_budget_allocations(session, client)
        print(f"✅ Created budget allocation history")
        
        await create_attention_token_transactions(session, client)
        print(f"✅ Created attention token transactions")
        
        print("\n🎉 Demo data creation complete!")
        print(f"📊 Client ID: {client.id}")
        print(f"🏢 Client: {client.name}")
        print(f"🎯 Industry: {client.industry}")


if __name__ == "__main__":
    asyncio.run(main())