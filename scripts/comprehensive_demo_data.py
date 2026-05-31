"""
Comprehensive mock data script for demo purposes.
Adds historical campaigns, model performance, keyword performance,
agent execution history, A/B tests, and content performance data.
"""

import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
import random
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database import get_async_session
from shared.models.client import Client
from shared.models.campaign import Campaign, CampaignPerformance
from shared.models.demo_models import (
    ModelPerformance,
    KeywordPerformance,
    AgentExecutionHistory,
    ABTestCampaign,
    ABTestResult,
    ContentPerformanceByChannel
)
from shared.models.content import ContentBrief


async def create_historical_campaigns(session: AsyncSession, client: Client):
    """Create 12 months of historical campaign data."""
    
    print("Creating historical campaign data (12 months)...")
    
    # Get current campaigns to avoid conflicts
    existing_campaigns = await session.execute(
        select(Campaign).where(Campaign.client_id == client.id)
    )
    existing_ids = [c.id for c in existing_campaigns.scalars().all()]
    
    base_date = datetime.now() - timedelta(days=365)
    
    # Create historical campaigns by season
    campaigns = []
    
    # Summer 2024 (June-August)
    for month in range(6, 9):
        camp = Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name=f"Summer 2024 - Month {month}",
            platform="meta",
            status="completed",
            start_date=datetime(2024, month, 1),
            end_date=datetime(2024, month, 28),
            daily_budget=Decimal("250.00"),
            total_budget=Decimal("7000.00"),
            target_audience={
                "age_range": ["18-34"],
                "interests": ["fitness", "summer", "workout"]
            },
            metadata={"season": "summer"}
        )
        campaigns.append(camp)
    
    # Fall 2024 (September-November)
    for month in range(9, 12):
        camp = Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name=f"Fall 2024 - Month {month}",
            platform="google",
            status="completed",
            start_date=datetime(2024, month, 1),
            end_date=datetime(2024, month, 28),
            daily_budget=Decimal("280.00"),
            total_budget=Decimal("7840.00"),
            target_audience={
                "keywords": ["gym wear", "fall fitness", "workout clothes"]
            },
            metadata={"season": "fall"}
        )
        campaigns.append(camp)
    
    # Winter 2025 (December-February)
    months = [12, 1, 2]
    years = [2024, 2025, 2025]
    for month, year in zip(months, years):
        camp = Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name=f"Winter {year} - Month {month}",
            platform="tiktok",
            status="completed",
            start_date=datetime(year, month, 1),
            end_date=datetime(year, month, 28),
            daily_budget=Decimal("220.00"),
            total_budget=Decimal("6160.00"),
            target_audience={
                "age_range": ["16-24"],
                "interests": ["fitness challenges", "winter workout"]
            },
            metadata={"season": "winter"}
        )
        campaigns.append(camp)
    
    # Spring 2025 (March-May)
    for month in range(3, 6):
        camp = Campaign(
            id=str(uuid.uuid4()),
            client_id=client.id,
            name=f"Spring 2025 - Month {month}",
            platform="microsoft",
            status="completed",
            start_date=datetime(2025, month, 1),
            end_date=datetime(2025, month, 28),
            daily_budget=Decimal("260.00"),
            total_budget=Decimal("7280.00"),
            target_audience={
                "keywords": ["spring fitness", "gym essentials", "workout gear"]
            },
            metadata={"season": "spring"}
        )
        campaigns.append(camp)
    
    session.add_all(campaigns)
    await session.flush()
    
    # Add weekly performance data for each campaign
    performance_records = []
    for campaign in campaigns:
        num_weeks = 4
        for week in range(num_weeks):
            perf = CampaignPerformance(
                id=str(uuid.uuid4()),
                campaign_id=campaign.id,
                date=campaign.start_date.date() + timedelta(weeks=week),
                impressions=random.randint(80000, 120000),
                clicks=random.randint(2400, 3600),
                conversions=random.randint(80, 150),
                spend=Decimal(str(random.uniform(600, 900))),
                revenue=Decimal(str(random.uniform(1800, 2700)))
            )
            performance_records.append(perf)
    
    session.add_all(performance_records)
    await session.commit()
    
    print(f"✅ Created {len(campaigns)} historical campaigns with {len(performance_records)} performance records")
    return campaigns


