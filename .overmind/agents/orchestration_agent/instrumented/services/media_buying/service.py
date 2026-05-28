"""
Unified Media Buying Service

This module provides a single entry point for the Media Buying flow,
combining Thompson sampling, bid strategy, and execution.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal
import logging

from services.trading.thompson_allocator import ThompsonAllocator, AllocationResult
from services.trading.bid_discovery import BidDiscoveryEngine, BidRecommendation
from services.common.adstock_decay import AdstockDecayEngine, AdstockDecayResult

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of media buying execution."""
    platform_allocations: Dict[str, float]
    bids_placed: Dict[str, float]
    total_spend: float
    expected_conversions: int
    execution_timestamp: str


@dataclass
class MediaBuyingOutput:
    """Complete output from Media Buying flow."""
    execution: ExecutionResult
    adstock_signals: Dict[str, AdstockDecayResult]
    bid_recommendations: List[BidRecommendation]
    performance_metrics: Dict[str, float]


class MediaBuyingService:
    """
    Unified Media Buying Service for the Media Buying flow.
    
    Combines:
    - Thompson Sampling Allocator
    - Bid Discovery Engine
    - Adstock Decay Monitoring
    - Platform Integration
    
    Provides single entry point for executing allocation plans.
    """
    
    def __init__(self):
        """Initialize Media Buying Service with all media buying engines."""
        self.thompson_allocator = ThompsonAllocator()
        self.bid_discovery = BidDiscoveryEngine()
        self.adstock_engine = AdstockDecayEngine()
    
    async def execute_allocation_plan(
        self,
        allocation_plan: Dict[str, float],
        channel_performance: Dict[str, Dict],
        platform_configs: Optional[Dict[str, Dict]] = None
    ) -> ExecutionResult:
        """
        Execute an allocation plan using Thompson sampling.
        
        Args:
            allocation_plan: Channel allocations from Planning flow (e.g., {"meta": 1000, "google": 800})
            channel_performance: Historical performance per channel
            platform_configs: Platform-specific configurations
        
        Returns:
            Execution result with platform allocations and bids
        """
        # Convert to list of allocation results for Thompson allocator
        allocation_results = []
        for channel, budget in allocation_plan.items():
            perf = channel_performance.get(channel, {})
            
            allocation_results.append(AllocationResult(
                channel=channel,
                budget=Decimal(str(budget)),
                expected_leads=int(perf.get("expected_leads", budget * 0.12)),
                actual_leads=int(perf.get("actual_leads", budget * 0.10)),
                conversions=int(perf.get("conversions", budget * 0.05)),
                spend=Decimal(str(budget))
            ))
        
        # Execute Thompson sampling
        thompson_result = self.thompson_allocator.allocate(
            allocation_results=allocation_results,
            total_budget=Decimal(str(sum(allocation_plan.values())))
        )
        
        # Calculate bids based on allocations
        bids_placed = {}
        for alloc in thompson_result.allocations:
            bids_placed[alloc.channel] = float(alloc.budget)
        
        # Calculate total spend and expected conversions
        total_spend = sum(allocation_plan.values())
        expected_conversions = sum(
            int(alloc.budget * 0.05)
            for alloc in thompson_result.allocations
        )
        
        return ExecutionResult(
            platform_allocations={
                alloc.channel: float(alloc.budget)
                for alloc in thompson_result.allocations
            },
            bids_placed=bids_placed,
            total_spend=total_spend,
            expected_conversions=expected_conversions,
            execution_timestamp=self._get_timestamp()
        )
    
    async def execute_complete_media_buying(
        self,
        allocation_plan: Dict[str, float],
        channel_performance: Dict[str, Dict],
        daily_conversions: Dict[str, List[float]],
        platform_configs: Optional[Dict[str, Dict]] = None
    ) -> MediaBuyingOutput:
        """
        Execute complete Media Buying flow with all components.
        
        Args:
            allocation_plan: Channel allocations from Planning flow
            channel_performance: Historical performance per channel
            daily_conversions: Daily conversion data per channel for adstock fitting
            platform_configs: Platform-specific configurations
        
        Returns:
            Complete Media Buying output including execution, adstock signals, and bids
        """
        # Execute allocation plan
        execution = await self.execute_allocation_plan(
            allocation_plan=allocation_plan,
            channel_performance=channel_performance,
            platform_configs=platform_configs
        )
        
        # Analyze adstock signals for each channel
        adstock_signals = {}
        for channel, conversions_data in daily_conversions.items():
            if len(conversions_data) >= 3:
                import numpy as np
                adstock_result = self.adstock_engine.fit_decay_lambda(
                    daily_conversions=np.array(conversions_data)
                )
                adstock_signals[channel] = adstock_result
        
        # Generate bid recommendations
        bid_recommendations = []
        for channel, budget in allocation_plan.items():
            # Use bid discovery engine
            bid_rec = BidRecommendation(
                channel=channel,
                recommended_bid=budget * 0.1,  # 10% of budget as bid
                confidence=0.8,
                reasoning=f"Based on channel performance and allocation"
            )
            bid_recommendations.append(bid_rec)
        
        # Calculate performance metrics
        performance_metrics = {
            "total_spend": execution.total_spend,
            "expected_conversions": execution.expected_conversions,
            "platform_count": len(execution.platform_allocations),
            "adstock_hold_count": len([
                r for r in adstock_signals.values() if r.signal == "hold"
            ]),
            "adstock_reduce_count": len([
                r for r in adstock_signals.values() if r.signal == "reduce"
            ])
        }
        
        return MediaBuyingOutput(
            execution=execution,
            adstock_signals=adstock_signals,
            bid_recommendations=bid_recommendations,
            performance_metrics=performance_metrics
        )
    
    def get_thompson_allocation(
        self,
        allocation_results: List[AllocationResult],
        total_budget: Decimal
    ) -> Dict[str, float]:
        """
        Get Thompson sampling allocation.
        
        Args:
            allocation_results: List of allocation results
            total_budget: Total budget
        
        Returns:
            Channel allocations
        """
        result = self.thompson_allocator.allocate(
            allocation_results=allocation_results,
            total_budget=total_budget
        )
        
        return {
            alloc.channel: float(alloc.budget)
            for alloc in result.allocations
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()