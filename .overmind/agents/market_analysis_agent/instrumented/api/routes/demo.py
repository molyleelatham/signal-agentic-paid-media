"""
Demo API routes for Acme fashion e-commerce client.
Endpoints to support the hackathon demonstration scenario.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import json as json_lib
import uuid

from shared.database import get_async_session
from shared.models.client import Client, ClientGoal, ClientPlatform
from shared.models.campaign import Campaign, CampaignPerformance
from shared.models.content import ContentBrief, TopicCluster
from shared.models.analytics import (
    PerformanceMetric, BudgetAllocation, 
    AttentionTokenTransaction, EfficiencyMetrics,
    FunnelStage, ChannelMapping
)
from shared.models.creative import Creative, CreativePlacement
from shared.agents.cursor_integration import CursorComposerService
from shared.utils.settings import settings


router = APIRouter(prefix="/api/v1/demo", tags=["demo"])


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get dashboard overview with briefs, allocation rounds, and recent decisions.
    This is the main dashboard data for the Acme client.
    """
    
    # Get client info
    client_result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get recent content briefs
    briefs_result = await session.execute(
        select(ContentBrief)
        .where(ContentBrief.client_id == client_id)
        .order_by(ContentBrief.created_at.desc())
        .limit(5)
    )
    briefs = briefs_result.scalars().all()
    
    # Get recent budget allocations (allocation rounds)
    allocations_result = await session.execute(
        select(BudgetAllocation)
        .where(BudgetAllocation.client_id == client_id)
        .order_by(BudgetAllocation.allocation_date.desc())
        .limit(4)
    )
    allocations = allocations_result.scalars().all()
    
    # Get client goals progress
    goals_result = await session.execute(
        select(ClientGoal).where(ClientGoal.client_id == client_id)
    )
    goals = goals_result.scalars().all()
    
    # Get active campaigns
    campaigns_result = await session.execute(
        select(Campaign)
        .where(Campaign.client_id == client_id, Campaign.status == "active")
    )
    active_campaigns = campaigns_result.scalars().all()
    
    # Calculate total weekly spend
    total_weekly_budget = sum(
        (cam.daily_budget or Decimal("0")) * 7 
        for cam in active_campaigns
    )
    
    # Get recent attention token balance
    recent_transactions_result = await session.execute(
        select(func.sum(AttentionTokenTransaction.amount))
        .where(AttentionTokenTransaction.client_id == client_id)
    )
    token_balance = recent_transactions_result.scalar() or Decimal("0")
    
    return {
        "client": {
            "id": client.id,
            "name": client.name,
            "industry": client.industry,
            "status": client.status,
            "metadata": client.metadata
        },
        "briefs": [
            {
                "id": brief.id,
                "title": brief.title,
                "type": brief.brief_type,
                "status": brief.status,
                "created_at": brief.created_at.isoformat(),
                "topic_clusters": brief.metadata.get("topic_clusters", []),
                "platforms": brief.metadata.get("platforms", [])
            }
            for brief in briefs
        ],
        "allocation_rounds": [
            {
                "id": allocation.id,
                "date": allocation.allocation_date.isoformat(),
                "total_budget": float(allocation.total_budget),
                "decay_alpha_rate": float(allocation.decay_alpha_rate),
                "allocations": allocation.allocations,
                "decision_type": allocation.decision_type,
                "week": allocation.metadata.get("week")
            }
            for allocation in allocations
        ],
        "goals": [
            {
                "id": goal.id,
                "type": goal.goal_type,
                "target": goal.target_value,
                "current": goal.current_value,
                "progress": round((goal.current_value / goal.target_value) * 100, 1),
                "timeframe": goal.timeframe,
                "priority": goal.priority
            }
            for goal in goals
        ],
        "summary": {
            "active_campaigns": len(active_campaigns),
            "weekly_budget": float(total_weekly_budget),
            "token_balance": float(token_balance),
            "platforms": ["meta", "google", "tiktok", "microsoft"]
        }
    }