async def create_model_performance_data(session: AsyncSession, client: Client):
    """Create model performance tracking data."""
    
    print("Creating model performance data...")
    
    models = [
        ("bid_strategy_v1", "1.0"),
        ("bid_strategy_v2", "2.0"),
        ("keyword_classifier", "1.0"),
        ("creative_optimizer", "1.0"),
        ("budget_allocator", "1.0")
    ]
    
    prediction_types = ["bid", "budget", "keyword", "creative"]
    
    performance_records = []
    
    # Create 6 months of model performance data
    for month in range(6):
        base_date = date.today() - timedelta(days=30 * month)
        
        for model_name, model_version in models:
            for pred_type in prediction_types:
                # Create multiple predictions per month
                for _ in range(10):
                    predicted = Decimal(str(random.uniform(1.0, 100.0)))
                    actual = Decimal(str(predicted * random.uniform(0.8, 1.2)))  # ±20% error
                    
                    abs_error = abs(predicted - actual)
                    pct_error = Decimal(str((abs_error / actual) * 100))
                    is_accurate = pct_error < Decimal("15.0")  # 15% threshold
                    
                    record = ModelPerformance(
                        id=str(uuid.uuid4()),
                        model_name=model_name,
                        model_version=model_version,
                        prediction_type=pred_type,
                        predicted_value=predicted,
                        actual_value=actual,
                        absolute_error=abs_error,
                        percentage_error=pct_error,
                        is_accurate=is_accurate,
                        client_id=client.id,
                        prediction_date=base_date,
                        actual_date=base_date + timedelta(days=random.randint(1, 7))
                    )
                    performance_records.append(record)
    
    session.add_all(performance_records)
    await session.commit()
    
    print(f"✅ Created {len(performance_records)} model performance records")
    return performance_records


async def create_keyword_performance_data(session: AsyncSession, client: Client):
    """Create keyword performance data."""
    
    print("Creating keyword performance data...")
    
    # Get campaigns
    campaigns_result = await session.execute(
        select(Campaign).where(Campaign.client_id == client.id).limit(5)
    )
    campaigns = campaigns_result.scalars().all()
    
    keywords = [
        ("gymshark leggings", "phrase", "H", "transactional"),
        ("buy gym clothes", "exact", "H", "transactional"),
        ("fitness workout", "broad", "E", "informational"),
        ("gym wear for women", "phrase", "L", "informational"),
        ("workout clothes", "broad", "L", "informational"),
        ("seamless leggings", "phrase", "H", "transactional"),
        ("gym essentials", "broad", "E", "informational"),
        ("athletic apparel", "phrase", "L", "informational"),
        ("training gear", "broad", "L", "informational"),
        ("fitness accessories", "phrase", "E", "informational")
    ]
    
    performance_records = []
    
    # Create 30 days of keyword performance data
    for day in range(30):
        perf_date = date.today() - timedelta(days=day)
        
        for campaign in campaigns:
            for keyword, match_type, category, intent in keywords:
                impressions = random.randint(500, 5000)
                clicks = random.randint(15, 150)
                conversions = random.randint(0, 10)
                spend = Decimal(str(random.uniform(5.0, 50.0)))
                revenue = Decimal(str(spend * random.uniform(1.5, 4.0)))
                
                ctr = Decimal(str((clicks / impressions) * 100)) if impressions > 0 else Decimal("0.0")
                cpa = Decimal(str(spend / conversions)) if conversions > 0 else None
                roas = Decimal(str(revenue / spend)) if spend > 0 else None
                
                record = KeywordPerformance(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign.id,
                    keyword=keyword,
                    match_type=match_type,
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    spend=spend,
                    revenue=revenue,
                    ctr=ctr,
                    cpa=cpa,
                    roas=roas,
                    current_bid=Decimal(str(random.uniform(1.0, 5.0))),
                    bid_suggestion=Decimal(str(random.uniform(1.0, 5.0))),
                    category=category,
                    intent=intent,
                    performance_date=perf_date
                )
                performance_records.append(record)
    
    session.add_all(performance_records)
    await session.commit()
    
    print(f"✅ Created {len(performance_records)} keyword performance records")
    return performance_records


