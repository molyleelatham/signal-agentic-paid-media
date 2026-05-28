"""
Unified Planning Service

This module provides a single entry point for the Planning flow,
combining scenario modeling, recommendation engine, and predictive modeling.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal
import logging

from .scenario_model import (
    ScenarioModelingEngine,
    FunnelStageEnum,
    ChannelType,
    FunnelAllocation,
    ScenarioResult
)
from .recommendation_engine import (
    RecommendationEngine,
    BusinessGoal,
    ClientContext,
    AllocationRecommendation
)
from .predictive_modeling import (
    PredictiveModelingEngine,
    SplinePrediction,
    ScenarioPrediction
)
from services.common.adstock_decay import AdstockDecayEngine, AdstockSaturation

logger = logging.getLogger(__name__)


@dataclass
class AllocationPlan:
    """Complete allocation plan from Planning flow."""
    funnel_allocation: FunnelAllocation
    scenario_result: ScenarioResult
    channel_allocations: Dict[str, float]
    expected_leads: int
    expected_revenue: float
    risk_score: float
    confidence: float
    recommendations: List[str]


@dataclass
class PlanningOutput:
    """Complete output from Planning flow."""
    allocation_plan: AllocationPlan
    prediction: ScenarioPrediction
    adstock_analysis: List[AdstockSaturation]
    token_outcome: Dict[str, float]


class PlanningService:
    """
    Unified Planning Service for the Planning flow.
    
    Combines:
    - Scenario Modeling Engine
    - Recommendation Engine
    - Predictive Modeling (Spline Predictions)
    - Adstock Analysis
    
    Provides single entry point for generating allocation plans.
    """
    
    def __init__(self):
        """Initialize Planning Service with all planning engines."""
        self.scenario_engine = ScenarioModelingEngine()
        self.recommendation_engine = RecommendationEngine()
        self.predictive_engine = PredictiveModelingEngine()
        self.adstock_engine = AdstockDecayEngine()
    
    async def generate_allocation_plan(
        self,
        client_context: ClientContext,
        total_budget: Decimal,
        funnel_allocation: Optional[FunnelAllocation] = None,
        selected_channels: Optional[List[ChannelType]] = None
    ) -> AllocationPlan:
        """
        Generate a complete allocation plan.
        
        Args:
            client_context: Client context with goals and targets
            total_budget: Total budget to allocate
            funnel_allocation: Optional funnel allocation (will use recommendations if not provided)
            selected_channels: Optional list of channels to include
        
        Returns:
            Complete allocation plan with scenario results
        """
        # Get recommendation if funnel allocation not provided
        if funnel_allocation is None:
            recommendation = self.recommendation_engine.generate_recommendation(client_context)
            funnel_allocation = recommendation.funnel_allocation
            selected_channels = recommendation.recommended_channels
        
        if selected_channels is None:
            selected_channels = [
                ChannelType.META,
                ChannelType.GOOGLE,
                ChannelType.TIKTOK,
                ChannelType.MICROSOFT
            ]
        
        # Model scenario with allocation
        scenario_result = self.scenario_engine.model_scenario(
            total_budget=total_budget,
            funnel_allocation=funnel_allocation,
            selected_channels=selected_channels
        )
        
        # Calculate channel allocations
        channel_allocations = {
            alloc.channel.value: float(alloc.budget)
            for alloc in scenario_result.channel_allocations
        }
        
        # Calculate expected leads
        expected_leads = scenario_result.expected_leads
        expected_revenue = float(scenario_result.expected_revenue)
        
        return AllocationPlan(
            funnel_allocation=funnel_allocation,
            scenario_result=scenario_result,
            channel_allocations=channel_allocations,
            expected_leads=expected_leads,
            expected_revenue=expected_revenue,
            risk_score=scenario_result.risk_score,
            confidence=scenario_result.confidence,
            recommendations=scenario_result.recommendations
        )
    
    async def generate_complete_planning_output(
        self,
        client_context: ClientContext,
        total_budget: Decimal,
        funnel_allocation: Optional[FunnelAllocation] = None,
        selected_channels: Optional[List[ChannelType]] = None,
        days_since_refresh: Optional[Dict[str, int]] = None
    ) -> PlanningOutput:
        """
        Generate complete Planning output with predictions and adstock analysis.
        
        Args:
            client_context: Client context
            total_budget: Total budget
            funnel_allocation: Optional funnel allocation
            selected_channels: Optional channels
            days_since_refresh: Days since creative refresh per channel
        
        Returns:
            Complete Planning output including allocation, predictions, and adstock
        """
        # Generate allocation plan
        allocation_plan = await self.generate_allocation_plan(
            client_context=client_context,
            total_budget=total_budget,
            funnel_allocation=funnel_allocation,
            selected_channels=selected_channels
        )
        
        # Convert to channel budget dict for prediction
        channel_budgets = {
            channel: budget
            for channel, budget in allocation_plan.channel_allocations.items()
        }
        
        # Set default days since refresh if not provided
        if days_since_refresh is None:
            days_since_refresh = {
                "meta": 14,
                "google": 7,
                "tiktok": 21,
                "microsoft": 10
            }
        
        # Calculate scenario prediction
        prediction = self.predictive_engine.calculate_scenario_prediction(
            funnel_allocation={
                "awareness": allocation_plan.funnel_allocation.awareness,
                "consideration": allocation_plan.funnel_allocation.consideration,
                "performance": allocation_plan.funnel_allocation.performance
            },
            total_budget=float(total_budget),
            channel_allocations=channel_budgets,
            client_targets={
                "target_leads": client_context.target_leads,
                "target_cpa": float(client_context.target_cpa)
            },
            current_performance={
                "current_cpa": 28.0,
                "previous_cpa": 35.0,
                "current_roas": 3.25,
                "previous_roas": 2.10
            },
            days_since_refresh=days_since_refresh
        )
        
        # Analyze adstock saturation
        adstock_analysis = []
        for channel, days in days_since_refresh.items():
            # Get decay lambda from historical performance
            decay_lambda = self.predictive_engine.historical_performance.get(
                channel, {}
            ).get("decay_lambda", 0.7)
            
            saturation = self.adstock_engine.analyze_saturation(
                channel=channel,
                days_since_refresh=days,
                decay_lambda=decay_lambda
            )
            adstock_analysis.append(saturation)
        
        # Calculate token outcome
        token_outcome = {
            "reward": prediction.token_reward,
            "penalty": prediction.token_penalty,
            "net_tokens": prediction.token_reward - prediction.token_penalty
        }
        
        return PlanningOutput(
            allocation_plan=allocation_plan,
            prediction=prediction,
            adstock_analysis=adstock_analysis,
            token_outcome=token_outcome
        )
    
    def get_recommendation(
        self,
        client_context: ClientContext
    ) -> AllocationRecommendation:
        """
        Get AI-powered allocation recommendation.
        
        Args:
            client_context: Client context
        
        Returns:
            Allocation recommendation
        """
        return self.recommendation_engine.generate_recommendation(client_context)