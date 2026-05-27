"""
Demo API routes for Acme fashion e-commerce client.
Endpoints to support the hackathon demonstration scenario.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from shared.database import get_async_session
from shared.models.client import Client, ClientGoal, ClientPlatform
from shared.models.campaign import Campaign, CampaignPerformance
from shared.models.content import ContentBrief, TopicCluster
from shared.models.analytics import (
    PerformanceMetric, BudgetAllocation, 
    AttentionTokenTransaction, EfficiencyMetrics
)
from shared.models.creative import Creative, CreativePlacement


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
    client_id: str = Query(..., description="Client ID"),
    message: str = Query(..., description="User message to agents"),
    session: AsyncSession = Depends(get_async_session)
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
    
    return {
        "user_message": message,
        "agent_response": response,
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