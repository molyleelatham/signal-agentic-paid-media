"""
Recommendation Engine for Goal-Based Budget Allocation

This module provides intelligent recommendations for marketing budget allocation
based on client goals, historical performance, and market conditions.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal

from .scenario_model import (
    FunnelStage, FunnelAllocation, ChannelType, 
    ScenarioModelingEngine, ScenarioResult
)


class BusinessGoal(Enum):
    """Primary business goals for marketing."""
    CUSTOMER_ACQUISITION = "customer_acquisition"
    BRAND_AWARENESS = "brand_awareness"
    RETENTION = "retention"
    REVENUE_GROWTH = "revenue_growth"
    MARKET_SHARE = "market_share"
    LEAD_GENERATION = "lead_generation"


@dataclass
class AllocationRecommendation:
    """Recommended allocation with reasoning."""
    funnel_allocation: FunnelAllocation
    recommended_channels: List[ChannelType]
    reasoning: str
    expected_outcomes: Dict[str, float]
    risk_assessment: str
    confidence: float
    alternatives: List[Dict]


@dataclass
class ClientContext:
    """Client context for recommendations."""
    industry: str
    business_goal: BusinessGoal
    current_budget: Decimal
    target_leads: Optional[int] = None
    target_cpa: Optional[Decimal] = None
    target_roas: Optional[float] = None
    historical_performance: Optional[Dict[ChannelType, Dict]] = None
    market_conditions: Optional[Dict] = None
    seasonality: Optional[str] = None


class RecommendationEngine:
    """
    Engine for generating intelligent budget allocation recommendations.
    
    Uses business goals, historical performance, and market conditions to suggest
    optimal marketing funnel allocations (awareness/consideration/performance).
    """
    
    # Goal-based allocation templates
    GOAL_ALLOCATION_TEMPLATES = {
        BusinessGoal.CUSTOMER_ACQUISITION: {
            "allocation": FunnelAllocation(awareness=20, consideration=30, performance=50),
            "reasoning": "Focus on performance marketing with strong consideration to drive conversions",
            "primary_channels": [ChannelType.GOOGLE, ChannelType.META, ChannelType.MICROSOFT],
            "secondary_channels": [ChannelType.REDDIT, ChannelType.INSTAGRAM],
            "expected_cpa_improvement": -0.15,  # 15% reduction
            "time_to_results": "short"
        },
        BusinessGoal.BRAND_AWARENESS: {
            "allocation": FunnelAllocation(awareness=60, consideration=30, performance=10),
            "reasoning": "Heavy investment in awareness to build brand recognition and consideration",
            "primary_channels": [ChannelType.TIKTOK, ChannelType.INSTAGRAM, ChannelType.OOH],
            "secondary_channels": [ChannelType.META, ChannelType.PINTEREST],
            "expected_cpa_improvement": 0.10,  # 10% increase (trade-off for awareness)
            "time_to_results": "long"
        },
        BusinessGoal.RETENTION: {
            "allocation": FunnelAllocation(awareness=20, consideration=50, performance=30),
            "reasoning": "Focus on consideration and relationship building to retain existing customers",
            "primary_channels": [ChannelType.META, ChannelType.INSTAGRAM, ChannelType.EMAIL],
            "secondary_channels": [ChannelType.REDDIT, ChannelType.LINKEDIN],
            "expected_cpa_improvement": -0.25,  # 25% reduction (retention is cheaper)
            "time_to_results": "medium"
        },
        BusinessGoal.REVENUE_GROWTH: {
            "allocation": FunnelAllocation(awareness=25, consideration=25, performance=50),
            "reasoning": "Balanced approach with emphasis on performance to drive immediate revenue",
            "primary_channels": [ChannelType.GOOGLE, ChannelType.META, ChannelType.MICROSOFT],
            "secondary_channels": [ChannelType.TIKTOK, ChannelType.INSTAGRAM],
            "expected_cpa_improvement": -0.10,  # 10% reduction
            "time_to_results": "short"
        },
        BusinessGoal.MARKET_SHARE: {
            "allocation": FunnelAllocation(awareness=50, consideration=30, performance=20),
            "reasoning": "Aggressive awareness to capture market, with consideration for differentiation",
            "primary_channels": [ChannelType.TIKTOK, ChannelType.OOH, ChannelType.META],
            "secondary_channels": [ChannelType.INSTAGRAM, ChannelType.SNAPCHAT],
            "expected_cpa_improvement": 0.05,  # 5% increase (investment for share)
            "time_to_results": "medium"
        },
        BusinessGoal.LEAD_GENERATION: {
            "allocation": FunnelAllocation(awareness=15, consideration=35, performance=50),
            "reasoning": "Strong focus on performance and consideration to maximize lead volume",
            "primary_channels": [ChannelType.GOOGLE, ChannelType.META, ChannelType.LINKEDIN],
            "secondary_channels": [ChannelType.MICROSOFT, ChannelType.REDDIT],
            "expected_cpa_improvement": -0.20,  # 20% reduction
            "time_to_results": "short"
        }
    }
    
    # Industry-specific adjustments
    INDUSTRY_ADJUSTMENTS = {
        "fashion_ecommerce": {
            "awareness_boost": 10,  # Fashion needs more awareness
            "preferred_channels": [ChannelType.INSTAGRAM, ChannelType.TIKTOK, ChannelType.PINTEREST],
            "seasonality_impact": "high"
        },
        "b2b_saaS": {
            "consideration_boost": 15,  # B2B needs more consideration/education
            "preferred_channels": [ChannelType.LINKEDIN, ChannelType.GOOGLE, ChannelType.MICROSOFT],
            "seasonality_impact": "low"
        },
        "food_beverage": {
            "awareness_boost": 15,
            "preferred_channels": [ChannelType.INSTAGRAM, ChannelType.TIKTOK, ChannelType.META],
            "seasonality_impact": "medium"
        },
        "finance": {
            "consideration_boost": 20,
            "preferred_channels": [ChannelType.GOOGLE, ChannelType.LINKEDIN, ChannelType.MICROSOFT],
            "seasonality_impact": "low"
        }
    }
    
    def __init__(self, scenario_engine: Optional[ScenarioModelingEngine] = None):
        """
        Initialize the recommendation engine.
        
        Args:
            scenario_engine: Scenario modeling engine (creates default if not provided)
        """
        self.scenario_engine = scenario_engine or ScenarioModelingEngine()
    
    def generate_recommendation(
        self,
        context: ClientContext
    ) -> AllocationRecommendation:
        """
        Generate allocation recommendation based on client context.
        
        Args:
            context: Client context including goals, budget, and performance
        
        Returns:
            Detailed allocation recommendation
        """
        # Get base allocation template for goal
        template = self.GOAL_ALLOCATION_TEMPLATES[context.business_goal]
        base_allocation = template["allocation"]
        
        # Apply industry-specific adjustments
        adjusted_allocation = self._apply_industry_adjustments(
            base_allocation,
            context.industry
        )
        
        # Apply seasonality adjustments
        if context.seasonality:
            adjusted_allocation = self._apply_seasonality_adjustments(
                adjusted_allocation,
                context.seasonality
            )
        
        # Select channels based on goal and industry
        recommended_channels = self._select_channels(
            context.business_goal,
            context.industry,
            template["primary_channels"],
            template["secondary_channels"]
        )
        
        # Apply historical performance adjustments
        if context.historical_performance:
            adjusted_allocation = self._apply_historical_adjustments(
                adjusted_allocation,
                context.historical_performance
            )
        
        # Generate scenario to validate recommendation
        scenario_result = self.scenario_engine.model_scenario(
            total_budget=context.current_budget,
            funnel_allocation=adjusted_allocation,
            selected_channels=recommended_channels,
            historical_performance=context.historical_performance
        )
        
        # Build reasoning
        reasoning = self._build_reasoning(
            context,
            template,
            adjusted_allocation,
            scenario_result
        )
        
        # Calculate expected outcomes
        expected_outcomes = self._calculate_expected_outcomes(
            scenario_result,
            template,
            context
        )
        
        # Risk assessment
        risk_assessment = self._assess_risk(adjusted_allocation, scenario_result)
        
        # Generate alternatives
        alternatives = self._generate_alternatives(
            context,
            adjusted_allocation,
            recommended_channels
        )
        
        return AllocationRecommendation(
            funnel_allocation=adjusted_allocation,
            recommended_channels=recommended_channels,
            reasoning=reasoning,
            expected_outcomes=expected_outcomes,
            risk_assessment=risk_assessment,
            confidence=scenario_result.confidence,
            alternatives=alternatives
        )
    
    def _apply_industry_adjustments(
        self,
        allocation: FunnelAllocation,
        industry: str
    ) -> FunnelAllocation:
        """Apply industry-specific adjustments to allocation."""
        adjustments = self.INDUSTRY_ADJUSTMENTS.get(industry, {})
        
        awareness = allocation.awareness + adjustments.get("awareness_boost", 0)
        consideration = allocation.consideration + adjustments.get("consideration_boost", 0)
        performance = allocation.performance - adjustments.get("awareness_boost", 0) - adjustments.get("consideration_boost", 0)
        
        # Ensure all values are non-negative and sum to 100
        total = awareness + consideration + performance
        if total != 100:
            # Normalize to 100
            awareness = (awareness / total) * 100
            consideration = (consideration / total) * 100
            performance = (performance / total) * 100
        
        return FunnelAllocation(
            awareness=round(awareness),
            consideration=round(consideration),
            performance=round(performance)
        )
    
    def _apply_seasonality_adjustments(
        self,
        allocation: FunnelAllocation,
        seasonality: str
    ) -> FunnelAllocation:
        """Apply seasonality-based adjustments."""
        seasonality_adjustments = {
            "peak": {"awareness": 5, "consideration": -5, "performance": 0},  # Peak season: more awareness
            "off_peak": {"awareness": -5, "consideration": 5, "performance": 0},  # Off-peak: more consideration
            "holiday": {"awareness": 10, "consideration": -5, "performance": -5}  # Holiday: heavy awareness
        }
        
        adjustments = seasonality_adjustments.get(seasonality, {})
        
        awareness = allocation.awareness + adjustments.get("awareness", 0)
        consideration = allocation.consideration + adjustments.get("consideration", 0)
        performance = allocation.performance + adjustments.get("performance", 0)
        
        # Normalize to 100
        total = awareness + consideration + performance
        if total != 100:
            awareness = (awareness / total) * 100
            consideration = (consideration / total) * 100
            performance = (performance / total) * 100
        
        return FunnelAllocation(
            awareness=round(awareness),
            consideration=round(consideration),
            performance=round(performance)
        )
    
    def _select_channels(
        self,
        goal: BusinessGoal,
        industry: str,
        primary_channels: List[ChannelType],
        secondary_channels: List[ChannelType]
    ) -> List[ChannelType]:
        """Select recommended channels based on goal and industry."""
        # Start with primary channels
        selected = list(primary_channels)
        
        # Add industry-preferred channels
        industry_prefs = self.INDUSTRY_ADJUSTMENTS.get(industry, {}).get("preferred_channels", [])
        for channel in industry_prefs:
            if channel not in selected:
                selected.append(channel)
        
        # Add some secondary channels for diversification
        for channel in secondary_channels[:2]:  # Top 2 secondary
            if channel not in selected:
                selected.append(channel)
        
        return selected
    
    def _apply_historical_adjustments(
        self,
        allocation: FunnelAllocation,
        historical_performance: Dict[ChannelType, Dict]
    ) -> FunnelAllocation:
        """Adjust allocation based on historical performance."""
        # Calculate performance scores by channel
        channel_scores = {}
        for channel, perf in historical_performance.items():
            # Score based on ROAS and conversion rate
            roas = perf.get("roas", 2.0)
            conversion_rate = perf.get("conversion_rate", 0.03)
            score = roas * conversion_rate * 100
            channel_scores[channel] = score
        
        if not channel_scores:
            return allocation
        
        # Get funnel stage for each channel
        from .scenario_model import ScenarioModelingEngine
        engine = ScenarioModelingEngine()
        
        # Calculate average performance by funnel stage
        stage_scores = {stage: [] for stage in FunnelStage}
        for channel, score in channel_scores.items():
            mapping = engine.channel_mappings.get(channel)
            if mapping:
                stage_scores[mapping.funnel_stage].append(score)
        
        stage_avg_scores = {
            stage: sum(scores) / len(scores) if scores else 1.0
            for stage, scores in stage_scores.items()
        }
        
        # Adjust allocation based on performance
        total_score = sum(stage_avg_scores.values())
        if total_score == 0:
            return allocation
        
        awareness = (stage_avg_scores[FunnelStage.AWARENESS] / total_score) * 100
        consideration = (stage_avg_scores[FunnelStage.CONSIDERATION] / total_score) * 100
        performance = (stage_avg_scores[FunnelStage.PERFORMANCE] / total_score) * 100
        
        # Blend with original allocation (70% original, 30% performance-based)
        final_awareness = round(allocation.awareness * 0.7 + awareness * 0.3)
        final_consideration = round(allocation.consideration * 0.7 + consideration * 0.3)
        final_performance = 100 - final_awareness - final_consideration
        
        return FunnelAllocation(
            awareness=final_awareness,
            consideration=final_consideration,
            performance=final_performance
        )
    
    def _build_reasoning(
        self,
        context: ClientContext,
        template: Dict,
        allocation: FunnelAllocation,
        scenario: ScenarioResult
    ) -> str:
        """Build detailed reasoning for recommendation."""
        reasoning_parts = [
            f"Based on your goal of {context.business_goal.value.replace('_', ' ')}, "
            f"we recommend a {allocation.performance}% performance / "
            f"{allocation.consideration}% consideration / "
            f"{allocation.awareness}% awareness allocation."
        ]
        
        reasoning_parts.append(template["reasoning"])
        
        if context.industry in self.INDUSTRY_ADJUSTMENTS:
            reasoning_parts.append(
                f"Adjusted for {context.industry.replace('_', ' ')} industry specifics."
            )
        
        if context.seasonality:
            reasoning_parts.append(
                f"Seasonality adjustment applied for {context.seasonality} period."
            )
        
        reasoning_parts.append(
            f"Expected results: {scenario.expected_leads} leads, "
            f"${scenario.expected_revenue:,.2f} revenue, "
            f"{scenario.expected_roas:.2f}x ROAS."
        )
        
        return " ".join(reasoning_parts)
    
    def _calculate_expected_outcomes(
        self,
        scenario: ScenarioResult,
        template: Dict,
        context: ClientContext
    ) -> Dict[str, float]:
        """Calculate expected outcomes."""
        cpa_improvement = template["expected_cpa_improvement"]
        
        outcomes = {
            "expected_leads": scenario.expected_leads,
            "expected_revenue": float(scenario.expected_revenue),
            "expected_roas": scenario.expected_roas,
            "cpa_improvement_percent": cpa_improvement * 100,
            "risk_score": scenario.risk_score,
            "confidence": scenario.confidence,
            "time_to_results": template["time_to_results"]
        }
        
        if context.target_leads:
            outcomes["target_achievement"] = scenario.expected_leads / context.target_leads
        
        if context.target_cpa:
            avg_cpa = float(scenario.total_budget / scenario.expected_leads) if scenario.expected_leads > 0 else 0
            outcomes["target_cpa_achievement"] = context.target_cpa / avg_cpa if avg_cpa > 0 else 0
        
        return outcomes
    
    def _assess_risk(
        self,
        allocation: FunnelAllocation,
        scenario: ScenarioResult
    ) -> str:
        """Generate risk assessment."""
        if scenario.risk_score < 3:
            return "Low risk: Conservative allocation with stable expected returns"
        elif scenario.risk_score < 6:
            return "Medium risk: Balanced allocation with moderate risk/reward"
        elif scenario.risk_score < 8:
            return "Medium-high risk: Performance-focused with higher volatility"
        else:
            return "High risk: Aggressive performance allocation with high potential but significant volatility"
    
    def _generate_alternatives(
        self,
        context: ClientContext,
        current_allocation: FunnelAllocation,
        current_channels: List[ChannelType]
    ) -> List[Dict]:
        """Generate alternative allocation strategies."""
        alternatives = []
        
        # Conservative alternative (more awareness)
        conservative = FunnelAllocation(
            awareness=min(current_allocation.awareness + 15, 70),
            consideration=max(current_allocation.consideration - 10, 10),
            performance=max(current_allocation.performance - 5, 10)
        )
        
        conservative_scenario = self.scenario_engine.model_scenario(
            total_budget=context.current_budget,
            funnel_allocation=conservative,
            selected_channels=current_channels
        )
        
        alternatives.append({
            "name": "Conservative",
            "allocation": {"awareness": conservative.awareness, "consideration": conservative.consideration, "performance": conservative.performance},
            "expected_leads": conservative_scenario.expected_leads,
            "expected_roas": conservative_scenario.expected_roas,
            "risk_score": conservative_scenario.risk_score,
            "description": "Lower risk, more brand building, slower conversion"
        })
        
        # Aggressive alternative (more performance)
        aggressive = FunnelAllocation(
            awareness=max(current_allocation.awareness - 10, 5),
            consideration=max(current_allocation.consideration - 5, 10),
            performance=min(current_allocation.performance + 15, 80)
        )
        
        aggressive_scenario = self.scenario_engine.model_scenario(
            total_budget=context.current_budget,
            funnel_allocation=aggressive,
            selected_channels=current_channels
        )
        
        alternatives.append({
            "name": "Aggressive",
            "allocation": {"awareness": aggressive.awareness, "consideration": aggressive.consideration, "performance": aggressive.performance},
            "expected_leads": aggressive_scenario.expected_leads,
            "expected_roas": aggressive_scenario.expected_roas,
            "risk_score": aggressive_scenario.risk_score,
            "description": "Higher risk, focus on immediate conversions"
        })
        
        return alternatives