async def create_agent_execution_history(session: AsyncSession, client: Client):
    """Create agent execution history data."""
    
    print("Creating agent execution history...")
    
    agents = [
        ("bid_strategy_agent", "bid_strategy"),
        ("content_brief_agent", "content_brief"),
        ("creative_optimization_agent", "creative_optimization"),
        ("market_analysis_agent", "market_analysis"),
        ("orchestration_agent", "orchestration")
    ]
    
    actions = [
        "optimize_bid",
        "generate_content",
        "select_creative",
        "analyze_market",
        "coordinate_workflow"
    ]
    
    history_records = []
    
    # Create 30 days of agent execution history
    for day in range(30):
        exec_date = datetime.now() - timedelta(days=day)
        
        for agent_name, agent_type in agents:
            for _ in range(5):  # 5 executions per day per agent
                success = random.random() > 0.1  # 90% success rate
                
                record = AgentExecutionHistory(
                    id=str(uuid.uuid4()),
                    agent_name=agent_name,
                    agent_type=agent_type,
                    action=random.choice(actions),
                    input_data={"query": "gymshark fitness", "context": "demo"},
                    output_data={"result": "success"} if success else None,
                    execution_time_ms=random.randint(100, 2000),
                    tokens_used=random.randint(100, 1000),
                    cost_usd=Decimal(str(random.uniform(0.001, 0.01))),
                    success=success,
                    error_message=None if success else "Timeout error",
                    client_id=client.id,
                    execution_date=exec_date
                )
                history_records.append(record)
    
    session.add_all(history_records)
    await session.commit()
    
    print(f"✅ Created {len(history_records)} agent execution records")
    return history_records


