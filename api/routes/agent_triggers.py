"""
Agent Trigger API Routes

Provides endpoints for triggering all agents with reactive updates.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from services.common import agent_trigger_service

router = APIRouter(tags=["agent-triggers"])


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify router is working."""
    return {"status": "ok", "message": "Agent triggers router is working"}


# ============ REQUEST MODELS ============

class BidOptimizeRequest(BaseModel):
    keyword: str
    current_bid: float
    platform: str = "google"
    campaign_id: Optional[str] = None


class ContentGenerateRequest(BaseModel):
    gap_topic: str
    gap_score: float
    platform: str = "meta"
    business_goal: str = "performance"


class CreativeOptimizeRequest(BaseModel):
    creative_id: str
    creative_type: str
    platform: str = "meta"


class MarketAnalyzeRequest(BaseModel):
    query: str
    time_range: str = "week"
    competitors: Optional[List[str]] = None


class KeywordClassifyRequest(BaseModel):
    query: str
    use_disbert: bool = True


class TavilyResearchRequest(BaseModel):
    query: str
    max_results: int = 15
    extract_keywords: bool = True


class OrchestrateRequest(BaseModel):
    task_type: str
    context: Dict
    required_agents: List[str]


class BulkTriggerRequest(BaseModel):
    triggers: List[Dict]  # List of trigger requests
    parallel: bool = True


# ============ ENDPOINTS ============

@router.post("/trigger/bid-optimize")
async def trigger_bid_optimize(request: BidOptimizeRequest):
    """
    Trigger bid optimization agent.
    
    This endpoint:
    - Optimizes bid for a keyword
    - Logs to agent logger and execution logger
    - Returns recommendation with confidence
    """
    result = await agent_trigger_service.trigger_bid_optimize(
        keyword=request.keyword,
        current_bid=request.current_bid,
        platform=request.platform,
        campaign_id=request.campaign_id
    )
    
    return result.to_dict()


@router.post("/trigger/content-generate")
async def trigger_content_generate(request: ContentGenerateRequest):
    """
    Trigger content brief generation agent.
    
    This endpoint:
    - Generates content brief for a gap topic
    - Logs to agent logger and execution logger
    - Returns brief with differentiation score
    """
    result = await agent_trigger_service.trigger_content_generate(
        gap_topic=request.gap_topic,
        gap_score=request.gap_score,
        platform=request.platform,
        business_goal=request.business_goal
    )
    
    return result.to_dict()


@router.post("/trigger/creative-optimize")
async def trigger_creative_optimize(request: CreativeOptimizeRequest):
    """
    Trigger creative optimization agent.
    
    This endpoint:
    - Analyzes creative performance
    - Generates optimization suggestions
    - Logs to agent logger and execution logger
    - Returns suggestions with predicted lift
    """
    result = await agent_trigger_service.trigger_creative_optimize(
        creative_id=request.creative_id,
        creative_type=request.creative_type,
        platform=request.platform
    )
    
    return result.to_dict()


@router.post("/trigger/market-analyze")
async def trigger_market_analyze(request: MarketAnalyzeRequest):
    """
    Trigger market analysis agent.
    
    This endpoint:
    - Analyzes market intelligence
    - Generates insights
    - Logs to agent logger and execution logger
    - Returns insights with confidence
    """
    result = await agent_trigger_service.trigger_market_analyze(
        query=request.query,
        time_range=request.time_range,
        competitors=request.competitors
    )
    
    return result.to_dict()


@router.post("/trigger/keyword-classify")
async def trigger_keyword_classify(request: KeywordClassifyRequest):
    """
    Trigger keyword classification with DisBERT.
    
    This endpoint:
    - Classifies keyword using DisBERT
    - Logs to campaign keyword logger
    - Logs to execution logger
    - Returns classification with strategy
    """
    result = await agent_trigger_service.trigger_keyword_classify(
        query=request.query,
        use_disbert=request.use_disbert
    )
    
    return result.to_dict()


@router.post("/trigger/tavily-research")
async def trigger_tavily_research(request: TavilyResearchRequest):
    """
    Trigger Tavily research for trending topics.
    
    This endpoint:
    - Performs Tavily web research
    - Converts results to trending topics format
    - Logs to agent logger and execution logger
    - Returns trending topics for Section A
    """
    result = await agent_trigger_service.trigger_tavily_research(
        query=request.query,
        max_results=request.max_results,
        extract_keywords=request.extract_keywords
    )
    
    return result.to_dict()


@router.post("/trigger/orchestrate")
async def trigger_orchestrate(request: OrchestrateRequest):
    """
    Trigger orchestration agent to coordinate multiple agents.
    
    This endpoint:
    - Coordinates multiple agents
    - Logs to agent logger and execution logger
    - Returns combined results
    """
    result = await agent_trigger_service.trigger_orchestrate(
        task_type=request.task_type,
        context=request.context,
        required_agents=request.required_agents
    )
    
    return result.to_dict()


@router.post("/trigger/bulk")
async def trigger_bulk(request: BulkTriggerRequest):
    """
    Trigger multiple agents in bulk.
    
    This endpoint:
    - Triggers multiple agents
    - Can run in parallel or sequentially
    - Returns all results
    """
    results = []
    
    if request.parallel:
        # Run all triggers in parallel
        import asyncio
        
        tasks = []
        for trigger_data in request.triggers:
            trigger_type = trigger_data.get("type")
            
            if trigger_type == "bid_optimize":
                task = agent_trigger_service.trigger_bid_optimize(**trigger_data.get("params", {}))
            elif trigger_type == "content_generate":
                task = agent_trigger_service.trigger_content_generate(**trigger_data.get("params", {}))
            elif trigger_type == "creative_optimize":
                task = agent_trigger_service.trigger_creative_optimize(**trigger_data.get("params", {}))
            elif trigger_type == "market_analyze":
                task = agent_trigger_service.trigger_market_analyze(**trigger_data.get("params", {}))
            elif trigger_type == "keyword_classify":
                task = agent_trigger_service.trigger_keyword_classify(**trigger_data.get("params", {}))
            elif trigger_type == "tavily_research":
                task = agent_trigger_service.trigger_tavily_research(**trigger_data.get("params", {}))
            elif trigger_type == "orchestrate":
                task = agent_trigger_service.trigger_orchestrate(**trigger_data.get("params", {}))
            else:
                continue
            
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        # Run sequentially
        for trigger_data in request.triggers:
            trigger_type = trigger_data.get("type")
            
            if trigger_type == "bid_optimize":
                result = await agent_trigger_service.trigger_bid_optimize(**trigger_data.get("params", {}))
            elif trigger_type == "content_generate":
                result = await agent_trigger_service.trigger_content_generate(**trigger_data.get("params", {}))
            elif trigger_type == "creative_optimize":
                result = await agent_trigger_service.trigger_creative_optimize(**trigger_data.get("params", {}))
            elif trigger_type == "market_analyze":
                result = await agent_trigger_service.trigger_market_analyze(**trigger_data.get("params", {}))
            elif trigger_type == "keyword_classify":
                result = await agent_trigger_service.trigger_keyword_classify(**trigger_data.get("params", {}))
            elif trigger_type == "tavily_research":
                result = await agent_trigger_service.trigger_tavily_research(**trigger_data.get("params", {}))
            elif trigger_type == "orchestrate":
                result = await agent_trigger_service.trigger_orchestrate(**trigger_data.get("params", {}))
            else:
                continue
            
            results.append(result)
    
    # Convert results to dicts
    results_dicts = []
    for result in results:
        if isinstance(result, Exception):
            results_dicts.append({
                "success": False,
                "error": str(result)
            })
        else:
            results_dicts.append(result.to_dict())
    
    return {
        "total_triggers": len(request.triggers),
        "successful": sum(1 for r in results_dicts if r.get("success")),
        "failed": sum(1 for r in results_dicts if not r.get("success")),
        "results": results_dicts
    }


@router.get("/trigger/types")
async def list_trigger_types():
    """List all available trigger types."""
    return {
        "trigger_types": [
            {
                "type": "bid_optimize",
                "description": "Optimize bid for a keyword",
                "agent": "bid_strategy_agent",
                "params": {
                    "keyword": "string (required)",
                    "current_bid": "float (required)",
                    "platform": "string (optional, default: google)",
                    "campaign_id": "string (optional)"
                }
            },
            {
                "type": "content_generate",
                "description": "Generate content brief for a gap topic",
                "agent": "content_brief_agent",
                "params": {
                    "gap_topic": "string (required)",
                    "gap_score": "float (required)",
                    "platform": "string (optional, default: meta)",
                    "business_goal": "string (optional, default: performance)"
                }
            },
            {
                "type": "creative_optimize",
                "description": "Optimize creative performance",
                "agent": "creative_optimization_agent",
                "params": {
                    "creative_id": "string (required)",
                    "creative_type": "string (required)",
                    "platform": "string (optional, default: meta)"
                }
            },
            {
                "type": "market_analyze",
                "description": "Analyze market intelligence",
                "agent": "market_analysis_agent",
                "params": {
                    "query": "string (required)",
                    "time_range": "string (optional, default: week)",
                    "competitors": "list of strings (optional)"
                }
            },
            {
                "type": "keyword_classify",
                "description": "Classify keyword with DisBERT",
                "agent": "disbert_classifier",
                "params": {
                    "query": "string (required)",
                    "use_disbert": "boolean (optional, default: true)"
                }
            },
            {
                "type": "tavily_research",
                "description": "Perform Tavily web research for trending topics",
                "agent": "tavily_research",
                "params": {
                    "query": "string (required)",
                    "max_results": "integer (optional, default: 15)",
                    "extract_keywords": "boolean (optional, default: true)"
                }
            },
            {
                "type": "orchestrate",
                "description": "Orchestrate multiple agents",
                "agent": "orchestration_agent",
                "params": {
                    "task_type": "string (required)",
                    "context": "dict (required)",
                    "required_agents": "list of strings (required)"
                }
            }
        ]
    }


@router.get("/trigger/history")
async def get_trigger_history(limit: int = 50):
    """
    Get recent agent trigger history from execution logger.
    
    This provides a unified view of all agent executions.
    """
    from services.common import agent_execution_logger
    
    history = await agent_execution_logger.get_execution_history(limit=limit)
    
    return {
        "limit": limit,
        "count": len(history),
        "executions": [
            {
                "id": exec.id,
                "agent_name": exec.agent_name,
                "agent_type": exec.agent_type,
                "action": exec.action,
                "execution_time_ms": exec.execution_time_ms,
                "tokens_used": exec.tokens_used,
                "cost_usd": float(exec.cost_usd) if exec.cost_usd else 0.0,
                "success": exec.success,
                "error_message": exec.error_message,
                "execution_date": exec.execution_date.isoformat()
            }
            for exec in history
        ]
    }


@router.get("/trigger/stats")
async def get_trigger_stats(days: int = 30):
    """
    Get trigger statistics over time.
    
    This provides metrics on agent performance.
    """
    from services.common import agent_execution_logger
    
    stats = await agent_execution_logger.get_execution_stats(days=days)
    
    return {
        "days": days,
        **stats
    }