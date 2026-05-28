"""
Scenario Modeling Engine for Funnel Stage Allocation

This module provides a portfolio-style allocation system for marketing funnel stages
(awareness, consideration, performance) similar to stock/bond allocation in investment portfolios.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import math


class FunnelStageEnum(Enum):
    """Marketing funnel stages (Enum to avoid conflict with database model)."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    PERFORMANCE = "performance"


class ChannelType(Enum):
    """Marketing channel types."""
    META = "meta"
    GOOGLE = "google"
    TIKTOK = "tiktok"
    MICROSOFT = "microsoft"
    REDDIT = "reddit"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    OOH = "ooh"  # Out-of-home
    OFFLINE = "offline"  # Offline events, sponsorships, etc.


@dataclass
class ChannelMapping:
    """Mapping of channels to funnel stages."""
    channel: ChannelType
    funnel_stage: FunnelStageEnum
    default_allocation_weight: float  # Default weight within the funnel stage
    typical_cpa: Decimal  # Typical cost per acquisition
    typical_conversion_rate: float


@dataclass
class FunnelAllocation:
    """Allocation across funnel stages."""
    awareness: float  # Percentage (0-100)
    consideration: float  # Percentage (0-100)
    performance: float  # Percentage (0-100)
    
    def __post_init__(self):
        """Validate that allocation sums to 100."""
        total = self.awareness + self.consideration + self.performance
        if not math.isclose(total, 100.0, rel_tol=0.01):
            raise ValueError(f"Funnel allocation must sum to 100%, got {total}%")


@dataclass
class BudgetAllocation:
    """Budget allocation by channel."""
    channel: ChannelType
    budget: Decimal
    funnel_stage: FunnelStageEnum
    expected_leads: int
    expected_cpa: Decimal
    risk_level: str  # low, medium, high


@dataclass
class ScenarioResult:
    """Result of scenario modeling."""
    funnel_allocation: FunnelAllocation
    channel_allocations: List[BudgetAllocation]
    total_budget: Decimal
    expected_leads: int
    expected_revenue: Decimal
    expected_roas: float
    risk_score: float
    confidence: float
    recommendations: List[str]