async def create_ab_test_data(session: AsyncSession, client: Client):
    """Create A/B test data."""
    
    print("Creating A/B test data...")
    
    # Create A/B test campaigns
    test_campaigns = []
    
    # Test 1: Creative A/B Test
    test1 = ABTestCampaign(
        id=str(uuid.uuid4()),
        client_id=client.id,
        test_name="Creative Format Test - Image vs Video",
        description="Testing image ads vs video ads for summer collection",
        variant_a_name="Image Ads",
        variant_a_description="Static image creative with product focus",
        variant_b_name="Video Ads",
        variant_b_description="15-second video showcasing product features",
        metric_to_optimize="roas",
        test_duration_days=14,
        statistical_significance=0.95,
        status="completed",
        start_date=date.today() - timedelta(days=21),
        end_date=date.today() - timedelta(days=7),
        winner="variant_b",
        confidence=0.92
    )
    test_campaigns.append(test1)
    
    # Test 2: Bid Strategy A/B Test
    test2 = ABTestCampaign(
        id=str(uuid.uuid4()),
        client_id=client.id,
        test_name="Bid Strategy Test - Manual vs Automated",
        description="Testing manual bid management vs automated bidding",
        variant_a_name="Manual Bidding",
        variant_a_description="Manual bid adjustments based on daily reviews",
        variant_b_name="Automated Bidding",
        variant_b_description="AI-powered automated bid optimization",
        metric_to_optimize="cpa",
        test_duration_days=14,
        statistical_significance=0.95,
        status="completed",
        start_date=date.today() - timedelta(days=28),
        end_date=date.today() - timedelta(days=14),
        winner="variant_b",
        confidence=0.88
    )
    test_campaigns.append(test2)
    
    # Test 3: Running test
    test3 = ABTestCampaign(
        id=str(uuid.uuid4()),
        client_id=client.id,
        test_name="Audience Test - Fitness Enthusiasts vs General",
        description="Testing fitness enthusiast audience vs general audience",
        variant_a_name="Fitness Enthusiasts",
        variant_a_description="Target users with fitness interests",
        variant_b_name="General Audience",
        variant_b_description="Broader audience with general interests",
        metric_to_optimize="conversions",
        test_duration_days=14,
        statistical_significance=0.95,
        status="running",
        start_date=date.today() - timedelta(days=7),
        end_date=date.today() + timedelta(days=7),
        winner=None,
        confidence=None
    )
    test_campaigns.append(test3)
    
    session.add_all(test_campaigns)
    await session.flush()
    
    # Create test results for completed tests
    result_records = []
    
    # Test 1 results
    for day in range(14):
        result_date = test1.start_date + timedelta(days=day)
        
        # Variant A (Image)
        result_records.append(ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test1.id,
            variant="variant_a",
            result_date=result_date,
            impressions=random.randint(40000, 60000),
            clicks=random.randint(1200, 1800),
            conversions=random.randint(30, 50),
            spend=Decimal(str(random.uniform(300, 450))),
            revenue=Decimal(str(random.uniform(600, 900)))
        ))
        
        # Variant B (Video) - better performance
        result_records.append(ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test1.id,
            variant="variant_b",
            result_date=result_date,
            impressions=random.randint(45000, 65000),
            clicks=random.randint(1500, 2200),
            conversions=random.randint(45, 70),
            spend=Decimal(str(random.uniform(350, 500))),
            revenue=Decimal(str(random.uniform(900, 1350)))
        ))
    
    # Test 2 results
    for day in range(14):
        result_date = test2.start_date + timedelta(days=day)
        
        # Variant A (Manual)
        result_records.append(ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test2.id,
            variant="variant_a",
            result_date=result_date,
            impressions=random.randint(50000, 70000),
            clicks=random.randint(1500, 2100),
            conversions=random.randint(40, 60),
            spend=Decimal(str(random.uniform(350, 500))),
            revenue=Decimal(str(random.uniform(700, 1050)))
        ))
        
        # Variant B (Automated) - better performance
        result_records.append(ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test2.id,
            variant="variant_b",
            result_date=result_date,
            impressions=random.randint(52000, 72000),
            clicks=random.randint(1600, 2300),
            conversions=random.randint(50, 75),
            spend=Decimal(str(random.uniform(340, 480))),
            revenue=Decimal(str(random.uniform(850, 1275)))
        ))
    
    # Test 3 results (partial - running test)
    for day in range(7):
        result_date = test3.start_date + timedelta(days=day)
        
        result_records.append(ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test3.id,
            variant="variant_a",
            result_date=result_date,
            impressions=random.randint(30000, 45000),
            clicks=random.randint(900, 1350),
            conversions=random.randint(25, 40),
            spend=Decimal(str(random.uniform(250, 375))),
            revenue=Decimal(str(random.uniform(500, 750)))
        ))
        
        result_records.append(ABTestResult(
            id=str(uuid.uuid4()),
            test_id=test3.id,
            variant="variant_b",
            result_date=result_date,
            impressions=random.randint(35000, 50000),
            clicks=random.randint(1050, 1500),
            conversions=random.randint(30, 45),
            spend=Decimal(str(random.uniform(280, 400))),
            revenue=Decimal(str(random.uniform(560, 840)))
        ))
    
    session.add_all(result_records)
    await session.commit()
    
    print(f"✅ Created {len(test_campaigns)} A/B tests with {len(result_records)} result records")
    return test_campaigns, result_records


