"""
Demo data script for Gymshark fitness apparel client.
Populates the database with realistic demo data for the hackathon demonstration.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from shared.database import get_async_session
from shared.models.client import Client, ClientGoal, ClientPlatform
from shared.models.campaign import Campaign, CampaignPerformance
from shared.models.content import ContentBrief, TopicCluster
from shared.models.analytics import (
    PerformanceMetric, BudgetAllocation, BidResult, 
    AttentionTokenTransaction, EfficiencyMetrics,
    FunnelStage, ChannelMapping, ScenarioModel, OfflineCost
)
from shared.models.creative import Creative, CreativePlacement
from shared.models.trading import AdstockDecay


async def create_gymshark_client(session: AsyncSession) -> Client:
    """Create the Gymshark fitness apparel client."""
    
    client = Client(
        id=str(uuid.uuid4()),
        name="Gymshark",
        industry="Fitness Apparel E-commerce",
        status="active",
        metadata={
            "description": "Leading fitness apparel and accessories brand targeting gym enthusiasts and athletes",
            "target_audience": "Fitness enthusiasts, gym-goers, athletes aged 18-35",
            "brand_voice": "Motivational, energetic, inclusive, performance-focused",
            "primary_markets": ["US", "UK", "Germany", "France", "Australia"],
            "product_categories": ["menswear", "womenswear", "accessories", "training", "gym essentials"],
            "founded_year": 2012,
            "headquarters": "Solihull, UK",
            "unique_value_prop": "High-performance gym wear with community-driven brand"
        }
    )
    session.add(client)
    await session.flush()
    await session.refresh(client)
    
    # Add client goals
    goals = [
        ClientGoal(
            id=str(uuid.uuid4()),
            client_id=client.id,
            goal_type="lead_generation",
            target_value=Decimal("1000"),
            current_value=Decimal("850"),
            period="weekly",
            is_active=True,
            metadata={"cpl_target": 25.0}
        ),
        ClientGoal(
            id=str(uuid.uuid4()),
            client_id=client.id,
            goal_type="customer_acquisition",
            target_value=Decimal("200"),
            current_value=Decimal("180"),
            period="weekly",
            is_active=True,
            metadata={"cac_target": 45.0}
        ),
        ClientGoal(
            id=str(uuid.uuid4()),
            client_id=client.id,
            goal_type="brand_awareness",
            target_value=Decimal("500000"),
            current_value=Decimal("420000"),
            period="weekly",
            is_active=True,
            metadata={"impressions_target": 500000}
        ),
        ClientGoal(
            id=str(uuid.uuid4()),
            client_id=client.id,
            goal_type="revenue",
            target_value=Decimal("50000"),
            current_value=Decimal("42000"),
            period="weekly",
            is_active=True,
            metadata={"arpu_target": 233.33}
        )
    ]
    session.add_all(goals)
    
    # Add platforms
    platforms = [
        ClientPlatform(
            id=str(uuid.uuid4()),
            client_id=client.id,
            platform="meta",
            is_active=True,
            configuration={
                "ad_account_id": "act_987654321",
                "spend_last_30_days": 18000.00,
                "roas_last_30_days": 3.4,
                "primary_platforms": ["facebook", "instagram"]
            }
        ),
        ClientPlatform(
            id=str(uuid.uuid4()),
            client_id=client.id,
            platform="google",
            is_active=True,
            configuration={
                "ad_account_id": "AW-123456789",
                "spend_last_30_days": 15000.00,
                "roas_last_30_days": 3.8,
                "conversion_tracking": True
            }
        ),
        ClientPlatform(
            id=str(uuid.uuid4()),
            client_id=client.id,
            platform="tiktok",
            is_active=True,
            configuration={
                "ad_account_id": "tiktok_456789123",
                "spend_last_30_days": 12000.00,
                "roas_last_30_days": 2.9,
                "engagement_rate": 0.042
            }
        ),
        ClientPlatform(
            id=str(uuid.uuid4()),
            client_id=client.id,
            platform="microsoft",
            is_active=True,
            configuration={
                "ad_account_id": "ms_789123456",
                "spend_last_30_days": 8000.00,
                "roas_last_30_days": 3.1,
                "search_market_share": 0.35
            }
        )
    ]
    session.add_all(platforms)
    
    await session.commit()
    return client


async def create_funnel_stages(session: AsyncSession, client: Client):
    """Create funnel stage definitions for scenario modeling."""
    
    funnel_stages = [
        FunnelStage(
            id=str(uuid.uuid4()),
            name="awareness",
            description="Brand building and reach activities to create awareness",
            risk_level="low",
            expected_roi_min=Decimal("1.5"),
            expected_roi_max=Decimal("2.5"),
            time_to_conversion="long"
        ),
        FunnelStage(
            id=str(uuid.uuid4()),
            name="consideration",
            description="Nurturing and education to drive consideration",
            risk_level="medium",
            expected_roi_min=Decimal("2.0"),
            expected_roi_max=Decimal("3.5"),
            time_to_conversion="medium"
        ),
        FunnelStage(
            id=str(uuid.uuid4()),
            name="performance",
            description="Direct response and conversion-focused activities",
            risk_level="high",
            expected_roi_min=Decimal("2.5"),
            expected_roi_max=Decimal("5.0"),
            time_to_conversion="short"
        )
    ]
    
    session.add_all(funnel_stages)
    await session.flush()
    
    return funnel_stages


async def create_channel_mappings(session: AsyncSession, client: Client, funnel_stages: list):
    """Create channel to funnel stage mappings."""
    
    # Create a mapping dict for easy lookup
    stage_map = {stage.name: stage.id for stage in funnel_stages}
    
    channel_mappings = [
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="meta",
            funnel_stage_id=stage_map["consideration"],
            default_allocation_weight=0.3,
            typical_cpa=Decimal("25.00"),
            typical_conversion_rate=0.035,
            is_active=True
        ),
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="google",
            funnel_stage_id=stage_map["performance"],
            default_allocation_weight=0.4,
            typical_cpa=Decimal("22.00"),
            typical_conversion_rate=0.045,
            is_active=True
        ),
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="tiktok",
            funnel_stage_id=stage_map["awareness"],
            default_allocation_weight=0.5,
            typical_cpa=Decimal("18.00"),
            typical_conversion_rate=0.025,
            is_active=True
        ),
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="microsoft",
            funnel_stage_id=stage_map["performance"],
            default_allocation_weight=0.3,
            typical_cpa=Decimal("28.00"),
            typical_conversion_rate=0.040,
            is_active=True
        ),
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="instagram",
            funnel_stage_id=stage_map["awareness"],
            default_allocation_weight=0.3,
            typical_cpa=Decimal("22.00"),
            typical_conversion_rate=0.028,
            is_active=True
        ),
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="reddit",
            funnel_stage_id=stage_map["consideration"],
            default_allocation_weight=0.2,
            typical_cpa=Decimal("20.00"),
            typical_conversion_rate=0.030,
            is_active=True
        ),
        ChannelMapping(
            id=str(uuid.uuid4()),
            channel_name="ooh",
            funnel_stage_id=stage_map["awareness"],
            default_allocation_weight=0.2,
            typical_cpa=Decimal("50.00"),
            typical_conversion_rate=0.010,
            is_active=True
        )
    ]
    
    session.add_all(channel_mappings)
    await session.commit()


async def create_campaigns(session: AsyncSession, client: Client):
    """Create sample campaigns for Gymshark."""
    
    base_date = datetime.now() - timedelta(days=30)
    
    campaigns = [
        Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name="Summer Training Collection Launch",
            platform="meta",
            status="active",
            start_date=base_date,
            end_date=base_date + timedelta(days=60),
            daily_budget=Decimal("300.00"),
            total_budget=Decimal("18000.00"),
            target_audience={
                "age_range": ["18-34"],
                "genders": ["female", "male"],
                "interests": ["fitness", "gym", "workout", "athletic apparel", "training"],
                "locations": ["US", "UK", "Germany"]
            },
            metadata={
                "creative_count": 15,
                "ad_sets": 5
            }
        ),
        Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name="Performance Training Gear",
            platform="google",
            status="active",
            start_date=base_date + timedelta(days=7),
            end_date=base_date + timedelta(days=67),
            daily_budget=Decimal("250.00"),
            total_budget=Decimal("15000.00"),
            target_audience={
                "keywords": ["gym wear", "workout clothes", "athletic apparel", "training gear", "fitness clothing"],
                "locations": ["US", "UK", "Germany", "France"],
                "device_types": ["mobile", "desktop"]
            },
            metadata={
                "ad_groups": 8,
                "keywords_count": 150
            }
        ),
        Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name="TikTok Fitness Challenge",
            platform="tiktok",
            status="active",
            start_date=base_date + timedelta(days=14),
            end_date=base_date + timedelta(days=74),
            daily_budget=Decimal("200.00"),
            total_budget=Decimal("12000.00"),
            target_audience={
                "age_range": ["16-24"],
                "interests": ["fitness challenges", "gym tiktok", "workout routines", "fitness motivation"],
                "locations": ["US", "UK"]
            },
            metadata={
                "video_count": 20,
                "hashtag_count": 30
            }
        ),
        Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name="Microsoft Search - Gym Essentials",
            platform="microsoft",
            status="active",
            start_date=base_date + timedelta(days=21),
            end_date=base_date + timedelta(days=81),
            daily_budget=Decimal("150.00"),
            total_budget=Decimal("9000.00"),
            target_audience={
                "keywords": ["gym essentials", "workout equipment", "fitness accessories", "training gear"],
                "locations": ["US", "UK", "Germany"],
                "device_types": ["desktop", "mobile"]
            },
            metadata={
                "ad_groups": 5,
                "keywords_count": 80
            }
        )
    ]
    
    session.add_all(campaigns)
    await session.flush()
    
    # Create campaign performance data
    for campaign in campaigns:
        performance = CampaignPerformance(
            id=str(uuid.uuid4()),
            campaign_id=campaign.id,
            date=datetime.now().date() - timedelta(days=1),
            impressions=100000,
            clicks=3000,
            conversions=120,
            spend=Decimal("900.00"),
            revenue=Decimal("2700.00")
        )
        session.add(performance)
    
    await session.commit()
    return campaigns


async def create_efficiency_metrics(session: AsyncSession, client: Client):
    """Create efficiency metrics for Gymshark."""
    
    metrics = EfficiencyMetrics(
        id=str(uuid.uuid4()),
        client_id=client.id,
        # Current metrics (with SIGNAL)
        current_cpl=Decimal("28.00"),
        current_roas=3.25,
        current_leads_per_week=1120,
        
        # Previous metrics (before SIGNAL)
        previous_cpl=Decimal("35.00"),
        previous_roas=2.10,
        previous_leads_per_week=800,
        
        # Business KPIs
        ltv_cac=4.1,
        retention_rate=0.78,
        cart_abandonment_rate=0.58,
        
        # Improvement calculations
        cpl_improvement_percent=20.0,
        leads_improvement_percent=40.0,
        roas_improvement_percent=55.0,
        
        metric_date=datetime.now().date()
    )
    
    session.add(metrics)
    await session.commit()
    
    return metrics


async def create_adstock_decay_data(session: AsyncSession, client: Client, campaigns: list):
    """Create adstock decay data for campaigns with refresh timing."""
    
    base_date = datetime.now() - timedelta(days=30)
    
    # Create adstock decay records for each campaign
    adstock_data = [
        {
            "campaign_id": campaigns[0].id,  # Meta
            "lambda_decay": 0.7,
            "std_error": 0.05,
            "signal": "reduce",
            "confidence": "moderate",
            "days_since_refresh": 14
        },
        {
            "campaign_id": campaigns[1].id,  # Google
            "lambda_decay": 0.65,
            "std_error": 0.04,
            "signal": "hold",
            "confidence": "high",
            "days_since_refresh": 7
        },
        {
            "campaign_id": campaigns[2].id,  # TikTok
            "lambda_decay": 0.8,
            "std_error": 0.06,
            "signal": "exit",
            "confidence": "low",
            "days_since_refresh": 21
        },
        {
            "campaign_id": campaigns[3].id,  # Microsoft
            "lambda_decay": 0.75,
            "std_error": 0.05,
            "signal": "hold",
            "confidence": "moderate",
            "days_since_refresh": 10
        }
    ]
    
    for data in adstock_data:
        adstock = AdstockDecay(
            id=str(uuid.uuid4()),
            position_id=data["campaign_id"],
            lambda_decay=str(data["lambda_decay"]),
            std_error=str(data["std_error"]),
            signal=data["signal"],
            confidence=data["confidence"],
            calculated_at=base_date + timedelta(days=data["days_since_refresh"])
        )
        session.add(adstock)
    
    await session.commit()
    
    return adstock_data


async def main():
    """Main function to populate demo data."""
    
    async with get_async_session() as session:
        # Clear existing data
        await session.execute("DELETE FROM efficiency_metrics")
        await session.execute("DELETE FROM campaign_performance")
        await session.execute("DELETE FROM campaigns")
        await session.execute("DELETE FROM client_goals")
        await session.execute("DELETE FROM client_platforms")
        await session.execute("DELETE FROM clients")
        await session.execute("DELETE FROM channel_mappings")
        await session.execute("DELETE FROM funnel_stages")
        await session.execute("DELETE FROM adstock_decay")
        
        # Create Gymshark client
        print("Creating Gymshark client...")
        client = await create_gymshark_client(session)
        
        # Create funnel stages for scenario modeling
        print("Creating funnel stages...")
        funnel_stages = await create_funnel_stages(session, client)
        
        # Create channel mappings
        print("Creating channel mappings...")
        await create_channel_mappings(session, client, funnel_stages)
        
        # Create campaigns
        print("Creating campaigns...")
        campaigns = await create_campaigns(session, client)
        
        # Create adstock decay data
        print("Creating adstock decay data...")
        await create_adstock_decay_data(session, client, campaigns)
        
        # Create efficiency metrics
        print("Creating efficiency metrics...")
        await create_efficiency_metrics(session, client)
        
        print("Demo data creation complete!")
        print(f"Client ID: {client.id}")
        print(f"Client Name: {client.name}")


if __name__ == "__main__":
    asyncio.run(main())