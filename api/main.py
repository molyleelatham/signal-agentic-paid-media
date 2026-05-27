"""
Main API application for SIGNAL platform.

This is the central FastAPI application that provides endpoints for:
- Trading operations
- Intelligence analysis
- Agent interactions
- Token operations
- Analytics and monitoring
"""
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from shared.utils.settings import settings
from shared.agents.overmind_integration import OvermindTracer
from services.agents import OrchestrationAgent
from services.platform_integration import ThradAuctionIntegrator
from services.trading.bid_discovery import BidDiscoveryEngine
from services.analytics.asymmetric_pnl import AttentionTokenCalculator
from api.routes.demo import router as demo_router


# Pydantic models for API requests/responses
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: dict


class TradingRequest(BaseModel):
    """Request for trading decision."""
    auction_context: dict
    campaign_context: dict
    intelligence_data: dict
    performance_history: Optional[List[dict]] = None


class TradingResponse(BaseModel):
    """Response from trading decision."""
    final_bid: float
    bid_confidence: float
    reasoning: str
    market_insights_count: int
    agents_executed: List[str]
    decision_source: str


class ContentGenerationRequest(BaseModel):
    """Request for content brief generation."""
    gap_topics: List[dict]
    campaign_context: dict
    platform: str


class TokenBalanceResponse(BaseModel):
    """Response for token balance."""
    user_id: str
    balance: float
    staked: float
    available: float


class MarketAnalysisRequest(BaseModel):
    """Request for market analysis."""
    intelligence_data: dict
    campaign_context: dict
    historical_analysis: Optional[List[dict]] = None


class ThradAuctionRequest(BaseModel):
    """Request for Thrad auction."""
    user_id: str
    chat_id: str
    messages: List[dict]
    request_type: str = "contextual"
    ad_formats: Optional[List[str]] = None
    config: Optional[dict] = None
    user_metadata: Optional[dict] = None
    campaign_context: Optional[dict] = None


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Initialize Overmind tracer
    overmind_tracer = OvermindTracer(
        api_key=settings.overmind_api_key,
        project_id=settings.overmind_project_id
    )
    
    # Initialize orchestration agent
    orchestration_agent = OrchestrationAgent(
        overmind_tracer=overmind_tracer
    )
    
    # Initialize Thrad auction integrator
    thrad_auction = ThradAuctionIntegrator(
        api_key=settings.thrad_api_key
    )
    
    # Initialize trading engine
    bid_discovery = BidDiscoveryEngine()
    
    # Initialize token calculator
    token_calculator = AttentionTokenCalculator()
    
    # Store in app state
    app.state.overmind_tracer = overmind_tracer
    app.state.orchestration_agent = orchestration_agent
    app.state.thrad_auction = thrad_auction
    app.state.bid_discovery = bid_discovery
    app.state.token_calculator = token_calculator
    
    yield
    
    # Cleanup
    # Close any connections if needed


# Create FastAPI app
app = FastAPI(
    title="SIGNAL Platform API",
    description="Autonomous Media Trading Platform with AI Agents",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include demo router
app.include_router(demo_router)


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "overmind": "configured" if settings.overmind_api_key else "not_configured",
            "tavily": "configured" if settings.tavily_api_key else "not_configured",
            "thrad": "configured" if settings.thrad_api_key else "not_configured"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "SIGNAL Platform API",
        "status": "running",
        "version": "0.1.0",
        "documentation": "/docs"
    }