async def create_content_performance_by_channel(session: AsyncSession, client: Client):
    """Create content performance by channel data."""
    
    print("Creating content performance by channel...")
    
    # Get content briefs
    content_result = await session.execute(
        select(ContentBrief).limit(5)
    )
    content_items = content_result.scalars().all()
    
    if not content_items:
        # Create sample content briefs
        for i in range(5):
            content = ContentBrief(
                id=str(uuid.uuid4()),
                client_id=client.id,
                title=f"Content Brief {i+1}",
                content_type="social_media",
                platform="meta",
                status="approved",
                brief_data={"topic": "gymshark fitness", "format": "video"}
            )
            session.add(content)
        await session.flush()
        
        content_result = await session.execute(
            select(ContentBrief).limit(5)
        )
        content_items = content_result.scalars().all()
    
    platforms = ["meta", "google", "tiktok", "microsoft"]
    
    performance_records = []
    
    # Create 30 days of content performance data
    for day in range(30):
        perf_date = date.today() - timedelta(days=day)
        
        for content in content_items:
            for platform in platforms:
                impressions = random.randint(10000, 50000)
                clicks = random.randint(300, 1500)
                engagements = random.randint(500, 2000)
                conversions = random.randint(10, 50)
                spend = Decimal(str(random.uniform(50, 200)))
                revenue = Decimal(str(spend * random.uniform(2.0, 4.0)))
                
                record = ContentPerformanceByChannel(
                    id=str(uuid.uuid4()),
                    content_id=content.id,
                    platform=platform,
                    impressions=impressions,
                    clicks=clicks,
                    engagements=engagements,
                    conversions=conversions,
                    spend=spend,
                    revenue=revenue,
                    likes=random.randint(100, 500) if platform in ["meta", "tiktok"] else None,
                    shares=random.randint(20, 100) if platform in ["meta", "tiktok"] else None,
                    comments=random.randint(30, 150) if platform in ["meta", "tiktok"] else None,
                    video_views=random.randint(5000, 20000) if platform == "tiktok" else None,
                    audience_age_distribution={
                        "18-24": random.randint(20, 40),
                        "25-34": random.randint(30, 50),
                        "35-44": random.randint(10, 25),
                        "45+": random.randint(0, 15)
                    },
                    audience_gender_distribution={
                        "male": random.randint(40, 60),
                        "female": random.randint(40, 60)
                    },
                    audience_location_distribution={
                        "US": random.randint(30, 50),
                        "UK": random.randint(20, 35),
                        "Germany": random.randint(10, 20),
                        "Other": random.randint(5, 15)
                    },
                    performance_date=perf_date
                )
                performance_records.append(record)
    
    session.add_all(performance_records)
    await session.commit()
    
    print(f"✅ Created {len(performance_records)} content performance records")
    return performance_records


async def main():
    """Main function to populate comprehensive demo data."""
    
    async with get_async_session() as session:
        # Get Gymshark client
        client_result = await session.execute(
            select(Client).where(Client.name == "Gymshark")
        )
        client = client_result.scalar_one_or_none()
        
        if not client:
            print("❌ Gymshark client not found. Run demo_data.py first.")
            return
        
        print("=" * 80)
        print("COMPREHENSIVE DEMO DATA SETUP")
        print("=" * 80)
        print()
        
        # Create historical campaigns
        historical_campaigns = await create_historical_campaigns(session, client)
        
        # Create model performance data
        model_performance = await create_model_performance_data(session, client)
        
        # Create keyword performance data
        keyword_performance = await create_keyword_performance_data(session, client)
        
        # Create agent execution history
        agent_history = await create_agent_execution_history(session, client)
        
        # Create A/B test data
        ab_tests, ab_results = await create_ab_test_data(session, client)
        
        # Create content performance by channel
        content_performance = await create_content_performance_by_channel(session, client)
        
        print()
        print("=" * 80)
        print("DEMO DATA SETUP COMPLETE")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  - Historical campaigns: {len(historical_campaigns)}")
        print(f"  - Model performance records: {len(model_performance)}")
        print(f"  - Keyword performance records: {len(keyword_performance)}")
        print(f"  - Agent execution records: {len(agent_history)}")
        print(f"  - A/B tests: {len(ab_tests)}")
        print(f"  - A/B test results: {len(ab_results)}")
        print(f"  - Content performance records: {len(content_performance)}")
        print()


if __name__ == "__main__":
    asyncio.run(main())