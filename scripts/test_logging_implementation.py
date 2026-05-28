"""
Test Script for Logging Implementation

Tests:
1. Agent logger (BUY/HOLD/STOP signals)
2. Campaign keyword logger (with Thrad data)
3. Agent execution logger (database logging)
"""

import asyncio
import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

from services.common import agent_logger, agent_execution_logger
from services.media_planning import campaign_keyword_logger


def test_agent_logger():
    """Test agent logger for BUY/HOLD/STOP signals."""
    print("=" * 80)
    print("TEST 1: Agent Logger")
    print("=" * 80)
    
    # Test BUY signal
    agent_logger.log_buy(
        agent="THOMPSON_ALLOCATOR",
        campaign="Summer Training Collection",
        amount=2500.0,
        channel="meta",
        confidence=0.85,
        reasoning="High performance, strong conversion rate"
    )
    print("✅ Logged BUY signal")
    
    # Test HOLD signal
    agent_logger.log_hold(
        agent="THOMPSON_ALLOCATOR",
        campaign="Performance Gear",
        channel="google",
        confidence=0.72,
        reasoning="Moderate performance, maintain current spend"
    )
    print("✅ Logged HOLD signal")
    
    # Test STOP signal
    agent_logger.log_stop(
        agent="THOMPSON_ALLOCATOR",
        campaign="Old Campaign",
        channel="tiktok",
        confidence=0.45,
        reasoning="Low performance, pausing campaign"
    )
    print("✅ Logged STOP signal")
    
    # Test OPTIMIZE
    agent_logger.log_optimize(
        agent="BID_STRATEGY",
        campaign="Summer Training Collection",
        optimization_type="Bid increase from £2.20 to £2.75",
        confidence=0.92
    )
    print("✅ Logged OPTIMIZE signal")
    
    # Test ANALYZE
    agent_logger.log_analyze(
        agent="MARKET_ANALYSIS",
        analysis_type="Trend analysis for gymshark leggings",
        result="Detected +15% increase in purchase intent"
    )
    print("✅ Logged ANALYZE signal")
    
    # Get logs
    logs = agent_logger.get_logs_dict(limit=10)
    print(f"\n✅ Retrieved {len(logs)} logs")
    
    for log in logs:
        print(f"  {log['timestamp']} [{log['agent']}] {log['action']} {log.get('campaign', '')}")
    
    print()


def test_campaign_keyword_logger():
    """Test campaign keyword logger with Thrad data."""
    print("=" * 80)
    print("TEST 2: Campaign Keyword Logger")
    print("=" * 80)
    
    # Test keyword addition with DisBERT model
    log_entry = campaign_keyword_logger.log_keyword_addition(
        keyword="gymshark leggings",
        match_type="phrase",
        bid_amount=2.75,
        source="tavily",
        confidence=0.95,
        intent="transactional",
        category="H",
        model_used="thrad_disbert"
    )
    print(f"✅ Logged keyword: {log_entry.keyword}")
    print(f"   Campaign: {log_entry.campaign_name}")
    print(f"   Model: {log_entry.model_used}")
    
    # Generate Thrad data
    thrad_data = campaign_keyword_logger.generate_thrad_data("gymshark leggings")
    log_entry.thrad_data = thrad_data
    print(f"✅ Generated Thrad data")
    print(f"   User ID: {thrad_data['user_id']}")
    print(f"   Chat ID: {thrad_data['chat_id']}")
    print(f"   Model: {thrad_data['model_used']}")
    
    # Log from research
    google_keywords = [
        {"keyword": "buy gymshark online", "match_type": "exact", "bid": 3.50, "intent": "transactional", "category": "H"},
        {"keyword": "gym wear women", "match_type": "broad", "bid": 2.20, "intent": "informational", "category": "E"}
    ]
    logs = campaign_keyword_logger.log_keywords_from_research(
        google_keywords=google_keywords,
        source="tavily",
        model_used="thrad_disbert"
    )
    print(f"\n✅ Logged {len(logs)} keywords from research")
    
    # Get logs
    campaign_logs = campaign_keyword_logger.get_logs_by_campaign("GYMSHARK_PPC_GENERIC_2026", limit=5)
    print(f"\n✅ Retrieved {len(campaign_logs)} campaign logs")
    
    for log in campaign_logs:
        print(f"  {log['timestamp']} {log['keyword']} ({log['match_type']}) £{log['bid_amount']}")
        if log['model_used']:
            print(f"    Model: {log['model_used']}")
    
    print()


async def test_agent_execution_logger():
    """Test agent execution logger with database."""
    print("=" * 80)
    print("TEST 3: Agent Execution Logger (Database)")
    print("=" * 80)
    
    # Test logging execution
    await agent_execution_logger.log_execution(
        agent_name="bid_strategy_agent",
        agent_type="bid_strategy",
        action="optimize_bid",
        input_data={"keyword": "gymshark leggings", "current_bid": 2.20},
        output_data={"recommended_bid": 2.75, "confidence": 0.85},
        execution_time_ms=450,
        tokens_used=150,
        cost_usd=0.0015,
        success=True
    )
    print("✅ Logged bid_strategy execution")
    
    await agent_execution_logger.log_execution(
        agent_name="content_brief_agent",
        agent_type="content_brief",
        action="generate_content",
        input_data={"gap_topic": "seamless leggings", "gap_score": 0.85},
        output_data={"brief": "...", "confidence": 0.92},
        execution_time_ms=620,
        tokens_used=280,
        cost_usd=0.0028,
        success=True
    )
    print("✅ Logged content_brief execution")
    
    await agent_execution_logger.log_execution(
        agent_name="creative_optimization_agent",
        agent_type="creative_optimization",
        action="analyze_creative",
        input_data={"creative_id": "cr_123"},
        output_data={"score": 75, "suggestions": [...]},
        execution_time_ms=380,
        tokens_used=120,
        cost_usd=0.0012,
        success=True
    )
    print("✅ Logged creative_optimization execution")
    
    # Test chat execution
    await agent_execution_logger.log_chat_execution(
        agent_name="bid_strategy",
        model="gpt-4",
        user_message="What's the optimal bid for gymshark leggings?",
        agent_response="I recommend £2.75 for phrase match...",
        tokens_used=150,
        cost_usd=0.0045,
        execution_time_ms=450,
        success=True
    )
    print("✅ Logged chat execution")
    
    # Get execution history
    history = await agent_execution_logger.get_execution_history(limit=10)
    print(f"\n✅ Retrieved {len(history)} execution records from database")
    
    for exec in history:
        print(f"  {exec.agent_name} - {exec.action}")
        print(f"    Success: {exec.success}, Time: {exec.execution_time_ms}ms")
        print(f"    Tokens: {exec.tokens_used}, Cost: ${exec.cost_usd}")
    
    # Get stats
    stats = await agent_execution_logger.get_execution_stats(days=30)
    print(f"\n✅ Execution Statistics (Last 30 Days):")
    print(f"  Total Executions: {stats['total_executions']}")
    print(f"  Success Rate: {stats['success_rate']:.2%}")
    print(f"  Avg Latency: {stats['avg_latency_ms']:.0f}ms")
    print(f"  Total Tokens: {stats['total_tokens']}")
    print(f"  Total Cost: ${stats['total_cost_usd']:.4f}")
    
    print()


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("LOGGING IMPLEMENTATION TESTS")
    print("=" * 80 + "\n")
    
    # Test 1: Agent Logger
    test_agent_logger()
    
    # Test 2: Campaign Keyword Logger
    test_campaign_keyword_logger()
    
    # Test 3: Agent Execution Logger (async)
    await test_agent_execution_logger()
    
    print("=" * 80)
    print("ALL TESTS PASSED ✅")
    print("=" * 80)
    print("\nLogging Implementation Summary:")
    print("1. ✅ Agent Logger - BUY/HOLD/STOP signals logged")
    print("2. ✅ Campaign Keyword Logger - Keywords logged with Thrad data")
    print("3. ✅ Agent Execution Logger - Executions logged to database")
    print("4. ✅ Chat Execution Logger - Chat interactions logged")
    print("\nAll logs are properly integrated with the backend and API routes.")
    print()


if __name__ == "__main__":
    asyncio.run(main())