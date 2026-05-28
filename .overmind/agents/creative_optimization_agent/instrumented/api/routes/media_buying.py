"""
Media Buying API Routes

Tactical media buying endpoints for budget execution, bid management,
and performance monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

from shared.database import get_async_session
from shared.models.campaign import Campaign, CampaignPerformance

from services.media_buying import MediaBuyingService, ExecutionResult, MediaBuyingOutput
from services.trading.thompson_allocator import AllocationResult

router = APIRouter(prefix="/api/v1/media-buying", tags=["media-buying"])


@router.post("/execute-allocation")
async def execute_allocation_plan(
    client_id: str = Query(..., description="Client ID"),
    allocation_plan: str = Query(..., description="JSON string of channel allocations"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Execute an allocation plan using Thompson sampling.
    
    This is the tactical execution phase that takes a strategic allocation plan
    from the Planning flow and executes it via Thompson sampling.
    """
    import json
    
    try:
        # Parse allocation plan
        plan = json.loads(allocation_plan)
        if not isinstance(plan, dict):
            raise HTTPException(status_code=400, detail="allocation_plan must be a JSON object")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in allocation_plan")
    
    # Mock channel performance data
    channel_performance = {
        channel: {
            "expected_leads": budget * 0.12,
            "actual_leads": budget * 0.10,
            "conversions": budget * 0.05
        }
        for channel, budget in plan.items()
    }
    
    # Initialize Media Buying Service
    media_buying_service = MediaBuyingService()
    
    # Execute allocation
    execution = await media_buying_service.execute_allocation_plan(
        allocation_plan=plan,
        channel_performance=channel_performance
    )
    
    return {
        "execution": {
            "platform_allocations": execution.platform_allocations,
            "bids_placed": execution.bids_placed,
            "total_spend": execution.total_spend,
            "expected_conversions": execution.expected_conversions,
            "execution_timestamp": execution.execution_timestamp
        },
        "method": "thompson_sampling",
        "status": "completed"
    }


@router.post("/execute-complete")
async def execute_complete_media_buying(
    client_id: str = Query(..., description="Client ID"),
    allocation_plan: str = Query(..., description="JSON string of channel allocations"),
    daily_conversions: str = Query(..., description="JSON string of daily conversions per channel"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Execute complete Media Buying flow with all components.
    
    Includes Thompson sampling, bid discovery, and adstock monitoring.
    """
    import json
    
    try:
        plan = json.loads(allocation_plan)
        conversions = json.loads(daily_conversions)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    # Mock channel performance
    channel_performance = {
        channel: {
            "expected_leads": budget * 0.12,
            "conversions": budget * 0.05
        }
        for channel, budget in plan.items()
    }
    
    # Initialize Media Buying Service
    media_buying_service = MediaBuyingService()
    
    # Execute complete media buying
    output = await media_buying_service.execute_complete_media_buying(
        allocation_plan=plan,
        channel_performance=channel_performance,
        daily_conversions=conversions
    )
    
    return {
        "execution": {
            "platform_allocations": output.execution.platform_allocations,
            "bids_placed": output.execution.bids_placed,
            "total_spend": output.execution.total_spend,
            "expected_conversions": output.execution.expected_conversions
        },
        "adstock_signals": {
            channel: {
                "lambda_decay": result.lambda_decay,
                "signal": result.signal,
                "confidence": result.confidence
            }
            for channel, result in output.adstock_signals.items()
        },
        "bid_recommendations": [
            {
                "channel": rec.channel,
                "recommended_bid": float(rec.recommended_bid),
                "confidence": rec.confidence,
                "reasoning": rec.reasoning
            }
            for rec in output.bid_recommendations
        ],
        "performance_metrics": output.performance_metrics,
        "status": "completed"
    }


@router.get("/campaign-performance")
async def get_campaign_performance(
    client_id: str = Query(..., description="Client ID"),
    campaign_id: str = Query(..., description="Campaign ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get performance data for a campaign.
    
    Returns impressions, clicks, conversions, ROAS, and other metrics.
    """
    # Get campaign
    campaign_result = await session.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get performance data
    perf_result = await session.execute(
        select(CampaignPerformance).where(CampaignPerformance.campaign_id == campaign_id)
    )
    performances = perf_result.scalars().all()
    
    if not performances:
        # Return demo data
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
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
    
    # Aggregate performance data
    total_impressions = sum(p.impressions for p in performances)
    total_clicks = sum(p.clicks for p in performances)
    total_conversions = sum(p.conversions for p in performances)
    total_spend = sum(float(p.spend) for p in performances)
    total_revenue = sum(float(p.revenue) for p in performances)
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "performance": {
            "impressions": total_impressions,
            "clicks": total_clicks,
            "ctr": round(total_clicks / total_impressions, 4) if total_impressions > 0 else 0,
            "conversions": total_conversions,
            "cost_per_conversion": round(total_spend / total_conversions, 2) if total_conversions > 0 else 0,
            "conversion_rate": round(total_conversions / total_clicks, 4) if total_clicks > 0 else 0,
            "cost": total_spend,
            "revenue": total_revenue,
            "roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0
        },
        "performance_by_day": [
            {
                "date": p.date.isoformat(),
                "impressions": p.impressions,
                "clicks": p.clicks,
                "conversions": p.conversions
            }
            for p in performances
        ]
    }


@router.get("/thompson-allocation")
async def get_thompson_sampling_result(
    client_id: str = Query(..., description="Client ID"),
    total_budget: float = Query(3500.0, description="Total budget"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get Thompson sampling allocation results.
    
    Returns the budget distribution based on Bayesian bandit algorithm.
    """
    # Mock allocation results for demo
    allocation_results = [
        AllocationResult(
            channel="meta",
            budget=Decimal("1000.00"),
            expected_leads=120,
            actual_leads=115,
            conversions=48,
            spend=Decimal("1000.00")
        ),
        AllocationResult(
            channel="google",
            budget=Decimal("900.00"),
            expected_leads=135,
            actual_leads=140,
            conversions=63,
            spend=Decimal("900.00")
        ),
        AllocationResult(
            channel="tiktok",
            budget=Decimal("1000.00"),
            expected_leads=95,
            actual_leads=90,
            conversions=38,
            spend=Decimal("1000.00")
        ),
        AllocationResult(
            channel="microsoft",
            budget=Decimal("600.00"),
            expected_leads=75,
            actual_leads=70,
            conversions=30,
            spend=Decimal("600.00")
        )
    ]
    
    # Initialize Media Buying Service
    media_buying_service = MediaBuyingService()
    
    # Get Thompson allocation
    allocations = media_buying_service.get_thompson_allocation(
        allocation_results=allocation_results,
        total_budget=Decimal(str(total_budget))
    )
    
    return {
        "total_budget": total_budget,
        "thompson_sampling_allocations": allocations,
        "method": "beta_bernoulli_bandit",
        "confidence": 0.85,
        "exploration_budget": total_budget * 0.15,
        "exploitation_budget": total_budget * 0.85
    }


@router.get("/adstock-signals")
async def get_adstock_signals(
    client_id: str = Query(..., description="Client ID"),
    daily_conversions: str = Query(..., description="JSON string of daily conversions per channel"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get adstock decay signals for all channels.
    
    Uses the unified adstock engine to determine hold/reduce/exit signals.
    """
    import json
    import numpy as np
    
    try:
        conversions_data = json.loads(daily_conversions)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in daily_conversions")
    
    from services.common.adstock_decay import AdstockDecayEngine
    
    engine = AdstockDecayEngine()
    
    signals = {}
    for channel, conversions in conversions_data.items():
        if len(conversions) >= 3:
            result = engine.fit_decay_lambda(
                daily_conversions=np.array(conversions)
            )
            signals[channel] = {
                "lambda_decay": result.lambda_decay,
                "std_error": result.std_error,
                "initial_effect": result.initial_effect,
                "confidence": result.confidence,
                "signal": result.signal
            }
        else:
            signals[channel] = {
                "lambda_decay": 0.5,
                "std_error": 0.5,
                "initial_effect": conversions[0] if conversions else 0,
                "confidence": "low",
                "signal": "monitor"
            }
    
    return {
        "adstock_signals": signals,
        "summary": {
            "total_channels": len(signals),
            "hold_signals": len([s for s in signals.values() if s["signal"] == "hold"]),
            "reduce_signals": len([s for s in signals.values() if s["signal"] == "reduce"]),
            "exit_signals": len([s for s in signals.values() if s["signal"] == "exit"])
        }
    }