# Trading endpoints
@app.post("/api/v1/trading/decide", response_model=TradingResponse)
async def make_trading_decision(request: TradingRequest):
    """
    Make a trading decision using AI agents and algorithmic components.
    
    This endpoint orchestrates the full trading decision process:
    1. Market analysis
    2. Algorithmic bid calculation
    3. Agent-based strategic adjustments
    4. Final decision with reasoning
    """
    try:
        decision = await app.state.orchestration_agent.orchestrate_trading_decision(
            auction_context=request.auction_context,
            campaign_context=request.campaign_context,
            intelligence_data=request.intelligence_data,
            performance_history=request.performance_history or []
        )
        
        return TradingResponse(
            final_bid=decision["final_bid"],
            bid_confidence=decision["bid_confidence"],
            reasoning=decision["bid_reasoning"],
            market_insights_count=decision["market_insights_count"],
            agents_executed=decision["agents_executed"],
            decision_source=decision["decision_source"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trading decision failed: {str(e)}"
        )


# Content generation endpoints
@app.post("/api/v1/content/generate-briefs")
async def generate_content_briefs(request: ContentGenerationRequest):
    """
    Generate content briefs for multiple gap topics.
    
    Uses the ContentBriefAgent to create strategic content briefs
    based on gap analysis from BERTopic.
    """
    try:
        result = await app.state.orchestration_agent.orchestrate_content_generation(
            gap_topics=request.gap_topics,
            campaign_context=request.campaign_context,
            platform=request.platform
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


# Market analysis endpoints
@app.post("/api/v1/intelligence/analyze")
async def analyze_market(request: MarketAnalysisRequest):
    """
    Analyze market intelligence and generate strategic insights.
    
    Uses the MarketAnalysisAgent to transform raw intelligence into
    actionable strategic insights.
    """
    try:
        insights = await app.state.orchestration_agent.market_agent.analyze_market_intelligence(
            intelligence_data=request.intelligence_data,
            campaign_context=request.campaign_context,
            historical_analysis=request.historical_analysis or []
        )
        
        return {
            "insights": [
                {
                    "insight_type": insight.insight_type,
                    "summary": insight.summary,
                    "confidence": insight.confidence,
                    "actionability": insight.actionability,
                    "urgency": insight.urgency
                }
                for insight in insights
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market analysis failed: {str(e)}"
        )


# Token endpoints
@app.get("/api/v1/tokens/balance/{user_id}", response_model=TokenBalanceResponse)
async def get_token_balance(user_id: str):
    """
    Get token balance for a user.
    
    Returns the user's current token balance, including staked and available tokens.
    """
    try:
        # This would query the database in production
        # For now, return a mock response
        return TokenBalanceResponse(
            user_id=user_id,
            balance=1234.56789012,
            staked=500.0,
            available=734.56789012
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token balance: {str(e)}"
        )


@app.post("/api/v1/tokens/calculate-reward")
async def calculate_token_reward(performance_data: dict):
    """
    Calculate token reward based on performance data.
    
    Uses the AttentionTokenCalculator to compute token rewards/penalties
    based on P&L performance.
    """
    try:
        result = app.state.token_calculator.calculate_complete_token_transaction(
            performance_data=performance_data
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token calculation failed: {str(e)}"
        )


# Agent endpoints
@app.get("/api/v1/agents/status")
async def get_agents_status():
    """
    Get status of all AI agents.
    
    Returns information about available agents and their status.
    """
    return {
        "agents": {
            "orchestration_agent": "active",
            "market_analysis_agent": "active",
            "content_brief_agent": "active",
            "bid_strategy_agent": "active",
            "creative_optimization_agent": "active"
        },
        "overmind_integration": "enabled" if settings.overmind_api_key else "disabled",
        "total_agents": 5
    }


@app.post("/api/v1/agents/optimize-daily")
async def run_daily_optimization(campaign_id: str, performance_data: dict, intelligence_data: dict):
    """
    Run daily optimization routine using all agents.
    
    Orchestrates market analysis, creative optimization, and bid strategy
    optimization for comprehensive daily improvements.
    """
    try:
        optimization = await app.state.orchestration_agent.orchestrate_daily_optimization(
            campaign_id=campaign_id,
            performance_data=performance_data,
            intelligence_data=intelligence_data,
            market_conditions={}
        )
        
        return optimization
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Daily optimization failed: {str(e)}"
        )


# Analytics endpoints
@app.get("/api/v1/analytics/performance/{position_id}")
async def get_position_performance(position_id: str):
    """
    Get performance analytics for a media position.
    
    Returns detailed performance metrics including P&L scores,
    efficiency ratios, and token rewards.
    """
    try:
        # This would query the database in production
        return {
            "position_id": position_id,
            "performance_summary": {
                "impressions": 10000,
                "clicks": 500,
                "conversions": 25,
                "ctr": 0.05,
                "conversion_rate": 0.05
            },
            "pnl_score": {
                "gross_revenue": 2500.0,
                "attention_waste_cost": 800.0,
                "net_pnl": 900.0,
                "efficiency_ratio": 3.125
            },
            "token_rewards": {
                "reward": 45.0,
                "penalty": 0.0
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance data: {str(e)}"
        )


# Thrad Auction endpoints
@app.post("/api/v1/thrad/auction")
async def request_thrad_auction(request: ThradAuctionRequest):
    """
    Request ad from Thrad's multi-bidder auction.
    
    This is the main endpoint for ad serving, using Thrad's auction system
    with AI agent strategic recommendations.
    """
    try:
        # Update orchestration agent with Thrad auction integrator
        app.state.orchestration_agent.thrad_auction = app.state.thrad_auction
        
        # Orchestrate auction with agent enhancements
        result = await app.state.orchestration_agent.orchestrate_thrad_auction(
            user_id=request.user_id,
            conversation_context={
                "chat_id": request.chat_id,
                "messages": request.messages,
                "intelligence_data": request.config.get("intelligence_data", {}) if request.config else {},
                "historical_analysis": request.config.get("historical_analysis", []) if request.config else []
            },
            campaign_context=request.campaign_context
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Thrad auction failed: {str(e)}"
        )


@app.post("/api/v1/thrad/contextual-ad")
async def request_contextual_ad(
    user_id: str,
    chat_id: str,
    messages: List[dict],
    ad_formats: List[str] = None,
    config: dict = None
):
    """
    Request a contextual ad (in-chat) from Thrad.
    
    Simplified endpoint for contextual ad requests without agent orchestration.
    """
    try:
        from services.platform_integration import ThradBidAPIClient
        
        client = ThradBidAPIClient()
        
        response = await client.request_contextual_ad(
            user_id=user_id,
            chat_id=chat_id,
            messages=messages,
            ad_formats=ad_formats,
            config=config
        )
        
        await client.close()
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Contextual ad request failed: {str(e)}"
        )


@app.post("/api/v1/thrad/opener-ad")
async def request_opener_ad(
    user_id: str,
    ad_formats: List[str] = None,
    config: dict = None
):
    """
    Request an opener ad (pre-chat) from Thrad.
    
    Simplified endpoint for opener ad requests without agent orchestration.
    """
    try:
        from services.platform_integration import ThradBidAPIClient
        
        client = ThradBidAPIClient()
        
        response = await client.request_opener_ad(
            user_id=user_id,
            ad_formats=ad_formats,
            config=config
        )
        
        await client.close()
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Opener ad request failed: {str(e)}"
        )


# Intelligence endpoints
@app.post("/api/v1/intelligence/trigger-scan")
async def trigger_intelligence_scan(category: str, competitors: Optional[List[str]] = None):
    """
    Trigger Tavily intelligence scan.
    
    Initiates a comprehensive market scan using Tavily's search capabilities.
    """
    try:
        from services.intelligence.tavily_client import TavilyClient, MarketScanner
        
        tavily_client = TavilyClient()
        scanner = MarketScanner(tavily_client)
        
        scan_results = await scanner.scan_market(
            category=category,
            competitors=competitors or [],
            scan_depth="advanced"
        )
        
        await tavily_client.close()
        
        return scan_results
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence scan failed: {str(e)}"
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return {
        "error": "Internal server error",
        "detail": str(exc),
        "type": type(exc).__name__
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )