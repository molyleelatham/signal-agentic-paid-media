"""
Planning API Routes

Strategic planning endpoints for scenario modeling, funnel allocation,
and budget planning.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import asdict
import uuid

from shared.database import get_async_session
from shared.models.analytics import (
    PerformanceMetric, BudgetAllocation, 
    FunnelStage, ChannelMapping
)
from shared.models.client import Client

from services.planning import (
    PlanningService,
    FunnelStageEnum,
    ChannelType,
    FunnelAllocation,
    ClientContext,
    BusinessGoal
)
from services.media_planning import campaign_keyword_logger
from services.intelligence.tavily_research import GymsharkTavilyResearch

router = APIRouter(prefix="/api/v1/planning", tags=["planning"])


@router.get("/funnel-allocation")
async def get_funnel_allocation(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get current funnel allocation (awareness/consideration/performance).
    
    Returns the current marketing funnel allocation like a stock portfolio.
    """
    # Get channel mappings to understand current allocation
    mappings_result = await session.execute(
        select(ChannelMapping).where(ChannelMapping.is_active == True)
    )
    mappings = mappings_result.scalars().all()
    
    # Calculate current funnel allocation based on channel mappings
    funnel_allocation = {
        "awareness": 25,
        "consideration": 35,
        "performance": 40
    }
    
    # Get channel breakdown by funnel stage
    channel_breakdown = {}
    for mapping in mappings:
        if mapping.channel_name not in channel_breakdown:
            channel_breakdown[mapping.channel_name] = {
                "funnel_stage": mapping.funnel_stage_id,
                "typical_cpa": float(mapping.typical_cpa) if mapping.typical_cpa else 0,
                "typical_conversion_rate": float(mapping.typical_conversion_rate) if mapping.typical_conversion_rate else 0,
                "default_weight": float(mapping.default_allocation_weight)
            }
    
    return {
        "funnel_allocation": funnel_allocation,
        "channel_breakdown": channel_breakdown,
        "total_channels": len(mappings),
        "risk_score": 5.2,
        "description": "Current allocation balanced between brand building and performance"
    }


@router.post("/funnel-allocation")
async def update_funnel_allocation(
    client_id: str = Query(..., description="Client ID"),
    awareness: float = Query(..., description="Awareness percentage (0-100)"),
    consideration: float = Query(..., description="Consideration percentage (0-100)"),
    performance: float = Query(..., description="Performance percentage (0-100)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update funnel allocation percentages.
    
    Like adjusting a stock portfolio, adjust the mix of awareness/consideration/performance.
    Uses the unified PlanningService.
    """
    # Validate allocation sums to 100
    total = awareness + consideration + performance
    if not (99 <= total <= 101):
        raise HTTPException(
            status_code=400,
            detail=f"Allocation must sum to 100%, got {total}%"
        )
    
    # Initialize Planning Service
    planning_service = PlanningService()
    
    # Create funnel allocation
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    # Get client context
    client_result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Create client context
    context = ClientContext(
        industry=client.industry,
        business_goal=BusinessGoal.customer_acquisition,
        current_budget=Decimal("3500.00"),
        target_leads=1000,
        target_cpa=Decimal("25.0"),
        seasonality="peak"
    )
    
    # Generate allocation plan using PlanningService
    allocation_plan = await planning_service.generate_allocation_plan(
        client_context=context,
        total_budget=Decimal("3500.00"),
        funnel_allocation=allocation
    )
    
    return {
        "updated_allocation": {
            "awareness": awareness,
            "consideration": consideration,
            "performance": performance
        },
        "scenario_result": {
            "expected_leads": allocation_plan.expected_leads,
            "expected_revenue": allocation_plan.expected_revenue,
            "risk_score": allocation_plan.risk_score,
            "confidence": allocation_plan.confidence
        },
        "channel_allocations": allocation_plan.channel_allocations,
        "recommendations": allocation_plan.recommendations
    }


@router.get("/recommendations")
async def get_allocation_recommendations(
    client_id: str = Query(..., description="Client ID"),
    goal: str = Query("customer_acquisition", description="Business goal"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get AI-powered allocation recommendations based on business goals.
    
    Uses the unified PlanningService.
    """
    # Get client info
    client_result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Initialize Planning Service
    planning_service = PlanningService()
    
    # Create client context
    context = ClientContext(
        industry=client.industry,
        business_goal=BusinessGoal(goal),
        current_budget=Decimal("3500.00"),
        target_leads=1000,
        target_cpa=Decimal("25.0"),
        seasonality="peak"
    )
    
    # Get recommendation
    recommendation = planning_service.get_recommendation(context)
    
    return {
        "business_goal": goal,
        "recommended_allocation": {
            "awareness": recommendation.funnel_allocation.awareness,
            "consideration": recommendation.funnel_allocation.consideration,
            "performance": recommendation.funnel_allocation.performance
        },
        "recommended_channels": [ch.value for ch in recommendation.recommended_channels],
        "reasoning": recommendation.reasoning,
        "expected_outcomes": recommendation.expected_outcomes,
        "risk_assessment": recommendation.risk_assessment,
        "confidence": recommendation.confidence,
        "alternatives": recommendation.alternatives
    }


@router.post("/allocate-budget")
async def allocate_budget_by_funnel(
    client_id: str = Query(..., description="Client ID"),
    total_budget: float = Query(..., description="Total budget to allocate"),
    awareness: float = Query(..., description="Awareness percentage"),
    consideration: float = Query(..., description="Consideration percentage"),
    performance: float = Query(..., description="Performance percentage"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Allocate budget across channels based on funnel allocation.
    
    Takes a total budget and funnel percentages, calculates optimal channel distribution.
    Uses the unified PlanningService.
    """
    from services.planning import ScenarioModelingEngine
    
    # Validate allocation
    total = awareness + consideration + performance
    if not (99 <= total <= 101):
        raise HTTPException(
            status_code=400,
            detail=f"Allocation must sum to 100%, got {total}%"
        )
    
    # Create funnel allocation
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    # Use scenario engine for calculation
    scenario_engine = ScenarioModelingEngine()
    
    scenario = scenario_engine.model_scenario(
        total_budget=Decimal(str(total_budget)),
        funnel_allocation=allocation,
        selected_channels=[
            ChannelType.META,
            ChannelType.GOOGLE,
            ChannelType.TIKTOK,
            ChannelType.MICROSOFT
        ]
    )
    
    return {
        "total_budget": total_budget,
        "funnel_allocation": {
            "awareness": awareness,
            "consideration": consideration,
            "performance": performance
        },
        "channel_allocations": [
            {
                "channel": alloc.channel.value,
                "budget": float(alloc.budget),
                "percentage": round(float(alloc.budget) / total_budget * 100, 1),
                "expected_leads": alloc.expected_leads,
                "expected_cpa": float(alloc.expected_cpa),
                "funnel_stage": alloc.funnel_stage.value,
                "risk_level": alloc.risk_level
            }
            for alloc in scenario.channel_allocations
        ],
        "summary": {
            "total_expected_leads": scenario.expected_leads,
            "total_expected_revenue": float(scenario.expected_revenue),
            "overall_roas": scenario.expected_roas,
            "risk_score": scenario.risk_score,
            "diversification_confidence": scenario.confidence
        },
        "recommendations": scenario.recommendations
    }


@router.post("/predict-scenario")
async def predict_scenario_advanced(
    client_id: str = Query(..., description="Client ID"),
    total_budget: float = Query(..., description="Total budget"),
    awareness: float = Query(..., description="Awareness percentage"),
    consideration: float = Query(..., description="Consideration percentage"),
    performance: float = Query(..., description="Performance percentage"),
    target_leads: float = Query(1000, description="Target leads"),
    target_cpa: float = Query(25.0, description="Target CPA"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Advanced scenario prediction with spline modeling, adstock saturation, and Overmind evaluation.
    
    Uses the unified PlanningService for complete planning output.
    """
    # Validate allocation
    total = awareness + consideration + performance
    if not (99 <= total <= 101):
        raise HTTPException(
            status_code=400,
            detail=f"Allocation must sum to 100%, got {total}%"
        )
    
    # Get client info
    client_result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Initialize Planning Service
    planning_service = PlanningService()
    
    # Create client context
    context = ClientContext(
        industry=client.industry,
        business_goal=BusinessGoal.customer_acquisition,
        current_budget=Decimal(str(total_budget)),
        target_leads=target_leads,
        target_cpa=Decimal(str(target_cpa)),
        seasonality="peak"
    )
    
    # Create funnel allocation
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    # Generate complete planning output
    output = await planning_service.generate_complete_planning_output(
        client_context=context,
        total_budget=Decimal(str(total_budget)),
        funnel_allocation=allocation,
        days_since_refresh={
            "meta": 14,
            "google": 7,
            "tiktok": 21,
            "microsoft": 10
        }
    )
    
    return {
        "scenario_inputs": {
            "total_budget": total_budget,
            "funnel_allocation": {
                "awareness": awareness,
                "consideration": consideration,
                "performance": performance
            },
            "client_targets": {
                "target_leads": target_leads,
                "target_cpa": target_cpa
            }
        },
        "predictions": {
            "predicted_leads": output.prediction.predicted_leads,
            "incremental_leads": output.prediction.incremental_leads,
            "confidence_level": output.prediction.confidence_level,
            "target_achievement": round(output.prediction.predicted_leads / target_leads, 2)
        },
        "channel_predictions": {
            channel: {
                "predicted_leads": pred.predicted_leads,
                "confidence_interval": {
                    "lower": pred.confidence_interval[0],
                    "upper": pred.confidence_interval[1]
                },
                "incremental_value": pred.incremental_value,
                "saturation_level": pred.saturation_level,
                "adstock_remaining": pred.adstock_remaining,
                "refresh_recommendation": pred.refresh_recommendation
            }
            for channel, pred in output.prediction.channel_predictions.items()
        },
        "adstock_analysis": [
            {
                "channel": sat.channel,
                "current_saturation": sat.current_saturation,
                "decay_rate": sat.decay_rate,
                "days_until_refresh": sat.days_until_refresh,
                "saturation_velocity": sat.saturation_velocity,
                "refresh_urgency": sat.refresh_urgency
            }
            for sat in output.adstock_analysis
        ],
        "overmind_evaluation": {
            "score": output.prediction.overmind_score,
            "assessment": "Strong alignment" if output.prediction.overmind_score > 0.8 else "Needs optimization" if output.prediction.overmind_score > 0.6 else "Poor alignment"
        },
        "token_outcome": output.token_outcome,
        "optimization_recommendations": output.prediction.optimization_recommendations
    }


@router.get("/spline-prediction")
async def get_spline_prediction(
    client_id: str = Query(..., description="Client ID"),
    channel: str = Query(..., description="Channel name"),
    budget: float = Query(..., description="Budget amount"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get spline-based prediction for a single channel.
    
    Returns predicted leads, confidence intervals, and incremental value analysis.
    """
    from services.planning import PredictiveModelingEngine
    
    engine = PredictiveModelingEngine()
    prediction = engine.calculate_spline_prediction(channel, budget)
    
    return {
        "channel": channel,
        "budget": budget,
        "prediction": {
            "predicted_leads": prediction.predicted_leads,
            "confidence_interval": {
                "lower": prediction.confidence_interval[0],
                "upper": prediction.confidence_interval[1]
            },
            "incremental_value": prediction.incremental_value,
            "saturation_level": prediction.saturation_level,
            "adstock_remaining": prediction.adstock_remaining,
            "refresh_recommendation": prediction.refresh_recommendation
        }
    }


@router.get("/adstock-saturation")
async def get_adstock_saturation(
    client_id: str = Query(..., description="Client ID"),
    channel: str = Query(..., description="Channel name"),
    days_since_refresh: int = Query(14, description="Days since creative refresh"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get adstock saturation analysis for a channel.
    
    Returns current saturation, decay rate, and refresh recommendations.
    Uses the unified adstock engine.
    """
    from services.common.adstock_decay import AdstockDecayEngine
    
    engine = AdstockDecayEngine()
    
    # Get default lambda for channel
    default_lambdas = {
        "meta": 0.7,
        "google": 0.65,
        "tiktok": 0.8,
        "microsoft": 0.75
    }
    
    decay_lambda = default_lambdas.get(channel, 0.7)
    
    saturation = engine.analyze_saturation(
        channel=channel,
        days_since_refresh=days_since_refresh,
        decay_lambda=decay_lambda
    )
    
    return {
        "channel": channel,
        "days_since_refresh": days_since_refresh,
        "saturation_analysis": {
            "current_saturation": saturation.current_saturation,
            "decay_rate": saturation.decay_rate,
            "days_until_refresh": saturation.days_until_refresh,
            "saturation_velocity": saturation.saturation_velocity,
            "refresh_urgency": saturation.refresh_urgency
        },
        "recommendations": {
            "refresh_timing": f"Refresh in {saturation.days_until_refresh} days" if saturation.days_until_refresh > 0 else "Refresh immediately",
            "action": "Replace creative assets" if saturation.refresh_urgency == "immediate" else "Monitor performance"
        }
    }


@router.post("/realtime-prediction")
async def realtime_prediction_update(
    client_id: str = Query(..., description="Client ID"),
    awareness: float = Query(..., description="Awareness slider value"),
    consideration: float = Query(..., description="Consideration slider value"),
    performance: float = Query(..., description="Performance slider value"),
    total_budget: float = Query(3500.0, description="Total budget"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Real-time prediction update as sliders move.
    
    Lightweight endpoint for fast UI updates during slider interaction.
    """
    from services.planning import ScenarioModelingEngine, FunnelAllocation
    from decimal import Decimal
    
    # Quick channel allocation calculation
    scenario_engine = ScenarioModelingEngine()
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    scenario = scenario_engine.model_scenario(
        total_budget=Decimal(str(total_budget)),
        funnel_allocation=allocation,
        selected_channels=[
            ChannelType.META,
            ChannelType.GOOGLE,
            ChannelType.TIKTOK,
            ChannelType.MICROSOFT
        ]
    )
    
    # Quick spline predictions
    from services.planning import PredictiveModelingEngine
    predictive_engine = PredictiveModelingEngine()
    channel_predictions = {}
    
    for alloc in scenario.channel_allocations:
        prediction = predictive_engine.calculate_spline_prediction(
            alloc.channel.value,
            float(alloc.budget)
        )
        channel_predictions[alloc.channel.value] = {
            "leads": prediction.predicted_leads,
            "incremental": prediction.incremental_value,
            "saturation": prediction.saturation_level
        }
    
    total_leads = sum(pred["leads"] for pred in channel_predictions.values())
    total_incremental = sum(pred["incremental"] for pred in channel_predictions.values())
    
    return {
        "funnel_allocation": {
            "awareness": awareness,
            "consideration": consideration,
            "performance": performance
        },
        "predictions": {
            "total_leads": total_leads,
            "total_incremental": total_incremental,
            "channel_breakdown": channel_predictions
        },
        "risk_score": scenario.risk_score,
        "confidence": scenario.confidence
    }


@router.get("/channel-mappings")
async def get_channel_mappings(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all channel mappings showing how channels map to funnel stages.
    """
    # Get all channel mappings
    mappings_result = await session.execute(
        select(ChannelMapping).where(ChannelMapping.is_active == True)
    )
    mappings = mappings_result.scalars().all()
    
    # Get funnel stages for context
    stages_result = await session.execute(
        select(FunnelStage)
    )
    stages = stages_result.scalars().all()
    
    # Create stage name to ID mapping
    stage_map = {stage.id: stage.name for stage in stages}
    stage_info = {stage.name: {
        "description": stage.description,
        "risk_level": stage.risk_level,
        "expected_roi_range": {
            "min": float(stage.expected_roi_min) if stage.expected_roi_min else 0,
            "max": float(stage.expected_roi_max) if stage.expected_roi_max else 0
        },
        "time_to_conversion": stage.time_to_conversion
    } for stage in stages}
    
    # Format channel mappings
    channel_mappings = []
    for mapping in mappings:
        stage_name = stage_map.get(mapping.funnel_stage_id, "unknown")
        
        channel_mappings.append({
            "channel_name": mapping.channel_name,
            "funnel_stage": stage_name,
            "funnel_stage_id": mapping.funnel_stage_id,
            "default_allocation_weight": float(mapping.default_allocation_weight),
            "typical_cpa": float(mapping.typical_cpa) if mapping.typical_cpa else 0,
            "typical_conversion_rate": float(mapping.typical_conversion_rate) if mapping.typical_conversion_rate else 0,
            "is_active": mapping.is_active,
            "updated_at": mapping.updated_at.isoformat() if mapping.updated_at else None
        })
    
    # Group by funnel stage
    by_stage = {}
    for mapping in channel_mappings:
        stage = mapping["funnel_stage"]
        if stage not in by_stage:
            by_stage[stage] = []
        by_stage[stage].append(mapping)
    
    return {
        "channel_mappings": channel_mappings,
        "by_funnel_stage": by_stage,
        "funnel_stages": stage_info,
        "total_channels": len(channel_mappings),
        "last_updated": max([m.updated_at for m in mappings] if mappings else None)
    }


@router.post("/channel-mappings")
async def create_channel_mapping(
    client_id: str = Query(..., description="Client ID"),
    channel_name: str = Query(..., description="Channel name (meta, google, tiktok, etc.)"),
    funnel_stage: str = Query(..., description="Funnel stage (awareness, consideration, performance)"),
    default_weight: float = Query(0.3, description="Default allocation weight"),
    typical_cpa: float = Query(25.0, description="Typical cost per acquisition"),
    typical_conversion_rate: float = Query(0.03, description="Typical conversion rate"),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new channel mapping."""
    # Get the funnel stage ID
    stage_result = await session.execute(
        select(FunnelStage).where(FunnelStage.name == funnel_stage)
    )
    stage = stage_result.scalar_one_or_none()
    
    if not stage:
        raise HTTPException(status_code=404, detail=f"Funnel stage '{funnel_stage}' not found")
    
    # Check if mapping already exists
    existing_result = await session.execute(
        select(ChannelMapping).where(ChannelMapping.channel_name == channel_name)
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        # Update existing mapping
        existing.funnel_stage_id = stage.id
        existing.default_allocation_weight = default_weight
        existing.typical_cpa = Decimal(str(typical_cpa))
        existing.typical_conversion_rate = typical_conversion_rate
        existing.is_active = True
        existing.updated_at = datetime.now()
        
        await session.commit()
        await session.refresh(existing)
        
        return {
            "action": "updated",
            "channel_mapping": {
                "id": existing.id,
                "channel_name": existing.channel_name,
                "funnel_stage": funnel_stage,
                "default_allocation_weight": float(existing.default_allocation_weight),
                "typical_cpa": float(existing.typical_cpa),
                "typical_conversion_rate": float(existing.typical_conversion_rate)
            }
        }
    
    # Create new mapping
    new_mapping = ChannelMapping(
        id=str(uuid.uuid4()),
        channel_name=channel_name,
        funnel_stage_id=stage.id,
        default_allocation_weight=default_weight,
        typical_cpa=Decimal(str(typical_cpa)),
        typical_conversion_rate=typical_conversion_rate,
        is_active=True
    )
    
    session.add(new_mapping)
    await session.commit()
    await session.refresh(new_mapping)
    
    return {
        "action": "created",
        "channel_mapping": {
            "id": new_mapping.id,
            "channel_name": new_mapping.channel_name,
            "funnel_stage": funnel_stage,
            "default_allocation_weight": float(new_mapping.default_allocation_weight),
            "typical_cpa": float(new_mapping.typical_cpa),
            "typical_conversion_rate": float(new_mapping.typical_conversion_rate)
        }
    }


@router.get("/funnel-stages")
async def get_funnel_stages(
    session: AsyncSession = Depends(get_async_session)
):
    """Get all funnel stage definitions."""
    stages_result = await session.execute(
        select(FunnelStage)
    )
    stages = stages_result.scalars().all()
    
    return {
        "funnel_stages": [
            {
                "id": stage.id,
                "name": stage.name,
                "description": stage.description,
                "risk_level": stage.risk_level,
                "expected_roi_range": {
                    "min": float(stage.expected_roi_min) if stage.expected_roi_min else 0,
                    "max": float(stage.expected_roi_max) if stage.expected_roi_max else 0
                },
                "time_to_conversion": stage.time_to_conversion
            }
            for stage in stages
        ],
        "total_stages": len(stages)
    }


@router.post("/complete-planning-with-keywords")
async def complete_planning_with_keywords(
    query: str = Query("Gymshark fitness apparel", description="Research query"),
    max_results: int = Query(10, description="Max results per source"),
    use_disbert: bool = Query(True, description="Use Thrad DisBERT model for context organization"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Complete media planning with keyword logging.
    
    This endpoint:
    1. Performs Tavily research (Reddit, SEO, Google keywords)
    2. Extracts Google keywords for bidding
    3. Logs keywords to GYMSHARK_PPC_GENERIC_2026 campaign
    4. Generates Thrad data for each keyword
    5. Returns complete planning results with logs
    
    If use_disbert is True, logs will specify "using thrad_disbert model".
    """
    from shared.utils.settings import settings
    
    tavily_api_key = settings.tavily_api_key
    
    if not tavily_api_key:
        raise HTTPException(
            status_code=400,
            detail="TAVILY_API_KEY not configured"
        )
    
    # Step 1: Perform Tavily research
    research_service = GymsharkTavilyResearch(tavily_api_key=tavily_api_key)
    
    research_result = research_service.perform_comprehensive_research(
        base_query=query,
        max_results_per_source=max_results,
        time_range="month"
    )
    
    # Step 2: Extract Google keywords
    google_keywords_dicts = [
        {
            "keyword": kw.keyword,
            "match_type": kw.match_type,
            "bid_suggestion": kw.bid_suggestion,
            "relevance_to_gymshark": kw.relevance_to_gymshark,
            "search_intent": kw.search_intent,
            "category": "H" if kw.search_intent == "transactional" else "E"
        }
        for kw in research_result.google_keywords
    ]
    
    # Step 3: Log keywords to campaign with model specification
    model_used = "thrad_disbert" if use_disbert else None
    log_entries = campaign_keyword_logger.log_keywords_from_research(
        google_keywords=google_keywords_dicts,
        source="tavily",
        model_used=model_used
    )
    
    # Step 4: Return complete results
    return {
        "research_summary": research_result.summary,
        "keywords_added": len(log_entries),
        "campaign_name": "GYMSHARK_PPC_GENERIC_2026",
        "model_used": model_used,
        "keyword_logs": [
            {
                "keyword": log.keyword,
                "match_type": log.match_type,
                "bid_amount": log.bid_amount,
                "source": log.source,
                "confidence": log.confidence,
                "intent": log.intent,
                "category": log.category,
                "model_used": log.model_used,
                "timestamp": log.timestamp,
                "thrad_data": log.thrad_data
            }
            for log in log_entries
        ],
        "research_data": {
            "reddit_posts_count": len(research_result.reddit_posts),
            "seo_keywords_count": len(research_result.seo_keywords),
            "google_keywords_count": len(research_result.google_keywords),
            "thrad_inputs_count": len(research_result.thrad_inputs),
            "content_ideas_count": len(research_result.content_ideas)
        }
    }


@router.get("/campaign-keyword-logs")
async def get_campaign_keyword_logs(
    campaign_name: str = Query("GYMSHARK_PPC_GENERIC_2026", description="Campaign name"),
    limit: int = Query(50, description="Max logs to return"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get keyword logs for a campaign."""
    logs = campaign_keyword_logger.get_logs_by_campaign(campaign_name, limit)
    
    return {
        "campaign_name": campaign_name,
        "logs_count": len(logs),
        "logs": logs
    }


@router.get("/keyword-logs-by-source")
async def get_keyword_logs_by_source(
    source: str = Query(..., description="Source (tavily, manual, bert, thrad)"),
    limit: int = Query(50, description="Max logs to return"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get keyword logs by source."""
    logs = campaign_keyword_logger.get_logs_by_source(source, limit)
    
    return {
        "source": source,
        "logs_count": len(logs),
        "logs": logs
    }


@router.post("/log-keyword-manually")
async def log_keyword_manually(
    keyword: str = Query(..., description="Keyword to log"),
    match_type: str = Query("phrase", description="Match type"),
    bid_amount: float = Query(2.0, description="Bid amount"),
    source: str = Query("manual", description="Source"),
    confidence: float = Query(0.7, description="Confidence"),
    intent: str = Query("informational", description="Intent"),
    category: Optional[str] = Query(None, description="Category"),
    session: AsyncSession = Depends(get_async_session)
):
    """Manually log a keyword addition."""
    log_entry = campaign_keyword_logger.log_keyword_addition(
        keyword=keyword,
        match_type=match_type,
        bid_amount=bid_amount,
        source=source,
        confidence=confidence,
        intent=intent,
        category=category
    )
    
    # Generate Thrad data
    thrad_data = campaign_keyword_logger.generate_thrad_data(keyword)
    log_entry.thrad_data = asdict(thrad_data)
    
    return {
        "message": "Keyword logged successfully",
        "log": asdict(log_entry)
    }