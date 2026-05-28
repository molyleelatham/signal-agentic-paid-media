"""
Test script to verify Overmind SDK integration.

This script tests:
1. Overmind SDK initialization
2. Tracer functionality
3. Agent LLM integration
4. Basic tracing operations
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from shared.agents.overmind_integration import OvermindTracer, BaseAgent
from services.agents.market_analysis_agent import MarketAnalysisAgent


async def test_overmind_initialization():
    """Test Overmind SDK initialization."""
    print("=" * 60)
    print("TEST 1: Overmind SDK Initialization")
    print("=" * 60)
    
    api_key = os.getenv("OVERMIND_API_KEY")
    project_id = os.getenv("OVERMIND_PROJECT_ID", "signal-platform-test")
    
    if not api_key:
        print("❌ OVERMIND_API_KEY not set in environment")
        print("⚠️  Skipping Overmind tests - set OVERMIND_API_KEY to enable")
        return False
    
    tracer = OvermindTracer(api_key=api_key, project_id=project_id)
    
    if tracer.initialized:
        print("✅ Overmind SDK initialized successfully")
        print(f"   Service: {tracer.project_id}")
        print(f"   Tracer available: {tracer.tracer is not None}")
        return True
    else:
        print("❌ Overmind SDK initialization failed")
        return False


async def test_tracer_functionality():
    """Test basic tracer functionality."""
    print("\n" + "=" * 60)
    print("TEST 2: Tracer Functionality")
    print("=" * 60)
    
    api_key = os.getenv("OVERMIND_API_KEY")
    if not api_key:
        print("⚠️  Skipping - Overmind not initialized")
        return False
    
    tracer = OvermindTracer(api_key=api_key)
    
    if not tracer.initialized:
        print("❌ Tracer not initialized")
        return False
    
    # Test custom tags
    try:
        tracer.set_custom_tag("test_tag", "test_value")
        print("✅ Custom tags work")
    except Exception as e:
        print(f"❌ Custom tags failed: {e}")
        return False
    
    # Test user context
    try:
        tracer.set_user_context("test_user_123", {"role": "admin", "tier": "premium"})
        print("✅ User context works")
    except Exception as e:
        print(f"❌ User context failed: {e}")
        return False
    
    # Test outcome logging
    try:
        tracer.log_outcome("trace_123", "test_metric", 0.85, {"metadata": "test"})
        print("✅ Outcome logging works")
    except Exception as e:
        print(f"❌ Outcome logging failed: {e}")
        return False
    
    # Test span creation
    try:
        with tracer.start_span("test_span"):
            pass
        print("✅ Span creation works")
    except Exception as e:
        print(f"❌ Span creation failed: {e}")
        return False
    
    return True


async def test_agent_llm_integration():
    """Test agent LLM integration with Overmind."""
    print("\n" + "=" * 60)
    print("TEST 3: Agent LLM Integration")
    print("=" * 60)
    
    api_key = os.getenv("OVERMIND_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not set - will use fallback responses")
    
    tracer = OvermindTracer(api_key=api_key) if api_key else None
    
    try:
        agent = MarketAnalysisAgent(overmind_tracer=tracer)
        print(f"✅ Agent created: {agent.name}")
        print(f"   Overmind initialized: {agent.overmind_tracer.initialized if agent.overmind_tracer else False}")
        print(f"   LLM client available: {agent.llm_client is not None}")
        
        # Test basic thinking
        response = await agent.think(
            prompt="What are the key trends in sustainable fashion?",
            context={"industry": "fashion", "focus": "sustainability"}
        )
        print(f"✅ Agent thinking works")
        print(f"   Response length: {len(response)} characters")
        print(f"   Response preview: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent LLM integration failed: {e}")
        return False


async def test_market_analysis_tracing():
    """Test market analysis with Overmind tracing."""
    print("\n" + "=" * 60)
    print("TEST 4: Market Analysis with Tracing")
    print("=" * 60)
    
    api_key = os.getenv("OVERMIND_API_KEY")
    if not api_key:
        print("⚠️  Skipping - Overmind not initialized")
        return False
    
    tracer = OvermindTracer(api_key=api_key)
    
    if not tracer.initialized:
        print("❌ Tracer not initialized")
        return False
    
    try:
        agent = MarketAnalysisAgent(overmind_tracer=tracer)
        
        # Sample intelligence data
        intelligence_data = {
            "tavily_search": {
                "query": "sustainable fashion trends 2024",
                "results": [
                    {"title": "E-friendly materials surge", "url": "example.com"},
                    {"title": "Gen Z prefers sustainable brands", "url": "example2.com"}
                ]
            },
            "topic_clusters": {
                "sustainable_fashion": {"volume": 125000, "growth": 0.23}
            }
        }
        
        campaign_context = {
            "client": "Acme Fashion",
            "goal": "brand awareness",
            "target_audience": "millennials"
        }
        
        # Run analysis with tracing
        insights = await agent.analyze_market_intelligence(
            intelligence_data=intelligence_data,
            campaign_context=campaign_context,
            historical_analysis=[]
        )
        
        print(f"✅ Market analysis completed with tracing")
        print(f"   Insights generated: {len(insights)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Market analysis tracing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🧪 Overmind Integration Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Initialization
    results["initialization"] = await test_overmind_initialization()
    
    # Only run other tests if initialization succeeded
    if results["initialization"]:
        # Test 2: Tracer functionality
        results["tracer"] = await test_tracer_functionality()
        
        # Test 3: Agent LLM integration
        results["agent_llm"] = await test_agent_llm_integration()
        
        # Test 4: Market analysis tracing
        results["market_analysis"] = await test_market_analysis_tracing()
    else:
        print("\n⚠️  Skipping remaining tests due to initialization failure")
        results["tracer"] = None
        results["agent_llm"] = None
        results["market_analysis"] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{test_name:20s}: {status}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed or skipped")


if __name__ == "__main__":
    asyncio.run(main())