class ScenarioModelingEngine:
    """
    Engine for modeling marketing budget scenarios across funnel stages.
    
    Similar to investment portfolio allocation, allows adjusting the mix of
    awareness (like bonds - stable, long-term), consideration (like balanced funds),
    and performance (like stocks - higher risk, higher return).
    """
    
    # Default channel mappings to funnel stages
    DEFAULT_CHANNEL_MAPPINGS = {
        ChannelType.META: ChannelMapping(
            channel=ChannelType.META,
            funnel_stage=FunnelStageEnum.CONSIDERATION,
            default_allocation_weight=0.3,
            typical_cpa=Decimal("25.00"),
            typical_conversion_rate=0.035
        ),
        ChannelType.GOOGLE: ChannelMapping(
            channel=ChannelType.GOOGLE,
            funnel_stage=FunnelStageEnum.PERFORMANCE,
            default_allocation_weight=0.4,
            typical_cpa=Decimal("22.00"),
            typical_conversion_rate=0.045
        ),
        ChannelType.TIKTOK: ChannelMapping(
            channel=ChannelType.TIKTOK,
            funnel_stage=FunnelStageEnum.AWARENESS,
            default_allocation_weight=0.5,
            typical_cpa=Decimal("18.00"),
            typical_conversion_rate=0.025
        ),
        ChannelType.MICROSOFT: ChannelMapping(
            channel=ChannelType.MICROSOFT,
            funnel_stage=FunnelStageEnum.PERFORMANCE,
            default_allocation_weight=0.3,
            typical_cpa=Decimal("28.00"),
            typical_conversion_rate=0.040
        ),
        ChannelType.REDDIT: ChannelMapping(
            channel=ChannelType.REDDIT,
            funnel_stage=FunnelStageEnum.CONSIDERATION,
            default_allocation_weight=0.2,
            typical_cpa=Decimal("20.00"),
            typical_conversion_rate=0.030
        ),
        ChannelType.INSTAGRAM: ChannelMapping(
            channel=ChannelType.INSTAGRAM,
            funnel_stage=FunnelStageEnum.AWARENESS,
            default_allocation_weight=0.3,
            typical_cpa=Decimal("22.00"),
            typical_conversion_rate=0.028
        ),
        ChannelType.LINKEDIN: ChannelMapping(
            channel=ChannelType.LINKEDIN,
            funnel_stage=FunnelStageEnum.CONSIDERATION,
            default_allocation_weight=0.2,
            typical_cpa=Decimal("45.00"),
            typical_conversion_rate=0.025
        ),
        ChannelType.OOH: ChannelMapping(
            channel=ChannelType.OOH,
            funnel_stage=FunnelStageEnum.AWARENESS,
            default_allocation_weight=0.2,
            typical_cpa=Decimal("50.00"),
            typical_conversion_rate=0.010
        ),
        ChannelType.OFFLINE: ChannelMapping(
            channel=ChannelType.OFFLINE,
            funnel_stage=FunnelStageEnum.AWARENESS,
            default_allocation_weight=0.0,
            typical_cpa=Decimal("75.00"),
            typical_conversion_rate=0.005
        ),
    }
    
    # Funnel stage characteristics (risk/return profiles)
    FUNNEL_STAGE_PROFILES = {
        FunnelStageEnum.AWARENESS: {
            "risk_level": "low",
            "expected_roi_range": (1.5, 2.5),
            "time_to_conversion": "long",
            "description": "Brand building and reach, stable long-term impact"
        },
        FunnelStageEnum.CONSIDERATION: {
            "risk_level": "medium",
            "expected_roi_range": (2.0, 3.5),
            "time_to_conversion": "medium",
            "description": "Nurturing and education, balanced risk/return"
        },
        FunnelStageEnum.PERFORMANCE: {
            "risk_level": "high",
            "expected_roi_range": (2.5, 5.0),
            "time_to_conversion": "short",
            "description": "Direct response and conversion, higher risk/reward"
        }
    }
    
    def __init__(self, channel_mappings: Optional[Dict[ChannelType, ChannelMapping]] = None):
        """
        Initialize the scenario modeling engine.
        
        Args:
            channel_mappings: Custom channel mappings (uses defaults if not provided)
        """
        self.channel_mappings = channel_mappings or self.DEFAULT_CHANNEL_MAPPINGS
    
    def calculate_channel_allocation(
        self,
        total_budget: Decimal,
        funnel_allocation: FunnelAllocation,
        selected_channels: Optional[List[ChannelType]] = None,
        historical_performance: Optional[Dict[ChannelType, Dict]] = None
    ) -> List[BudgetAllocation]:
        """
        Calculate budget allocation across channels based on funnel allocation.
        
        Args:
            total_budget: Total budget to allocate
            funnel_allocation: Funnel stage allocation percentages
            selected_channels: Channels to include (uses all if not provided)
            historical_performance: Historical performance data for adjustments
        
        Returns:
            List of budget allocations per channel
        """
        selected_channels = selected_channels or list(self.channel_mappings.keys())
        historical_performance = historical_performance or {}
        
        allocations = []
        
        # Calculate budget per funnel stage
        awareness_budget = total_budget * (Decimal(str(funnel_allocation.awareness)) / Decimal("100"))
        consideration_budget = total_budget * (Decimal(str(funnel_allocation.consideration)) / Decimal("100"))
        performance_budget = total_budget * (Decimal(str(funnel_allocation.performance)) / Decimal("100"))
        
        funnel_budgets = {
            FunnelStageEnum.AWARENESS: awareness_budget,
            FunnelStageEnum.CONSIDERATION: consideration_budget,
            FunnelStageEnum.PERFORMANCE: performance_budget
        }
        
        # Allocate budget within each funnel stage
        for stage in [FunnelStageEnum.AWARENESS, FunnelStageEnum.CONSIDERATION, FunnelStageEnum.PERFORMANCE]:
            stage_channels = [
                ch for ch in selected_channels 
                if self.channel_mappings[ch].funnel_stage == stage
            ]
            
            if not stage_channels:
                continue
            
            stage_budget = funnel_budgets[stage]
            
            # Get total weights for this stage
            total_weight = sum(
                self.channel_mappings[ch].default_allocation_weight 
                for ch in stage_channels
            )
            
            # Allocate budget to each channel
            for channel in stage_channels:
                mapping = self.channel_mappings[channel]
                
                # Calculate base allocation
                weight = mapping.default_allocation_weight
                base_allocation = stage_budget * (Decimal(str(weight)) / Decimal(str(total_weight)))
                
                # Adjust based on historical performance if available
                if channel in historical_performance:
                    perf = historical_performance[channel]
                    performance_multiplier = Decimal(str(perf.get("performance_multiplier", 1.0)))
                    base_allocation *= performance_multiplier
                
                # Calculate expected leads and CPA
                typical_cpa = mapping.typical_cpa
                if channel in historical_performance:
                    typical_cpa = Decimal(str(historical_performance[channel].get("actual_cpa", typical_cpa)))
                
                expected_leads = int(base_allocation / typical_cpa)
                expected_cpa = base_allocation / expected_leads if expected_leads > 0 else typical_cpa
                
                # Determine risk level based on funnel stage
                risk_level = self.FUNNEL_STAGE_PROFILES[stage]["risk_level"]
                
                allocations.append(BudgetAllocation(
                    channel=channel,
                    budget=base_allocation,
                    funnel_stage=stage,
                    expected_leads=expected_leads,
                    expected_cpa=expected_cpa,
                    risk_level=risk_level
                ))
        
        return allocations
    
    def calculate_scenario_metrics(
        self,
        channel_allocations: List[BudgetAllocation],
        average_order_value: Decimal = Decimal("90.00")
    ) -> ScenarioResult:
        """
        Calculate overall scenario metrics.
        
        Args:
            channel_allocations: Channel budget allocations
            average_order_value: Average revenue per conversion
        
        Returns:
            Complete scenario result with metrics
        """
        total_budget = sum(alloc.budget for alloc in channel_allocations)
        total_expected_leads = sum(alloc.expected_leads for alloc in channel_allocations)
        expected_revenue = Decimal(str(total_expected_leads)) * average_order_value
        
        if total_budget > 0:
            expected_roas = float(expected_revenue / total_budget)
        else:
            expected_roas = 0.0
        
        # Calculate risk score based on funnel allocation
        funnel_allocation = self._extract_funnel_allocation(channel_allocations)
        risk_score = self._calculate_risk_score(funnel_allocation)
        
        # Calculate confidence based on diversification
        confidence = self._calculate_confidence(channel_allocations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(funnel_allocation, channel_allocations)
        
        return ScenarioResult(
            funnel_allocation=funnel_allocation,
            channel_allocations=channel_allocations,
            total_budget=total_budget,
            expected_leads=total_expected_leads,
            expected_revenue=expected_revenue,
            expected_roas=expected_roas,
            risk_score=risk_score,
            confidence=confidence,
            recommendations=recommendations
        )
    
    def _extract_funnel_allocation(self, allocations: List[BudgetAllocation]) -> FunnelAllocation:
        """Extract funnel allocation from channel allocations."""
        total_budget = sum(alloc.budget for alloc in allocations)
        
        if total_budget == 0:
            return FunnelAllocation(awareness=0, consideration=0, performance=0)
        
        awareness = float(
            sum(alloc.budget for alloc in allocations if alloc.funnel_stage == FunnelStageEnum.AWARENESS) / total_budget * 100
        )
        consideration = float(
            sum(alloc.budget for alloc in allocations if alloc.funnel_stage == FunnelStageEnum.CONSIDERATION) / total_budget * 100
        )
        performance = float(
            sum(alloc.budget for alloc in allocations if alloc.funnel_stage == FunnelStageEnum.PERFORMANCE) / total_budget * 100
        )
        
        return FunnelAllocation(awareness=awareness, consideration=consideration, performance=performance)
    
    def _calculate_risk_score(self, allocation: FunnelAllocation) -> float:
        """
        Calculate risk score (0-10, where 10 is highest risk).
        
        Higher performance allocation = higher risk (but higher potential return)
        Higher awareness allocation = lower risk (but slower return)
        """
        # Risk weights: awareness=0.2, consideration=0.5, performance=0.9
        risk_score = (
            (allocation.awareness / 100) * 0.2 +
            (allocation.consideration / 100) * 0.5 +
            (allocation.performance / 100) * 0.9
        ) * 10
        
        return round(risk_score, 2)
    
    def _calculate_confidence(self, allocations: List[BudgetAllocation]) -> float:
        """
        Calculate confidence score (0-1) based on diversification.
        
        More diversified channels = higher confidence
        """
        if not allocations:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI) for diversification
        total_budget = sum(alloc.budget for alloc in allocations)
        if total_budget == 0:
            return 0.0
        
        shares = [float(alloc.budget / total_budget) for alloc in allocations]
        hhi = sum(share ** 2 for share in shares)
        
        # Convert HHI to confidence (lower HHI = higher confidence)
        confidence = 1.0 - (hhi - 1.0 / len(allocations)) / (1.0 - 1.0 / len(allocations))
        
        return round(confidence, 2)
    
    def _generate_recommendations(
        self,
        allocation: FunnelAllocation,
        channel_allocations: List[BudgetAllocation]
    ) -> List[str]:
        """Generate recommendations based on allocation."""
        recommendations = []
        
        # Funnel allocation recommendations
        if allocation.performance > 70:
            recommendations.append(
                "High performance allocation focuses on immediate conversions. "
                "Consider increasing awareness for long-term brand building."
            )
        elif allocation.awareness > 60:
            recommendations.append(
                "High awareness allocation builds brand but may delay conversions. "
                "Consider increasing performance spend for short-term results."
            )
        
        if allocation.consideration < 20:
            recommendations.append(
                "Low consideration allocation may miss nurturing opportunities. "
                "Consider increasing mid-funnel content and education efforts."
            )
        
        # Channel-specific recommendations
        high_risk_channels = [alloc for alloc in channel_allocations if alloc.risk_level == "high"]
        if len(high_risk_channels) > len(channel_allocations) * 0.6:
            recommendations.append(
                "Portfolio is heavily weighted toward high-risk channels. "
                "Consider adding stable awareness channels for balance."
            )
        
        # Budget optimization recommendations
        total_budget = sum(alloc.budget for alloc in channel_allocations)
        if total_budget > 0:
            best_performer = max(channel_allocations, key=lambda x: float(x.budget) / x.expected_leads if x.expected_leads > 0 else float('inf'))
            recommendations.append(
                f"Consider scaling {best_performer.channel.value} which shows efficient cost per lead."
            )
        
        return recommendations
    
    def model_scenario(
        self,
        total_budget: Decimal,
        funnel_allocation: FunnelAllocation,
        selected_channels: Optional[List[ChannelType]] = None,
        historical_performance: Optional[Dict[ChannelType, Dict]] = None,
        average_order_value: Decimal = Decimal("90.00")
    ) -> ScenarioResult:
        """
        Model a complete scenario with given parameters.
        
        Args:
            total_budget: Total budget to allocate
            funnel_allocation: Funnel stage allocation percentages
            selected_channels: Channels to include
            historical_performance: Historical performance data
            average_order_value: Average revenue per conversion
        
        Returns:
            Complete scenario result
        """
        channel_allocations = self.calculate_channel_allocation(
            total_budget=total_budget,
            funnel_allocation=funnel_allocation,
            selected_channels=selected_channels,
            historical_performance=historical_performance
        )
        
        return self.calculate_scenario_metrics(
            channel_allocations=channel_allocations,
            average_order_value=average_order_value
        )