@router.get("/dashboard/briefs")
async def get_content_briefs(
    client_id: str = Query(..., description="Client ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all content briefs with filtering options."""
    
    query = select(ContentBrief).where(ContentBrief.client_id == client_id)
    
    if status:
        query = query.where(ContentBrief.status == status)
    
    query = query.order_by(ContentBrief.created_at.desc())
    
    result = await session.execute(query)
    briefs = result.scalars().all()
    
    return {
        "briefs": [
            {
                "id": brief.id,
                "title": brief.title,
                "type": brief.brief_type,
                "status": brief.status,
                "created_at": brief.created_at.isoformat(),
                "source": brief.metadata.get("source"),
                "topic_clusters": brief.metadata.get("topic_clusters", []),
                "target_audience": brief.metadata.get("target_audience"),
                "key_insights": brief.metadata.get("key_insights", []),
                "creative_guidance": brief.metadata.get("creative_guidance", {}),
                "platforms": brief.metadata.get("platforms", []),
                "content_types": brief.metadata.get("content_types", [])
            }
            for brief in briefs
        ]
    }


@router.get("/dashboard/allocations")
async def get_budget_allocations(
    client_id: str = Query(..., description="Client ID"),
    weeks: int = Query(4, description="Number of weeks to retrieve"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get budget allocation history (allocation rounds)."""
    
    result = await session.execute(
        select(BudgetAllocation)
        .where(BudgetAllocation.client_id == client_id)
        .order_by(BudgetAllocation.allocation_date.desc())
        .limit(weeks)
    )
    allocations = result.scalars().all()
    
    return {
        "allocations": [
            {
                "id": allocation.id,
                "date": allocation.allocation_date.isoformat(),
                "total_budget": float(allocation.total_budget),
                "decay_alpha_rate": float(allocation.decay_alpha_rate),
                "allocations": allocation.allocations,
                "decision_type": allocation.decision_type,
                "week": allocation.metadata.get("week"),
                "exploration_budget": float(allocation.metadata.get("exploration_budget", 0)),
                "exploitation_budget": float(allocation.metadata.get("exploitation_budget", 0)),
                "agent_recommendations": allocation.metadata.get("agent_recommendations", {})
            }
            for allocation in allocations
        ]
    }


# ============================================================================
# Tavily Crawling & Topic Clustering Endpoints
# ============================================================================

@router.get("/intelligence/tavily-results")
async def get_tavily_crawling_results(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get Tavily crawling results and topic clustering analysis.
    Shows social media monitoring and topic clustering for creative briefs.
    """
    
    # Get topic clusters
    clusters_result = await session.execute(
        select(TopicCluster)
        .where(TopicCluster.client_id == client_id)
        .order_by(TopicCluster.search_volume.desc())
    )
    clusters = clusters_result.scalars().all()
    
    # Get recent briefs with Tavily source
    briefs_result = await session.execute(
        select(ContentBrief)
        .where(
            ContentBrief.client_id == client_id,
            ContentBrief.metadata["source"].astext == "tavily_crawling"
        )
        .order_by(ContentBrief.created_at.desc())
        .limit(3)
    )
    tavily_briefs = briefs_result.scalars().all()
    
    return {
        "topic_clusters": [
            {
                "id": cluster.id,
                "name": cluster.name,
                "keywords": cluster.keywords,
                "search_volume": cluster.search_volume,
                "competition_score": cluster.competition_score,
                "trend_direction": cluster.trend_direction,
                "growth_rate": cluster.metadata.get("growth_rate", 0),
                "seasonal": cluster.metadata.get("seasonal", False),
                "peak_months": cluster.metadata.get("peak_months", []),
                "related_topics": cluster.metadata.get("related_topics", []),
                "last_updated": cluster.last_updated.isoformat()
            }
            for cluster in clusters
        ],
        "tavily_briefs": [
            {
                "id": brief.id,
                "title": brief.title,
                "created_at": brief.created_at.isoformat(),
                "topic_clusters": brief.metadata.get("topic_clusters", []),
                "key_insights": brief.metadata.get("key_insights", []),
                "target_audience": brief.metadata.get("target_audience")
            }
            for brief in tavily_briefs
        ],
        "crawling_summary": {
            "total_topics": len(clusters),
            "active_clusters": sum(1 for c in clusters if c.trend_direction == "up"),
            "avg_growth_rate": round(sum(c.metadata.get("growth_rate", 0) for c in clusters) / len(clusters), 2) if clusters else 0,
            "last_crawl": max(c.last_updated for c in clusters).isoformat() if clusters else None
        }
    }


@router.get("/intelligence/topic-clusters")
async def get_topic_clusters(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get detailed topic cluster information for SEO and geo optimization."""
    
    result = await session.execute(
        select(TopicCluster)
        .where(TopicCluster.client_id == client_id)
        .order_by(TopicCluster.search_volume.desc())
    )
    clusters = result.scalars().all()
    
    return {
        "clusters": [
            {
                "id": cluster.id,
                "name": cluster.name,
                "keywords": cluster.keywords,
                "search_volume": cluster.search_volume,
                "competition_score": cluster.competition_score,
                "trend_direction": cluster.trend_direction,
                "growth_rate": cluster.metadata.get("growth_rate", 0),
                "seasonal": cluster.metadata.get("seasonal", False),
                "peak_months": cluster.metadata.get("peak_months", []),
                "related_topics": cluster.metadata.get("related_topics", []),
                "last_updated": cluster.last_updated.isoformat(),
                "seo_opportunity": {
                    "priority": "high" if cluster.competition_score < 0.6 and cluster.trend_direction == "up" else "medium",
                    "difficulty": "low" if cluster.competition_score < 0.5 else "medium" if cluster.competition_score < 0.7 else "high",
                    "potential_traffic": cluster.search_volume * (1 + cluster.metadata.get("growth_rate", 0))
                },
                "geo_optimization": {
                    "target_markets": ["US", "UK", "Germany", "France"],
                    "regional_variations": {
                        "US": cluster.search_volume * 0.4,
                        "UK": cluster.search_volume * 0.25,
                        "Germany": cluster.search_volume * 0.2,
                        "France": cluster.search_volume * 0.15
                    }
                }
            }
            for cluster in clusters
        ]
    }


# ============================================================================
# CPL Output Matrix & Scenario Builder Endpoints
# ============================================================================

@router.get("/planning/cpl-matrix")
async def get_cpl_output_matrix(
    client_id: str = Query(..., description="Client ID"),
    target_leads: int = Query(1000, description="Target number of leads"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get CPL output matrix for scenario planning.
    Helps client plan budget allocation to achieve lead targets.
    """
    
    # Get current efficiency metrics
    efficiency_result = await session.execute(
        select(EfficiencyMetrics)
        .where(EfficiencyMetrics.client_id == client_id)
        .order_by(EfficiencyMetrics.period_end.desc())
        .limit(1)
    )
    efficiency = efficiency_result.scalar_one_or_none()
    
    # Get current CPL from recent performance
    recent_perf_result = await session.execute(
        select(PerformanceMetric)
        .where(
            PerformanceMetric.client_id == client_id,
            PerformanceMetric.metric_type == "efficiency"
        )
        .order_by(PerformanceMetric.date.desc())
        .limit(7)
    )
    recent_metrics = recent_perf_result.scalars().all()
    
    if recent_metrics:
        current_cpl = sum(m.value.get("cpl", 0) for m in recent_metrics) / len(recent_metrics)
        current_roas = sum(m.value.get("roas", 0) for m in recent_metrics) / len(recent_metrics)
    else:
        current_cpl = 28.0  # Default from demo data
        current_roas = 3.25
    
    # Calculate scenarios
    scenarios = []
    
    # Conservative scenario (current performance)
    scenarios.append({
        "name": "Conservative",
        "description": "Maintain current performance levels",
        "assumptions": {
            "cpl": current_cpl,
            "conversion_rate": 0.045,
            "roas": current_roas
        },
        "outcomes": {
            "required_budget": target_leads * current_cpl,
            "expected_leads": target_leads,
            "expected_revenue": target_leads * current_cpl * current_roas,
            "expected_customers": target_leads * 0.045
        }
    })
    
    # Optimistic scenario (10% improvement)
    scenarios.append({
        "name": "Optimistic",
        "description": "10% improvement in CPL from optimization",
        "assumptions": {
            "cpl": current_cpl * 0.9,
            "conversion_rate": 0.05,
            "roas": current_roas * 1.1
        },
        "outcomes": {
            "required_budget": target_leads * (current_cpl * 0.9),
            "expected_leads": target_leads,
            "expected_revenue": target_leads * (current_cpl * 0.9) * (current_roas * 1.1),
            "expected_customers": target_leads * 0.05
        }
    })
    
    # Aggressive scenario (20% improvement)
    scenarios.append({
        "name": "Aggressive",
        "description": "20% improvement in CPL from aggressive optimization",
        "assumptions": {
            "cpl": current_cpl * 0.8,
            "conversion_rate": 0.055,
            "roas": current_roas * 1.2
        },
        "outcomes": {
            "required_budget": target_leads * (current_cpl * 0.8),
            "expected_leads": target_leads,
            "expected_revenue": target_leads * (current_cpl * 0.8) * (current_roas * 1.2),
            "expected_customers": target_leads * 0.055
        }
    })
    
    return {
        "target_leads": target_leads,
        "current_performance": {
            "cpl": current_cpl,
            "roas": current_roas,
            "conversion_rate": 0.045
        },
        "improvement_history": {
            "cpl_reduction": float(efficiency.cpl_reduction) if efficiency else 0.20,
            "lead_increase": float(efficiency.lead_increase) if efficiency else 0.40
        },
        "scenarios": scenarios,
        "recommendation": {
            "suggested_scenario": "Optimistic",
            "reasoning": "Balanced approach with realistic improvements based on historical performance",
            "agent_insights": "Market analysis indicates strong momentum in sustainable fashion segment"
        }
    }


@router.post("/planning/scenario-builder")
async def build_scenario(
    client_id: str = Query(..., description="Client ID"),
    scenario_config: dict = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Build custom scenario based on client inputs.
    Interactive scenario builder for what-if analysis.
    """
    
    if not scenario_config:
        scenario_config = {
            "target_leads": 1000,
            "target_cpa": 25.0,
            "platform_allocation": {
                "meta": 0.30,
                "google": 0.30,
                "tiktok": 0.25,
                "microsoft": 0.15
            },
            "optimization_level": "moderate"
        }
    
    target_leads = scenario_config.get("target_leads", 1000)
    target_cpa = scenario_config.get("target_cpa", 25.0)
    platform_allocation = scenario_config.get("platform_allocation", {})
    optimization_level = scenario_config.get("optimization_level", "moderate")
    
    # Calculate optimization multiplier
    optimization_multipliers = {
        "conservative": 1.0,
        "moderate": 0.9,
        "aggressive": 0.8
    }
    opt_multiplier = optimization_multipliers.get(optimization_level, 0.9)
    
    # Platform-specific performance assumptions
    platform_performance = {
        "meta": {"cpl": 28.0, "roas": 3.2, "conversion_rate": 0.04},
        "google": {"cpl": 32.0, "roas": 3.5, "conversion_rate": 0.05},
        "tiktok": {"cpl": 22.0, "roas": 2.8, "conversion_rate": 0.03},
        "microsoft": {"cpl": 35.0, "roas": 3.0, "conversion_rate": 0.045}
    }
    
    # Calculate per-platform metrics
    platform_results = {}
    total_budget = 0
    total_expected_revenue = 0
    
    for platform, allocation in platform_allocation.items():
        perf = platform_performance.get(platform, {})
        platform_leads = int(target_leads * allocation)
        platform_cpl = perf.get("cpl", 30.0) * opt_multiplier
        platform_budget = platform_leads * platform_cpl
        platform_revenue = platform_budget * perf.get("roas", 3.0)
        
        platform_results[platform] = {
            "allocation": allocation,
            "target_leads": platform_leads,
            "expected_cpl": platform_cpl,
            "budget": platform_budget,
            "expected_revenue": platform_revenue,
            "roas": perf.get("roas", 3.0)
        }
        
        total_budget += platform_budget
        total_expected_revenue += platform_revenue
    
    return {
        "scenario_config": scenario_config,
        "results": {
            "total_budget": total_budget,
            "total_expected_revenue": total_expected_revenue,
            "overall_roas": total_expected_revenue / total_budget if total_budget > 0 else 0,
            "target_leads": target_leads,
            "weighted_cpl": total_budget / target_leads if target_leads > 0 else 0
        },
        "platform_breakdown": platform_results,
        "agent_recommendations": {
            "optimization_suggestions": [
                "Increase TikTok allocation for Gen Z audience",
                "Focus Google budget on high-intent keywords",
                "Test creative variations on Meta"
            ],
            "risk_factors": [
                "TikTok conversion rate lower than other platforms",
                "Microsoft competition increasing in fashion category"
            ],
            "confidence_score": 0.85
        }
    }


# ============================================================================
# Agent Chat & Overmind Evals Endpoints
# ============================================================================

@router.post("/agents/chat")
async def agent_chat(
    request: Request,
    client_id: str = Query(..., description="Client ID"),
    message: str = Query(..., description="User message to agents"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Agent chat interface for querying performance and insights.
    Handles "what happened in the last two weeks" type queries.
    """
    
    # Get efficiency metrics
    efficiency_result = await session.execute(
        select(EfficiencyMetrics)
        .where(EfficiencyMetrics.client_id == client_id)
        .order_by(EfficiencyMetrics.period_end.desc())
        .limit(1)
    )
    efficiency = efficiency_result.scalar_one_or_none()
    
    # Get recent performance metrics
    two_weeks_ago = datetime.now() - timedelta(days=14)
    recent_perf_result = await session.execute(
        select(PerformanceMetric)
        .where(
            PerformanceMetric.client_id == client_id,
            PerformanceMetric.metric_type == "efficiency",
            PerformanceMetric.date >= two_weeks_ago
        )
        .order_by(PerformanceMetric.date.desc())
    )
    recent_metrics = recent_perf_result.scalars().all()
    
    # Get recent budget allocations with agent recommendations
    recent_allocations_result = await session.execute(
        select(BudgetAllocation)
        .where(
            BudgetAllocation.client_id == client_id,
            BudgetAllocation.allocation_date >= two_weeks_ago
        )
        .order_by(BudgetAllocation.allocation_date.desc())
        .limit(2)
    )
    recent_allocations = recent_allocations_result.scalars().all()
    
    # Get recent content briefs
    recent_briefs_result = await session.execute(
        select(ContentBrief)
        .where(
            ContentBrief.client_id == client_id,
            ContentBrief.created_at >= two_weeks_ago
        )
        .order_by(ContentBrief.created_at.desc())
    )
    recent_briefs = recent_briefs_result.scalars().all()
    
    # Generate agent response based on query
    if "what happened" in message.lower() or "last two weeks" in message.lower():
        response = generate_what_happened_response(
            recent_metrics, 
            efficiency, 
            recent_allocations,
            recent_briefs
        )
    elif "efficiency" in message.lower() or "improvement" in message.lower():
        response = generate_efficiency_response(efficiency, recent_metrics)
    else:
        response = generate_general_response(client_id, recent_metrics, recent_briefs)

    llm_backend = "template"
    composer_note = None
    cursor = getattr(request.app.state, "cursor_composer", None) or CursorComposerService(
        api_key=settings.cursor_api_key,
        model=settings.cursor_model,
        cwd=settings.cursor_agent_cwd,
    )
    if cursor.is_configured:
        try:
            context_summary = {
                "client_id": client_id,
                "metrics_count": len(recent_metrics),
                "allocations_count": len(recent_allocations),
                "briefs_count": len(recent_briefs),
                "structured_response": response,
            }
            composer_text = await cursor.complete(
                user_prompt=(
                    f"User question: {message}\n\n"
                    f"Platform data context (JSON): {context_summary}\n\n"
                    "Synthesize a helpful answer for a marketing client. "
                    "Return JSON with keys: summary (string), insights (list of strings), "
                    "recommendations (list of strings)."
                ),
                system_prompt=(
                    "You are the SIGNAL orchestration agent using Cursor Composer 2.5. "
                    "Be specific, data-driven, and concise."
                ),
            )
            try:
                response = json_lib.loads(composer_text)
            except json_lib.JSONDecodeError:
                response = {
                    "summary": composer_text,
                    "insights": [],
                    "recommendations": [],
                }
            llm_backend = "cursor-composer-2.5"
            composer_note = "Response generated by Cursor Composer 2.5"
        except Exception as exc:
            composer_note = f"Composer unavailable, using templates: {exc}"
    
    return {
        "user_message": message,
        "agent_response": response,
        "llm_backend": llm_backend,
        "composer_note": composer_note,
        "overmind_evals": {
            "quality_score": 0.92,
            "optimization_cycles": 5,
            "learning_rate": 0.15,
            "last_optimization": (datetime.now() - timedelta(hours=6)).isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }


def generate_what_happened_response(metrics, efficiency, allocations, briefs):
    """Generate response for 'what happened' query."""
    
    if not metrics:
        return {
            "summary": "Not enough data available for the requested period.",
            "insights": [],
            "recommendations": []
        }
    
    # Calculate averages
    avg_cpl = sum(m.value.get("cpl", 0) for m in metrics) / len(metrics)
    avg_leads = sum(m.value.get("leads", 0) for m in metrics) / len(metrics)
    avg_roas = sum(m.value.get("roas", 0) for m in metrics) / len(metrics)
    avg_ltv_cac = sum(m.value.get("ltv_cac", 0) for m in metrics) / len(metrics)
    
    # Extract improvements
    improvements = efficiency.metadata if efficiency else {}
    
    response = {
        "summary": f"Since you've been working with SIGNAL, you've achieved a 20% reduction in CPL and 40% increase in leads. Here's what happened in the last two weeks:",
        "key_metrics": {
            "current_cpl": round(avg_cpl, 2),
            "cpl_reduction": "20%",
            "weekly_leads": int(avg_leads),
            "lead_increase": "40%",
            "current_roas": round(avg_roas, 2),
            "ltv_cac": round(avg_ltv_cac, 2)
        },
        "insights": [
            f"Strong performance on sustainable fashion content, driving {int(avg_leads * 0.35)} leads from eco-conscious audience",
            f"TikTok Gen Z campaign outperforming benchmarks with 4.2% engagement rate",
            f"Google search campaigns showing 45% higher conversion rate on 'sustainable fashion' keywords",
            f"Creative optimization improved CTR by 28% across all platforms"
        ],
        "opportunities": [
            "Expand successful sustainable fashion creative to Microsoft platform",
            "Increase budget allocation to TikTok for Gen Z back-to-school campaign",
            "Test new creative variants for high-performing 'summer trends' cluster",
            "Explore geo-targeting for UK market showing 23% lower CPL"
        ],
        "learnings": [
            "UGC-style creatives performing 2.3x better than polished studio content",
            "Evening ad delivery (6-9 PM) generating 35% higher conversion rates",
            "Mobile-first creative format resonating with target audience",
            "Sustainability messaging driving higher engagement and conversion"
        ],
        "agent_contributions": {
            "market_analysis": "Identified sustainable fashion trend early, enabling first-mover advantage",
            "bid_strategy": "Optimized bids for high-intent keywords, reducing CPA by 18%",
            "creative_optimization": "A/B tested creative elements, identifying winning combinations",
            "orchestration": "Coordinated multi-platform strategy for consistent messaging"
        }
    }
    
    return response


def generate_efficiency_response(efficiency, metrics):
    """Generate response for efficiency queries."""
    
    if not efficiency:
        return {
            "summary": "Efficiency metrics not available yet.",
            "details": {}
        }
    
    return {
        "summary": "Your efficiency metrics have improved significantly since implementing SIGNAL:",
        "improvements": {
            "cpl_reduction": f"{float(efficiency.cpl_reduction) * 100:.1f}%",
            "lead_increase": f"{float(efficiency.lead_increase) * 100:.1f}%",
            "roas_improvement": f"{float(efficiency.roas_improvement) * 100:.1f}%",
            "cac_reduction": f"{float(efficiency.cac_reduction) * 100:.1f}%",
            "ltv_cac_improvement": f"{float(efficiency.ltv_cac_improvement) * 100:.1f}%",
            "retention_improvement": f"{float(efficiency.retention_improvement) * 100:.1f}%",
            "abandonment_reduction": f"{float(efficiency.abandonment_reduction) * 100:.1f}%"
        },
        "before_vs_after": efficiency.metadata,
        "driver_analysis": [
            "AI-driven bid optimization reducing wasted spend",
            "Creative optimization improving engagement and conversion",
            "Strategic budget allocation to high-performing channels",
            "Real-time performance monitoring and adjustment"
        ]
    }


def generate_general_response(client_id, metrics, briefs):
    """Generate general response."""
    
    return {
        "summary": "I'm here to help you optimize your advertising performance. Ask me about specific metrics, recent performance, or strategic recommendations.",
        "available_queries": [
            "What happened in the last two weeks?",
            "Show me efficiency improvements",
            "What are the top performing campaigns?",
            "Recommend budget allocation for next week"
        ],
        "recent_activity": {
            "briefs_generated": len(briefs),
            "metrics_available": len(metrics)
        }
    }


@router.get("/agents/efficiency-metrics")
async def get_efficiency_metrics(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get detailed efficiency metrics with before/after comparison."""
    
    efficiency_result = await session.execute(
        select(EfficiencyMetrics)
        .where(EfficiencyMetrics.client_id == client_id)
        .order_by(EfficiencyMetrics.period_end.desc())
        .limit(1)
    )
    efficiency = efficiency_result.scalar_one_or_none()
    
    if not efficiency:
        raise HTTPException(status_code=404, detail="Efficiency metrics not found")
    
    return {
        "period": {
            "start": efficiency.period_start.isoformat(),
            "end": efficiency.period_end.isoformat()
        },
        "improvements": {
            "cpl_reduction": {
                "value": f"{float(efficiency.cpl_reduction) * 100:.1f}%",
                "before": efficiency.metadata.get("before_signal", {}).get("avg_cpl"),
                "after": efficiency.metadata.get("after_signal", {}).get("avg_cpl"),
                "impact": "Reduced cost per lead by $7.00"
            },
            "lead_increase": {
                "value": f"{float(efficiency.lead_increase) * 100:.1f}%",
                "before": efficiency.metadata.get("before_signal", {}).get("avg_leads_per_week"),
                "after": efficiency.metadata.get("after_signal", {}).get("avg_leads_per_week"),
                "impact": "Generating 320 additional leads per week"
            },
            "roas_improvement": {
                "value": f"{float(efficiency.roas_improvement) * 100:.1f}%",
                "before": efficiency.metadata.get("before_signal", {}).get("avg_roas"),
                "after": efficiency.metadata.get("after_signal", {}).get("avg_roas"),
                "impact": "Improved return on ad spend by 55%"
            },
            "business_kpis": {
                "ltv_cac": {
                    "improvement": f"{float(efficiency.ltv_cac_improvement) * 100:.1f}%",
                    "before": efficiency.metadata.get("before_signal", {}).get("avg_ltv_cac"),
                    "after": efficiency.metadata.get("after_signal", {}).get("avg_ltv_cac")
                },
                "retention_rate": {
                    "improvement": f"{float(efficiency.retention_improvement) * 100:.1f}%",
                    "before": efficiency.metadata.get("before_signal", {}).get("avg_retention"),
                    "after": efficiency.metadata.get("after_signal", {}).get("avg_retention")
                },
                "cart_abandonment": {
                    "reduction": f"{float(efficiency.abandonment_reduction) * 100:.1f}%",
                    "before": efficiency.metadata.get("before_signal", {}).get("avg_abandonment"),
                    "after": efficiency.metadata.get("after_signal", {}).get("avg_abandonment")
                }
            }
        },
        "agent_quality_score": 0.88,
        "optimization_cycles": 5,
        "learning_rate": 0.15
    }


# ============================================================================
# Creative Upload & Placement Management Endpoints
# ============================================================================

@router.get("/creatives")
async def get_creatives(
    client_id: str = Query(..., description="Client ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status"),
    session: AsyncSession = Depends(get_async_session)
):
    """Get all creatives with placement information."""
    
    query = select(Creative).where(Creative.client_id == client_id)
    
    if status:
        query = query.where(Creative.status == status)
    
    query = query.order_by(Creative.created_at.desc())
    
    result = await session.execute(query)
    creatives = result.scalars().all()
    
    # Get placements for each creative
    creative_data = []
    for creative in creatives:
        placements_result = await session.execute(
            select(CreativePlacement)
            .where(CreativePlacement.creative_id == creative.id)
        )
        placements = placements_result.scalars().all()
        
        # Filter by platform if specified
        if platform:
            placements = [p for p in placements if p.platform == platform]
        
        creative_data.append({
            "id": creative.id,
            "name": creative.name,
            "type": creative.creative_type,
            "format": creative.format,
            "status": creative.status,
            "created_at": creative.created_at.isoformat(),
            "metadata": creative.metadata,
            "placements": [
                {
                    "id": placement.id,
                    "platform": placement.platform,
                    "placement": placement.placement,
                    "status": placement.status,
                    "metadata": placement.metadata
                }
                for placement in placements
            ]
        })
    
    return {
        "creatives": creative_data
    }


@router.post("/creatives/upload")
async def upload_creative(
    client_id: str = Query(..., description="Client ID"),
    creative_data: dict = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Upload creative (demo endpoint).
    In production, this would handle actual file uploads.
    """
    
    if not creative_data:
        creative_data = {
            "name": "New Creative Upload",
            "type": "video",
            "format": "vertical",
            "platforms": ["tiktok", "meta"],
            "metadata": {
                "duration": 15,
                "dimensions": "1080x1920"
            }
        }
    
    creative = Creative(
        client_id=client_id,
        name=creative_data.get("name"),
        creative_type=creative_data.get("type"),
        format=creative_data.get("format"),
        status="pending",
        metadata=creative_data.get("metadata", {})
    )
    
    session.add(creative)
    await session.flush()
    await session.refresh(creative)
    
    # Create placements
    platforms = creative_data.get("platforms", [])
    for platform in platforms:
        placement = CreativePlacement(
            creative_id=creative.id,
            platform=platform,
            placement="in_feed" if platform == "tiktok" else "feed",
            status="pending",
            metadata={}
        )
        session.add(placement)
    
    await session.commit()
    
    return {
        "message": "Creative uploaded successfully",
        "creative_id": creative.id,
        "name": creative.name,
        "platforms": platforms,
        "status": "pending"
    }


@router.post("/creatives/bulk-upload")
async def bulk_upload_creatives(
    client_id: str = Query(..., description="Client ID"),
    creative_list: list = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Bulk upload creatives for TikTok and paid social.
    MCP integrations would automatically place these in appropriate placements.
    """
    
    if not creative_list:
        # Demo data for bulk upload
        creative_list = [
            {
                "name": "Summer Collection Video 1",
                "type": "video",
                "format": "vertical",
                "platforms": ["tiktok"],
                "metadata": {"duration": 15, "dimensions": "1080x1920"}
            },
            {
                "name": "Summer Collection Video 2",
                "type": "video",
                "format": "vertical",
                "platforms": ["tiktok"],
                "metadata": {"duration": 20, "dimensions": "1080x1920"}
            },
            {
                "name": "Sustainable Fashion Carousel",
                "type": "carousel",
                "format": "square",
                "platforms": ["meta", "instagram"],
                "metadata": {"card_count": 5, "dimensions": "1080x1080"}
            },
            {
                "name": "Back to School Static",
                "type": "static_image",
                "format": "horizontal",
                "platforms": ["meta", "google"],
                "metadata": {"dimensions": "1200x628"}
            }
        ]
    
    uploaded_creatives = []
    
    for creative_data in creative_list:
        creative = Creative(
            client_id=client_id,
            name=creative_data.get("name"),
            creative_type=creative_data.get("type"),
            format=creative_data.get("format"),
            status="pending",
            metadata=creative_data.get("metadata", {})
        )
        
        session.add(creative)
        await session.flush()
        await session.refresh(creative)
        
        # Create placements via MCP (simulated)
        platforms = creative_data.get("platforms", [])
        for platform in platforms:
            placement = CreativePlacement(
                creative_id=creative.id,
                platform=platform,
                placement="auto",  # MCP auto-placement
                status="pending",
                metadata={
                    "mcp_managed": True,
                    "auto_optimization": True
                }
            )
            session.add(placement)
        
        uploaded_creatives.append({
            "creative_id": creative.id,
            "name": creative.name,
            "platforms": platforms,
            "status": "pending"
        })
    
    await session.commit()
    
    return {
        "message": f"Bulk upload complete: {len(uploaded_creatives)} creatives uploaded",
        "creatives": uploaded_creatives,
        "mcp_integrations": {
            "meta": "Active - auto-placing in feed and story placements",
            "tiktok": "Active - auto-placing in in-feed and top view",
            "google": "Active - auto-placing in display and video"
        }
    }


# ============================================================================
# Keyword Generation Endpoints
# ============================================================================

@router.get("/intelligence/keywords")
async def generate_keywords(
    client_id: str = Query(..., description="Client ID"),
    topic_cluster: str = Query(..., description="Topic cluster to generate keywords for"),
    platform: str = Query("google", description="Target platform (google/microsoft)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Generate keywords for Google Ads and Microsoft based on topic clusters.
    """
    
    # Get topic cluster
    cluster_result = await session.execute(
        select(TopicCluster)
        .where(
            TopicCluster.client_id == client_id,
            TopicCluster.name.ilike(f"%{topic_cluster}%")
        )
    )
    cluster = cluster_result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Topic cluster not found")
    
    # Generate platform-specific keywords
    base_keywords = cluster.keywords
    
    if platform == "google":
        keywords = generate_google_keywords(base_keywords, cluster.name)
    elif platform == "microsoft":
        keywords = generate_microsoft_keywords(base_keywords, cluster.name)
    else:
        keywords = base_keywords
    
    return {
        "topic_cluster": cluster.name,
        "platform": platform,
        "base_keywords": base_keywords,
        "generated_keywords": keywords,
        "search_volume": cluster.search_volume,
        "competition": cluster.competition_score,
        "recommendations": {
            "match_types": ["broad", "phrase", "exact"],
            "negative_keywords": generate_negative_keywords(cluster.name),
            "bid_suggestions": {
                "high_intent": cluster.competition_score * 2.5,
                "medium_intent": cluster.competition_score * 1.8,
                "low_intent": cluster.competition_score * 1.2
            }
        }
    }


def generate_google_keywords(base_keywords, cluster_name):
    """Generate Google Ads specific keywords."""
    
    keywords = []
    
    for keyword in base_keywords:
        keywords.extend([
            keyword,
            f"{keyword} for sale",
            f"buy {keyword}",
            f"best {keyword}",
            f"{keyword} online",
            f"affordable {keyword}",
            f"{keyword} deals",
            f"{keyword} near me"
        ])
    
    # Add cluster-specific variations
    if "sustainable" in cluster_name.lower():
        keywords.extend([
            "eco friendly clothing",
            "ethical fashion brands",
            "sustainable apparel",
            "green fashion",
            "conscious clothing"
        ])
    
    return list(set(keywords))


def generate_microsoft_keywords(base_keywords, cluster_name):
    """Generate Microsoft Ads specific keywords."""
    
    keywords = []
    
    for keyword in base_keywords:
        keywords.extend([
            keyword,
            f"{keyword} shopping",
            f"{keyword} store",
            f"cheap {keyword}",
            f"discount {keyword}",
            f"{keyword} offers"
        ])
    
    # Microsoft-specific variations
    keywords.extend([
        f"{cluster_name} Bing",
        f"{cluster_name} search",
        f"{cluster_name} Microsoft"
    ])
    
    return list(set(keywords))


def generate_negative_keywords(cluster_name):
    """Generate negative keywords to exclude irrelevant traffic."""
    
    base_negatives = [
        "free", "cheap", "wholesale", "bulk", "used", "second hand",
        "repair", "diy", "pattern", "tutorial", "how to make"
    ]
    
    cluster_specific = {
        "sustainable": ["fast fashion", "synthetic", "polyester"],
        "summer": ["winter", "fall", "autumn", "cold weather"],
        "gen z": ["millennial", "baby boomer", "senior"]
    }
    
    for key, values in cluster_specific.items():
        if key in cluster_name.lower():
            base_negatives.extend(values)
    
    return list(set(base_negatives))


# ============================================================================
# Campaign Performance with Business KPIs Endpoints
# ============================================================================

@router.get("/campaigns/performance")
async def get_campaign_performance(
    client_id: str = Query(..., description="Client ID"),
    campaign_id: Optional[str] = Query(None, description="Specific campaign ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get campaign performance with business KPIs that matter:
    LTV:CAC, retention rate, cart abandonment.
    """
    
    query = select(Campaign).where(Campaign.client_id == client_id)
    
    if campaign_id:
        query = query.where(Campaign.id == campaign_id)
    
    query = query.order_by(Campaign.created_at.desc())
    
    result = await session.execute(query)
    campaigns = result.scalars().all()
    
    campaign_data = []
    
    for campaign in campaigns:
        # Get performance data
        perf_result = await session.execute(
            select(CampaignPerformance)
            .where(CampaignPerformance.campaign_id == campaign.id)
            .order_by(CampaignPerformance.date.desc())
            .limit(30)
        )
        performance_data = perf_result.scalars().all()
        
        # Calculate aggregates
        if performance_data:
            total_impressions = sum(p.impressions for p in performance_data)
            total_clicks = sum(p.clicks for p in performance_data)
            total_conversions = sum(p.conversions for p in performance_data)
            total_spend = sum(p.spend for p in performance_data)
            total_revenue = sum(p.revenue for p in performance_data)
            
            avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
            avg_cpa = total_spend / total_conversions if total_conversions > 0 else 0
            avg_roas = total_revenue / total_spend if total_spend > 0 else 0
        else:
            total_impressions = total_clicks = total_conversions = 0
            total_spend = total_revenue = Decimal("0")
            avg_ctr = avg_cpa = avg_roas = 0
        
        # Business KPIs (simulated based on campaign performance)
        ltv_cac = 4.1 if avg_roas > 3.0 else 3.2
        retention_rate = 0.78 if avg_roas > 3.0 else 0.68
        cart_abandonment = 0.58 if avg_roas > 3.0 else 0.72
        
        campaign_data.append({
            "id": campaign.id,
            "name": campaign.name,
            "platform": campaign.platform,
            "type": campaign.campaign_type,
            "status": campaign.status,
            "period": {
                "start": campaign.start_date.isoformat(),
                "end": campaign.end_date.isoformat()
            },
            "budget": {
                "daily": float(campaign.daily_budget),
                "total": float(campaign.total_budget)
            },
            "performance": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "spend": float(total_spend),
                "revenue": float(total_revenue),
                "ctr": round(avg_ctr, 4),
                "cpa": round(float(avg_cpa), 2),
                "roas": round(float(avg_roas), 2)
            },
            "business_kpis": {
                "ltv_cac": round(ltv_cac, 2),
                "retention_rate": round(retention_rate, 4),
                "cart_abandonment": round(cart_abandonment, 4)
            },
            "target_audience": campaign.target_audience
        })
    
    return {
        "campaigns": campaign_data
    }


@router.get("/campaigns/business-kpis")
async def get_business_kpis(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get aggregated business KPIs across all campaigns.
    Shows how agents learn to optimize towards business goals.
    """
    
    # Get efficiency metrics
    efficiency_result = await session.execute(
        select(EfficiencyMetrics)
        .where(EfficiencyMetrics.client_id == client_id)
        .order_by(EfficiencyMetrics.period_end.desc())
        .limit(1)
    )
    efficiency = efficiency_result.scalar_one_or_none()
    
    # Get all campaigns
    campaigns_result = await session.execute(
        select(Campaign).where(Campaign.client_id == client_id)
    )
    campaigns = campaigns_result.scalars().all()
    
    # Calculate aggregate performance
    total_spend = Decimal("0")
    total_revenue = Decimal("0")
    total_conversions = 0
    
    for campaign in campaigns:
        perf_result = await session.execute(
            select(CampaignPerformance)
            .where(CampaignPerformance.campaign_id == campaign.id)
            .order_by(CampaignPerformance.date.desc())
            .limit(30)
        )
        performance_data = perf_result.scalars().all()
        
        for perf in performance_data:
            total_spend += perf.spend
            total_revenue += perf.revenue
            total_conversions += perf.conversions
    
    overall_roas = float(total_revenue / total_spend) if total_spend > 0 else 0
    
    return {
        "summary": {
            "total_campaigns": len(campaigns),
            "active_campaigns": sum(1 for c in campaigns if c.status == "active"),
            "total_spend": float(total_spend),
            "total_revenue": float(total_revenue),
            "overall_roas": round(overall_roas, 2)
        },
        "business_kpis": {
            "ltv_cac": {
                "current": 4.1,
                "target": 5.0,
                "improvement": "+28%",
                "trend": "improving"
            },
            "retention_rate": {
                "current": 0.78,
                "target": 0.85,
                "improvement": "+15%",
                "trend": "improving"
            },
            "cart_abandonment": {
                "current": 0.58,
                "target": 0.50,
                "improvement": "-19%",
                "trend": "improving"
            },
            "customer_lifetime_value": {
                "current": 233.33,
                "target": 280.00,
                "improvement": "+18%",
                "trend": "improving"
            }
        },
        "agent_optimization": {
            "learning_progress": "Agents have learned to optimize toward your business goals",
            "goal_alignment": {
                "lead_generation": "Optimizing for CPL reduction and lead volume",
                "customer_acquisition": "Optimizing for CAC reduction and quality",
                "revenue": "Optimizing for ROAS and LTV:CAC improvement",
                "retention": "Optimizing for cart abandonment reduction"
            },
            "adaptive_behavior": "As your business grows, agents automatically adjust optimization strategies to maintain alignment with your evolving goals"
        },
        "improvement_timeline": efficiency.metadata if efficiency else {}
    }


# ============================================================================
# Channel Mapping Endpoints
# ============================================================================

@router.get("/planning/channel-mappings")
async def get_channel_mappings(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all channel mappings showing how channels map to funnel stages.
    
    Returns the mapping of marketing channels (Meta, Google, TikTok, etc.) to funnel stages
    (awareness, consideration, performance) with their characteristics.
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


@router.post("/planning/channel-mappings")
async def create_channel_mapping(
    client_id: str = Query(..., description="Client ID"),
    channel_name: str = Query(..., description="Channel name (meta, google, tiktok, etc.)"),
    funnel_stage: str = Query(..., description="Funnel stage (awareness, consideration, performance)"),
    default_weight: float = Query(0.3, description="Default allocation weight"),
    typical_cpa: float = Query(25.0, description="Typical cost per acquisition"),
    typical_conversion_rate: float = Query(0.03, description="Typical conversion rate"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new channel mapping.
    
    Maps a marketing channel to a funnel stage with performance characteristics.
    """
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


@router.get("/planning/funnel-stages")
async def get_funnel_stages(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all funnel stage definitions.
    
    Returns the available funnel stages (awareness, consideration, performance) with their characteristics.
    """
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


# ============================================================================
# DisBERT Thrad Classification Integration Endpoints
# ============================================================================

@router.get("/classification/disbert-keywords")
async def get_disbert_keyword_strategy(
    client_id: str = Query(..., description="Client ID"),
    classification: str = Query(..., description="DisBERT classification (A-M)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get Google Ads keyword strategy for a DisBERT Thrad classification.
    
    Returns whether the classification should be used as keywords,
    along with keywords, negative keywords, and bid adjustments.
    """
    from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator, DisBERTThradClassification
    
    integrator = DisBERTThradAdIntegrator()
    
    try:
        classification_enum = DisBERTThradClassification(classification)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid classification. Must be one of: A, B, C, D, E, F, G, H, I, J, K, L, M"
        )
    
    strategy = integrator.get_google_ads_keywords_for_classification(classification_enum)
    
    if not strategy:
        return {
            "classification": classification,
            "use_as_keywords": False,
            "reason": "Classification not used for Google Ads keywords (low commercial value or blocked)"
        }
    
    return {
        "classification": classification,
        "classification_name": strategy.classification_name,
        "use_as_keywords": True,
        "keywords": strategy.keywords,
        "negative_keywords": strategy.negative_keywords,
        "bid_multiplier": strategy.bid_multiplier,
        "commercial_intent": strategy.commercial_intent,
        "recommended_action": "USE in Google Ads campaigns"
    }


@router.get("/classification/ingestion-rules")
async def get_disbert_ingestion_rules(
    client_id: str = Query(..., description="Client ID"),
    classification: str = Query(..., description="DisBERT classification (A-M)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get Thrad platform ingestion rule for a DisBERT classification.
    
    Returns whether the classification should be ingested back into the platform,
    priority, content type, and filtering rules.
    """
    from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator, DisBERTThradClassification
    
    integrator = DisBERTThradAdIntegrator()
    
    try:
        classification_enum = DisBERTThradClassification(classification)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid classification. Must be one of: A, B, C, D, E, F, G, H, I, J, K, L, M"
        )
    
    rule = integrator.get_ingestion_rule_for_classification(classification_enum)
    
    if not rule:
        return {
            "classification": classification,
            "should_ingest": False,
            "reason": "Classification not ingested into Thrad platform"
        }
    
    return {
        "classification": classification,
        "classification_name": rule.classification_name,
        "should_ingest": True,
        "ingestion_priority": rule.ingestion_priority,
        "content_type": rule.content_type,
        "ad_usage": rule.ad_usage,
        "filtering_rules": rule.filtering_rules,
        "priority_level": "HIGHEST" if rule.ingestion_priority >= 10 else "HIGH" if rule.ingestion_priority >= 8 else "MEDIUM" if rule.ingestion_priority >= 5 else "LOW"
    }


@router.get("/classification/high-priority-ingestion")
async def get_high_priority_ingestion(
    client_id: str = Query(..., description="Client ID"),
    min_priority: int = Query(8, description="Minimum priority level (8-10 recommended)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get high-priority classifications for Thrad platform ingestion.
    
    By default (min_priority=8), returns:
    - J (relationships_and_personal_reflection) - Priority 10
    - E (general_guidance_and_info) - Priority 9
    - H (purchasable_products) - Priority 8
    """
    from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator
    
    integrator = DisBERTThradAdIntegrator()
    high_priority = integrator.get_high_priority_ingestion_classifications(min_priority)
    
    return {
        "min_priority": min_priority,
        "high_priority_classifications": [
            {
                "classification": rule.classification.value,
                "classification_name": rule.classification_name,
                "priority": rule.ingestion_priority,
                "content_type": rule.content_type,
                "ad_usage": rule.ad_usage,
                "filtering_rules": rule.filtering_rules,
                "priority_level": "HIGHEST" if rule.ingestion_priority >= 10 else "HIGH"
            }
            for rule in high_priority
        ],
        "total": len(high_priority),
        "summary": f"Found {len(high_priority)} classifications with priority >= {min_priority}"
    }


@router.post("/classification/classify-query")
async def classify_user_query(
    client_id: str = Query(..., description="Client ID"),
    query: str = Query(..., description="User query to classify"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Classify a user query using DisBERT Thrad classification system.
    
    Returns the classification (A-M) and associated keyword/ingestion strategies.
    """
    from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator
    
    integrator = DisBERTThradAdIntegrator()
    classification = integrator.classify_query_with_disbert(query)
    
    # Get keyword strategy
    keyword_strategy = integrator.get_google_ads_keywords_for_classification(classification)
    
    # Get ingestion rule
    ingestion_rule = integrator.get_ingestion_rule_for_classification(classification)
    
    return {
        "query": query,
        "classification": classification.value,
        "classification_name": keyword_strategy.classification_name if keyword_strategy else "Blocked",
        "google_ads_strategy": {
            "use_as_keywords": keyword_strategy.use_as_keywords if keyword_strategy else False,
            "keywords": keyword_strategy.keywords if keyword_strategy else [],
            "bid_multiplier": keyword_strategy.bid_multiplier if keyword_strategy else 0,
            "commercial_intent": keyword_strategy.commercial_intent if keyword_strategy else 0
        } if keyword_strategy else None,
        "thrad_ingestion": {
            "should_ingest": ingestion_rule.should_ingest if ingestion_rule else False,
            "priority": ingestion_rule.ingestion_priority if ingestion_rule else 0,
            "content_type": ingestion_rule.content_type if ingestion_rule else "none",
            "ad_usage": ingestion_rule.ad_usage if ingestion_rule else "none"
        } if ingestion_rule else None
    }


@router.post("/classification/generate-campaign")
async def generate_campaign_from_classifications(
    client_id: str = Query(..., description="Client ID"),
    classifications: str = Query(..., description="Comma-separated classifications (e.g., H,E,J,F)"),
    budget: float = Query(500.0, description="Campaign budget"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Generate Google Ads campaign targeting specific DisBERT classifications.
    
    Example: classifications=H,E,J,F targets purchasable_products, general_guidance,
    relationships, and programming.
    """
    from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator, DisBERTThradClassification
    
    integrator = DisBERTThradAdIntegrator()
    
    # Parse classifications
    classification_list = []
    for c in classifications.split(','):
        c = c.strip().upper()
        try:
            classification_list.append(DisBERTThradClassification(c))
        except ValueError:
            continue
    
    if not classification_list:
        raise HTTPException(
            status_code=400,
            detail=f"No valid classifications provided. Use: A, B, C, D, E, F, G, H, I, J, K, L, M"
        )
    
    campaign = integrator.generate_google_ads_campaign_from_disbert(
        target_classifications=classification_list,
        budget=budget
    )
    
    return campaign


@router.get("/classification/all-strategies")
async def get_all_classification_strategies(
    client_id: str = Query(..., description="Client ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all DisBERT Thrad classification strategies.
    
    Returns keyword strategies and ingestion rules for all classifications (A-M).
    """
    from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator, DisBERTThradClassification
    
    integrator = DisBERTThradAdIntegrator()
    
    all_strategies = []
    
    for classification in DisBERTThradClassification:
        keyword_strategy = integrator.get_google_ads_keywords_for_classification(classification)
        ingestion_rule = integrator.get_ingestion_rule_for_classification(classification)
        
        all_strategies.append({
            "classification": classification.value,
            "classification_name": keyword_strategy.classification_name if keyword_strategy else "Blocked",
            "google_ads": {
                "use_as_keywords": keyword_strategy.use_as_keywords if keyword_strategy else False,
                "keyword_count": len(keyword_strategy.keywords) if keyword_strategy else 0,
                "bid_multiplier": keyword_strategy.bid_multiplier if keyword_strategy else 0,
                "commercial_intent": keyword_strategy.commercial_intent if keyword_strategy else 0
            } if keyword_strategy else None,
            "thrad_ingestion": {
                "should_ingest": ingestion_rule.should_ingest if ingestion_rule else False,
                "priority": ingestion_rule.ingestion_priority if ingestion_rule else 0,
                "content_type": ingestion_rule.content_type if ingestion_rule else "none",
                "ad_usage": ingestion_rule.ad_usage if ingestion_rule else "none"
            } if ingestion_rule else None
        })
    
    return {
        "total_classifications": len(all_strategies),
        "strategies": all_strategies,
        "summary": {
            "used_for_keywords": len([s for s in all_strategies if s["google_ads"] and s["google_ads"]["use_as_keywords"]]),
            "ingested_into_platform": len([s for s in all_strategies if s["thrad_ingestion"] and s["thrad_ingestion"]["should_ingest"]]),
            "high_priority_ingestion": len([s for s in all_strategies if s["thrad_ingestion"] and s["thrad_ingestion"]["priority"] >= 8])
        }
    }


# ============================================================================
# Intelligence-to-Activation Pipeline Endpoints
# ============================================================================

@router.post("/intelligence/complete-pipeline")
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
    from services.intelligence.tavily_client import TavilyClient
    from services.intelligence.thrad_bert_client import ThradBERTClient
    from services.platform_integration.google_ads_manager import GoogleAdsManager, IntelligenceToActivationPipeline
    
    # Initialize clients
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


@router.post("/intelligence/tavily-to-keywords")
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
    from services.intelligence.tavily_client import TavilyClient
    from services.intelligence.thrad_bert_client import ThradBERTClient
    
    # Initialize clients
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


@router.post("/intelligence/create-google-campaign")
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
    from services.platform_integration.google_ads_manager import GoogleAdsManager
    
    if not keywords:
        # Generate default keywords for demo
        keywords = [
            "gym wear", "workout clothes", "athletic apparel", "training gear",
            "fitness clothing", "gym outfits", "workout gear", "gym clothes",
            "athletic wear", "fitness apparel", "training clothes", "gym attire"
        ]
    
    # Initialize Google Ads manager
    google_ads_manager = GoogleAdsManager(demo_mode=True)
    
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


@router.get("/intelligence/campaign-performance")
async def get_campaign_performance(
    client_id: str = Query(..., description="Client ID"),
    campaign_id: str = Query(..., description="Google Ads campaign ID"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get performance data for a Google Ads campaign.
    
    Returns impressions, clicks, conversions, ROAS, and other metrics.
    """
    from services.platform_integration.google_ads_manager import GoogleAdsManager
    
    google_ads_manager = GoogleAdsManager(demo_mode=True)
    
    performance = google_ads_manager.get_campaign_performance(campaign_id)
    
    return performance


@router.post("/intelligence/optimize-keywords")
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
    from services.platform_integration.google_ads_manager import GoogleAdsManager
    from services.intelligence.thrad_bert_client import ThradBERTClient
    
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


# ============================================================================
# Advanced Predictive Modeling Endpoints
# ============================================================================

@router.post("/planning/predict-scenario")
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
    Advanced scenario prediction with LOESS modeling, adstock saturation, and Overmind evaluation.
    
    Returns comprehensive predictions including:
    - LOESS-based lead predictions
    - Incremental value analysis
    - Adstock saturation and refresh recommendations
    - Overmind evaluation score
    - Token reward/penalty calculations
    """
    from services.planning import ScenarioModelingEngine, FunnelAllocation
    from services.planning.predictive_modeling import PredictiveModelingEngine
    
    # Calculate channel allocations
    scenario_engine = ScenarioModelingEngine()
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    scenario = scenario_engine.model_scenario(
        total_budget=Decimal(str(total_budget)),
        funnel_allocation=allocation,
        selected_channels=["meta", "google", "tiktok", "microsoft"]
    )
    
    # Convert to channel budget dict
    channel_allocations = {
        alloc.channel.value: float(alloc.budget)
        for alloc in scenario.channel_allocations
    }
    
    # Get current performance for context
    current_performance = {
        "current_cpl": 28.0,
        "previous_cpl": 35.0,
        "current_roas": 3.25,
        "previous_roas": 2.10
    }
    
    # Mock days since refresh for each channel
    days_since_refresh = {
        "meta": 14,
        "google": 7,
        "tiktok": 21,
        "microsoft": 10
    }
    
    # Calculate advanced predictions
    predictive_engine = PredictiveModelingEngine()
    
    prediction = predictive_engine.calculate_scenario_prediction(
        funnel_allocation={
            "awareness": awareness,
            "consideration": consideration,
            "performance": performance
        },
        total_budget=total_budget,
        channel_allocations=channel_allocations,
        client_targets={
            "target_leads": target_leads,
            "target_cpa": target_cpa
        },
        current_performance=current_performance,
        days_since_refresh=days_since_refresh
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
            "predicted_leads": prediction.predicted_leads,
            "incremental_leads": prediction.incremental_leads,
            "confidence_level": prediction.confidence_level,
            "target_achievement": round(prediction.predicted_leads / target_leads, 2)
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
            for channel, pred in prediction.channel_predictions.items()
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
            for sat in prediction.adstock_analysis
        ],
        "overmind_evaluation": {
            "score": prediction.overmind_score,
            "assessment": "Strong alignment" if prediction.overmind_score > 0.8 else "Needs optimization" if prediction.overmind_score > 0.6 else "Poor alignment"
        },
        "token_outcome": {
            "reward": prediction.token_reward,
            "penalty": prediction.token_penalty,
            "net_tokens": prediction.token_reward - prediction.token_penalty
        },
        "optimization_recommendations": prediction.optimization_recommendations
    }


@router.get("/planning/loess-prediction")
async def get_loess_prediction(
    client_id: str = Query(..., description="Client ID"),
    channel: str = Query(..., description="Channel name"),
    budget: float = Query(..., description="Budget amount"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get LOESS-based prediction for a single channel.
    
    Returns predicted leads, confidence intervals, and incremental value analysis.
    """
    from services.planning.predictive_modeling import PredictiveModelingEngine
    
    engine = PredictiveModelingEngine()
    prediction = engine.calculate_loess_prediction(channel, budget)
    
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


@router.get("/planning/adstock-saturation")
async def get_adstock_saturation(
    client_id: str = Query(..., description="Client ID"),
    channel: str = Query(..., description="Channel name"),
    days_since_refresh: int = Query(14, description="Days since creative refresh"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get adstock saturation analysis for a channel.
    
    Returns current saturation, decay rate, and refresh recommendations.
    """
    from services.planning.predictive_modeling import PredictiveModelingEngine
    
    engine = PredictiveModelingEngine()
    saturation = engine.analyze_adstock_saturation(channel, days_since_refresh)
    
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


@router.post("/planning/realtime-prediction")
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
    from services.planning.predictive_modeling import PredictiveModelingEngine
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
        selected_channels=["meta", "google", "tiktok", "microsoft"]
    )
    
    # Quick LOESS predictions
    predictive_engine = PredictiveModelingEngine()
    channel_predictions = {}
    
    for alloc in scenario.channel_allocations:
        prediction = predictive_engine.calculate_loess_prediction(
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


# ============================================================================
# Scenario Modeling Endpoints
# ============================================================================

@router.get("/planning/funnel-allocation")
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
        "risk_score": 5.2,  # Calculated risk score
        "description": "Current allocation balanced between brand building and performance"
    }


@router.post("/planning/funnel-allocation")
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
    """
    # Validate allocation sums to 100
    total = awareness + consideration + performance
    if not (99 <= total <= 101):  # Allow small rounding errors
        raise HTTPException(
            status_code=400,
            detail=f"Allocation must sum to 100%, got {total}%"
        )
    
    # Import scenario modeling engine
    from services.planning import ScenarioModelingEngine, FunnelAllocation
    
    engine = ScenarioModelingEngine()
    
    # Create funnel allocation
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    # Calculate scenario with default budget
    from decimal import Decimal
    scenario = engine.model_scenario(
        total_budget=Decimal("3500.00"),  # Weekly budget
        funnel_allocation=allocation,
        selected_channels=["meta", "google", "tiktok", "microsoft"]
    )
    
    return {
        "updated_allocation": {
            "awareness": awareness,
            "consideration": consideration,
            "performance": performance
        },
        "scenario_result": {
            "expected_leads": scenario.expected_leads,
            "expected_revenue": float(scenario.expected_revenue),
            "expected_roas": scenario.expected_roas,
            "risk_score": scenario.risk_score,
            "confidence": scenario.confidence
        },
        "channel_allocations": [
            {
                "channel": alloc.channel.value,
                "budget": float(alloc.budget),
                "expected_leads": alloc.expected_leads,
                "funnel_stage": alloc.funnel_stage.value
            }
            for alloc in scenario.channel_allocations
        ],
        "recommendations": scenario.recommendations
    }


@router.get("/planning/recommendations")
async def get_allocation_recommendations(
    client_id: str = Query(..., description="Client ID"),
    goal: str = Query("customer_acquisition", description="Business goal"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get AI-powered allocation recommendations based on business goals.
    
    Provides intelligent suggestions for optimal funnel allocation.
    """
    # Get client info
    client_result = await session.execute(
        select(Client).where(Client.id == client_id)
    )
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Import recommendation engine
    from services.planning import RecommendationEngine, ClientContext, BusinessGoal
    
    engine = RecommendationEngine()
    
    # Create client context
    context = ClientContext(
        industry=client.industry,
        business_goal=BusinessGoal(goal),
        current_budget=Decimal("3500.00"),
        target_leads=1000,
        target_cpa=Decimal("25.0"),
        seasonality="peak"  # Summer peak for fitness
    )
    
    # Generate recommendation
    recommendation = engine.generate_recommendation(context)
    
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


@router.post("/planning/allocate-budget")
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
    """
    from services.planning import ScenarioModelingEngine, FunnelAllocation
    from decimal import Decimal
    
    engine = ScenarioModelingEngine()
    
    allocation = FunnelAllocation(
        awareness=awareness,
        consideration=consideration,
        performance=performance
    )
    
    scenario = engine.model_scenario(
        total_budget=Decimal(str(total_budget)),
        funnel_allocation=allocation,
        selected_channels=["meta", "google", "tiktok", "microsoft"]
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


@router.get("/intelligence/realtime-keywords")
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
    from services.intelligence.tavily_client import TavilyClient
    from services.platform_integration.google_ads import GoogleAdsClient
    
    # Initialize Tavily client
    tavily_client = TavilyClient()
    enhanced_client = EnhancedTavilyClient(tavily_client)
    
    # Generate keywords using enhanced Tavily
    positive_keywords, negative_keywords = await enhanced_client.generate_seo_keywords(
        topic=topic,
        location="US",
        language="en"
    )
    
    # Initialize Google Ads client for additional data
    google_client = GoogleAdsClient(demo_mode=True)
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


@router.post("/creatives/mcp-distribute")
async def distribute_creatives_mcp(
    client_id: str = Query(..., description="Client ID"),
    creatives: List[dict] = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Distribute creatives across platforms using MCP connectors.
    
    Bulk creative placement via MCP integrations (demo mode).
    """
    from services.platform_integration.mcp_connectors import MCPPlacementManager
    
    if not creatives:
        raise HTTPException(status_code=400, detail="No creatives provided")
    
    manager = MCPPlacementManager(demo_mode=True)
    
    # Distribute all creatives
    results = await manager.bulk_distribute_creatives(creatives)
    
    # Summarize results
    summary = {
        "total_creatives": len(creatives),
        "successful_placements": 0,
        "failed_placements": 0,
        "platform_results": {}
    }
    
    for creative_id, platform_results in results.items():
        for platform, result in platform_results.items():
            platform_name = platform.value
            if platform_name not in summary["platform_results"]:
                summary["platform_results"][platform_name] = {
                    "success": 0,
                    "failed": 0,
                    "placements": []
                }
            
            if result.success:
                summary["successful_placements"] += 1
                summary["platform_results"][platform_name]["success"] += 1
            else:
                summary["failed_placements"] += 1
                summary["platform_results"][platform_name]["failed"] += 1
            
            summary["platform_results"][platform_name]["placements"].append({
                "creative_id": creative_id,
                "status": result.success,
                "message": result.message,
                "placement_count": len(result.placements)
            })
    
    return {
        "summary": summary,
        "detailed_results": results,
        "mcp_status": "demo_mode",
        "distributed_at": datetime.now().isoformat()
    }