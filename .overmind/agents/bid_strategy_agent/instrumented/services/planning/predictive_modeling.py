"""
Predictive Modeling for Scenario Builder

This module adds LOESS-based lead prediction, adstock saturation modeling,
and incremental value calculation to the scenario modeling engine.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d
from scipy.stats import norm
import logging

from services.common.adstock_decay import AdstockDecayEngine, AdstockSaturation

logger = logging.getLogger(__name__)


@dataclass
class SplinePrediction:
    """Spline-based prediction result (using cubic spline interpolation)."""
    predicted_leads: int
    confidence_interval: Tuple[float, float]
    incremental_value: int  # Additional leads from this allocation
    saturation_level: float  # 0-1, how saturated the channel is
    adstock_remaining: float  # Remaining adstock effectiveness
    refresh_recommendation: str  # When to refresh creative


@dataclass
class ScenarioPrediction:
    """Complete scenario prediction with all metrics."""
    funnel_allocation: Dict[str, float]
    predicted_leads: int
    incremental_leads: int  # vs baseline
    confidence_level: float
    adstock_analysis: List[AdstockSaturation]
    channel_predictions: Dict[str, SplinePrediction]
    overmind_score: float  # Overmind evaluation score
    token_reward: float  # Expected token reward
    token_penalty: float  # Expected token penalty
    optimization_recommendations: List[str]


class PredictiveModelingEngine:
    """
    Advanced predictive modeling for scenario building.
    
    Uses LOESS regression for lead prediction, adstock modeling for saturation,
    and integrates with Overmind for real-time optimization.
    """
    
    def __init__(self, overmind_tracer=None):
        """
        Initialize predictive modeling engine.
        
        Args:
            overmind_tracer: Overmind tracer for evaluation and optimization
        """
        self.overmind_tracer = overmind_tracer
        self.adstock_engine = AdstockDecayEngine()  # Use unified adstock engine
        
        # Historical performance data for LOESS modeling (demo data)
        self.historical_performance = {
            "meta": {
                "budgets": np.array([500, 750, 1000, 1250, 1500, 1750, 2000]),
                "leads": np.array([80, 115, 150, 180, 205, 225, 240]),
                "decay_rate": 0.7
            },
            "google": {
                "budgets": np.array([400, 600, 800, 1000, 1200, 1400, 1600]),
                "leads": np.array([75, 110, 145, 175, 200, 220, 235]),
                "decay_rate": 0.65
            },
            "tiktok": {
                "budgets": np.array([300, 450, 600, 750, 900, 1050, 1200]),
                "leads": np.array([50, 75, 95, 110, 120, 128, 132]),
                "decay_rate": 0.8
            },
            "microsoft": {
                "budgets": np.array([200, 300, 400, 500, 600, 700, 800]),
                "leads": np.array([40, 55, 70, 82, 90, 96, 100]),
                "decay_rate": 0.75
            }
        }
    
    def calculate_spline_prediction(
        self,
        channel: str,
        budget: float,
        historical_data: Optional[Dict] = None
    ) -> SplinePrediction:
        """
        Calculate spline-based lead prediction for a channel using cubic spline interpolation.
        
        Args:
            channel: Channel name
            budget: Budget amount
            historical_data: Optional historical performance data
        
        Returns:
            Spline prediction with confidence intervals and saturation analysis
        """
        data = historical_data or self.historical_performance.get(channel, {})
        
        if not data or len(data.get("budgets", [])) < 3:
            # Fallback to linear prediction if insufficient data
            return self._fallback_prediction(channel, budget)
        
        budgets = data["budgets"]
        leads = data["leads"]
        decay_rate = data.get("decay_rate", 0.7)
        
        # Fit cubic spline interpolation for smooth curve fitting
        try:
            # Use spline interpolation for smooth curve fitting
            spline = interp1d(budgets, leads, kind='cubic', fill_value='extrapolate')
            predicted_leads = max(0, int(spline(budget)))
            
            # Calculate saturation (diminishing returns)
            max_observed_budget = max(budgets)
            max_observed_leads = max(leads)
            saturation_level = min(1.0, budget / (max_observed_budget * 1.5))
            
            # Calculate adstock remaining
            adstock_remaining = (1 - saturation_level) ** decay_rate
            
            # Confidence interval based on distance from observed data
            min_budget, max_budget = min(budgets), max(budgets)
            if min_budget <= budget <= max_budget:
                confidence = 0.85  # Higher confidence within observed range
            else:
                confidence = 0.65  # Lower confidence for extrapolation
            
            # Calculate confidence interval
            std_error = max(5, predicted_leads * 0.1)  # 10% standard error
            confidence_interval = (
                max(0, predicted_leads - 1.96 * std_error),
                predicted_leads + 1.96 * std_error
            )
            
            # Calculate incremental value vs baseline (50% of current budget)
            baseline_budget = budget * 0.5
            baseline_leads = max(0, int(spline(baseline_budget)))
            incremental_value = predicted_leads - baseline_leads
            
            # Refresh recommendation based on saturation
            if saturation_level > 0.8:
                refresh_recommendation = "immediate"
            elif saturation_level > 0.6:
                refresh_recommendation = "soon"
            else:
                refresh_recommendation = "monitor"
            
            return SplinePrediction(
                predicted_leads=predicted_leads,
                confidence_interval=confidence_interval,
                incremental_value=incremental_value,
                saturation_level=saturation_level,
                adstock_remaining=adstock_remaining,
                refresh_recommendation=refresh_recommendation
            )
            
        except Exception as e:
            logger.error(f"Spline prediction failed for {channel}: {e}")
            return self._fallback_prediction(channel, budget)
    
    def _fallback_prediction(self, channel: str, budget: float) -> SplinePrediction:
        """Fallback linear prediction when spline interpolation fails."""
        # Simple linear model: leads = budget * conversion_rate
        conversion_rates = {
            "meta": 0.16,  # ~$6.25 per lead
            "google": 0.18,  # ~$5.55 per lead
            "tiktok": 0.12,  # ~$8.33 per lead
            "microsoft": 0.15  # ~$6.67 per lead
        }
        
        conv_rate = conversion_rates.get(channel, 0.15)
        predicted_leads = int(budget * conv_rate)
        
        return SplinePrediction(
            predicted_leads=predicted_leads,
            confidence_interval=(predicted_leads * 0.8, predicted_leads * 1.2),
            incremental_value=int(predicted_leads * 0.5),
            saturation_level=0.5,
            adstock_remaining=0.7,
            refresh_recommendation="monitor"
        )
    
    def analyze_adstock_saturation(
        self,
        channel: str,
        days_since_refresh: int,
        historical_performance: Optional[Dict] = None
    ) -> AdstockSaturation:
        """
        Analyze adstock saturation and recommend refresh timing.
        
        Uses unified adstock decay engine for consistency with Media Buying flow.
        
        Args:
            channel: Channel name
            days_since_refresh: Days since creative was last refreshed
            historical_data: Historical performance data
        
        Returns:
            Adstock saturation analysis with refresh recommendations
        """
        data = historical_performance or self.historical_performance.get(channel, {})
        decay_rate = data.get("decay_rate", 0.7)
        
        # Use unified adstock engine
        return self.adstock_engine.analyze_saturation(
            channel=channel,
            days_since_refresh=days_since_refresh,
            decay_rate=decay_rate,
            historical_performance=historical_performance
        )
    
    def calculate_scenario_prediction(
        self,
        funnel_allocation: Dict[str, float],
        total_budget: float,
        channel_allocations: Dict[str, float],
        client_targets: Dict[str, float],
        current_performance: Dict[str, float],
        days_since_refresh: Dict[str, int]
    ) -> ScenarioPrediction:
        """
        Calculate complete scenario prediction with all advanced metrics.
        
        Args:
            funnel_allocation: Funnel stage allocation percentages
            total_budget: Total budget
            channel_allocations: Budget per channel
            client_targets: Client targets (leads, cpa, etc.)
            current_performance: Current performance metrics
            days_since_refresh: Days since creative refresh per channel
        
        Returns:
            Complete scenario prediction with LOESS, adstock, Overmind, and token metrics
        """
        # Calculate LOESS predictions for each channel
        channel_predictions = {}
        total_predicted_leads = 0
        
        for channel, budget in channel_allocations.items():
            prediction = self.calculate_loess_prediction(channel, budget)
            channel_predictions[channel] = prediction
            total_predicted_leads += prediction.predicted_leads
        
        # Calculate baseline (current allocation)
        baseline_leads = sum(
            self.calculate_loess_prediction(ch, budget * 0.5).predicted_leads
            for ch, budget in channel_allocations.items()
        )
        incremental_leads = total_predicted_leads - baseline_leads
        
        # Analyze adstock saturation
        adstock_analysis = []
        for channel, days in days_since_refresh.items():
            saturation = self.analyze_adstock_saturation(channel, days)
            adstock_analysis.append(saturation)
        
        # Calculate Overmind score (demo implementation)
        overmind_score = self._calculate_overmind_score(
            funnel_allocation,
            total_predicted_leads,
            client_targets,
            current_performance
        )
        
        # Calculate token rewards/penalties
        token_reward, token_penalty = self._calculate_token_outcome(
            total_predicted_leads,
            client_targets.get("target_leads", 1000),
            client_targets.get("target_cpa", 25.0),
            total_budget,
            overmind_score
        )
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            channel_predictions,
            adstock_analysis,
            overmind_score,
            client_targets
        )
        
        return ScenarioPrediction(
            funnel_allocation=funnel_allocation,
            predicted_leads=total_predicted_leads,
            incremental_leads=incremental_leads,
            confidence_level=0.78,  # Overall confidence
            adstock_analysis=adstock_analysis,
            channel_predictions=channel_predictions,
            overmind_score=overmind_score,
            token_reward=token_reward,
            token_penalty=token_penalty,
            optimization_recommendations=recommendations
        )
    
    def _calculate_overmind_score(
        self,
        funnel_allocation: Dict[str, float],
        predicted_leads: int,
        client_targets: Dict[str, float],
        current_performance: Dict[str, float]
    ) -> float:
        """
        Calculate Overmind evaluation score for the scenario.
        
        Simulates Overmind's evaluation of the scenario quality.
        """
        target_leads = client_targets.get("target_leads", 1000)
        
        # Lead achievement score (0-1)
        lead_score = min(1.0, predicted_leads / target_leads)
        
        # Funnel balance score (prefer balanced allocation)
        awareness = funnel_allocation.get("awareness", 0)
        consideration = funnel_allocation.get("consideration", 0)
        performance = funnel_allocation.get("performance", 0)
        
        # Penalize extreme allocations
        balance_penalty = 0
        if awareness > 70 or consideration > 70 or performance > 70:
            balance_penalty = 0.2
        elif awareness < 10 or consideration < 10 or performance < 10:
            balance_penalty = 0.1
        
        balance_score = 1.0 - balance_penalty
        
        # Historical improvement score
        current_cpa = current_performance.get("current_cpa", 35.0)
        previous_cpa = current_performance.get("previous_cpa", 35.0)
        improvement_score = min(1.0, (previous_cpa - current_cpa) / previous_cpa) if previous_cpa > 0 else 0
        
        # Overall Overmind score
        overmind_score = (lead_score * 0.5 + balance_score * 0.3 + improvement_score * 0.2)
        
        return round(overmind_score, 3)
    
    def _calculate_token_outcome(
        self,
        predicted_leads: int,
        target_leads: float,
        target_cpa: float,
        total_budget: float,
        overmind_score: float
    ) -> Tuple[float, float]:
        """
        Calculate token reward and penalty based on scenario performance.
        
        Args:
            predicted_leads: Predicted leads from scenario
            target_leads: Target leads
            target_cpa: Target CPA
            total_budget: Total budget
            overmind_score: Overmind evaluation score
        
        Returns:
            Tuple of (token_reward, token_penalty)
        """
        # Calculate actual CPA
        actual_cpa = total_budget / predicted_leads if predicted_leads > 0 else float('inf')
        
        # Base reward from lead achievement
        lead_achievement = min(1.0, predicted_leads / target_leads)
        base_reward = lead_achievement * 50  # Up to 50 tokens for lead achievement
        
        # Bonus for beating CPA target
        cpa_bonus = 0
        if actual_cpa <= target_cpa:
            cpa_savings = (target_cpa - actual_cpa) / target_cpa
            cpa_bonus = cpa_savings * 30  # Up to 30 tokens for CPA efficiency
        
        # Overmind multiplier (higher score = higher multiplier)
        overmind_multiplier = 1.0 + (overmind_score * 0.5)
        
        total_reward = (base_reward + cpa_bonus) * overmind_multiplier
        
        # Calculate penalty if targets not met
        penalty = 0
        if predicted_leads < target_leads * 0.8:  # Less than 80% of target
            penalty = (target_leads - predicted_leads) / target_leads * 20  # Penalty for missing target
        elif actual_cpa > target_cpa * 1.2:  # More than 120% of target CPA
            penalty = ((actual_cpa / target_cpa) - 1.2) * 15  # Penalty for high CPA
        
        return round(total_reward, 2), round(penalty, 2)
    
    def _generate_optimization_recommendations(
        self,
        channel_predictions: Dict[str, SplinePrediction],
        adstock_analysis: List[AdstockSaturation],
        overmind_score: float,
        client_targets: Dict[str, float]
    ) -> List[str]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        # Adstock refresh recommendations
        urgent_refreshes = [a for a in adstock_analysis if a.refresh_urgency == "immediate"]
        if urgent_refreshes:
            channels = ", ".join([a.channel for a in urgent_refreshes])
            recommendations.append(f"Immediate creative refresh recommended for: {channels}")
        
        # Saturation-based budget adjustments
        saturated_channels = [
            ch for ch, pred in channel_predictions.items() 
            if pred.saturation_level > 0.75
        ]
        if saturated_channels:
            channels = ", ".join(saturated_channels)
            recommendations.append(f"Consider reducing budget for saturated channels: {channels}")
        
        # High incremental value channels
        high_incremental = [
            ch for ch, pred in channel_predictions.items()
            if pred.incremental_value > 20
        ]
        if high_incremental:
            channels = ", ".join(high_incremental)
            recommendations.append(f"Increase allocation to high-incremental channels: {channels}")
        
        # Overmind-based recommendations
        if overmind_score < 0.6:
            recommendations.append("Overmind recommends rebalancing funnel allocation for better performance")
        elif overmind_score > 0.8:
            recommendations.append("Overmind indicates strong scenario alignment with goals")
        
        # Target-based recommendations
        target_leads = client_targets.get("target_leads", 1000)
        total_predicted = sum(pred.predicted_leads for pred in channel_predictions.values())
        
        if total_predicted < target_leads:
            deficit = target_leads - total_predicted
            recommendations.append(f"Increase budget by ~${deficit * 25:.0f} to meet lead target")
        
        return recommendations