"""
Thompson Sampling Budget Allocator.

This implements Module 5 from the technical spec:
- Beta-Bernoulli bandit for platform budget allocation
- Dynamic allocation based on conversion performance
- Floor and cap constraints
"""
from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass
class PlatformPosterior:
    """Beta distribution posterior for a platform."""
    
    platform: str
    alpha: float = 2.0  # successes + prior
    beta: float = 2.0   # failures + prior
    # Beta(2,2) prior: weakly informative, symmetric, neither arm starts dominant
    
    def sample(self) -> float:
        """Sample from this posterior."""
        return np.random.beta(self.alpha, self.beta)
    
    def update(self, conversions: int, non_converting_spend: int):
        """Update posterior with new data."""
        self.alpha += conversions
        self.beta += non_converting_spend


@dataclass
class BudgetAllocation:
    """Budget allocation result."""
    
    platform: str
    allocated_budget: float
    raw_allocation: float
    floor: float
    cap: float
    sample_value: float


class ThompsonSamplingAllocator:
    """
    Thompson Sampling Budget Allocator.
    
    This implements Module 5 from the technical spec:
    - Models each platform as a Beta-Bernoulli bandit arm
    - Samples from posteriors to allocate budget
    - Enforces floor and cap constraints
    """
    
    def __init__(
        self,
        prior_alpha: float = 2.0,
        prior_beta: float = 2.0
    ):
        """
        Initialize Thompson sampling allocator.
        
        Args:
            prior_alpha: Prior alpha parameter (successes)
            prior_beta: Prior beta parameter (failures)
        """
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.posteriors: Dict[str, PlatformPosterior] = {}
    
    def initialize_platforms(
        self,
        platforms: List[str]
    ) -> None:
        """
        Initialize posteriors for all platforms.
        
        Args:
            platforms: List of platform names
        """
        self.posteriors = {}
        for platform in platforms:
            self.posteriors[platform] = PlatformPosterior(
                platform=platform,
                alpha=self.prior_alpha,
                beta=self.prior_beta
            )
    
    def update_posterior(
        self,
        platform: str,
        conversions: int,
        non_converting_spend: int
    ) -> None:
        """
        Update posterior for a platform with new performance data.
        
        Args:
            platform: Platform name
            conversions: Number of conversions (successes)
            non_converting_spend: Spend that didn't convert (failures)
        """
        if platform not in self.posteriors:
            self.posteriors[platform] = PlatformPosterior(
                platform=platform,
                alpha=self.prior_alpha,
                beta=self.prior_beta
            )
        
        self.posteriors[platform].update(conversions, non_converting_spend)
    
    def thompson_allocate(
        self,
        total_budget: float,
        floors: Dict[str, float] = None,
        caps: Dict[str, float] = None
    ) -> Dict[str, BudgetAllocation]:
        """
        Allocate budget using Thompson sampling.
        
        Args:
            total_budget: Total budget to allocate
            floors: Minimum budget per platform
            caps: Maximum budget per platform
        
        Returns:
            Dict mapping platform names to BudgetAllocation objects
        """
        if floors is None:
            floors = {}
        if caps is None:
            caps = {}
        
        if not self.posteriors:
            raise ValueError("No platforms initialized. Call initialize_platforms first.")
        
        # Sample from each platform's posterior
        samples = {
            platform: posterior.sample()
            for platform, posterior in self.posteriors.items()
        }
        
        # Calculate raw allocation proportional to samples
        total_sample = sum(samples.values())
        raw_allocation = {
            platform: (sample / total_sample) * total_budget
            for platform, sample in samples.items()
        }
        
        # Enforce floors and caps
        allocations = {}
        remaining = total_budget
        
        # First pass: apply floors
        for platform in self.posteriors.keys():
            raw_amount = raw_allocation[platform]
            floor = floors.get(platform, 0)
            cap = caps.get(platform, float("inf"))
            
            floored = max(raw_amount, floor)
            capped = min(floored, cap)
            
            allocations[platform] = BudgetAllocation(
                platform=platform,
                allocated_budget=capped,
                raw_allocation=raw_amount,
                floor=floor,
                cap=cap,
                sample_value=samples[platform]
            )
            
            remaining -= capped
        
        # Redistribute remaining budget proportionally to uncapped platforms
        if remaining > 0:
            uncapped_platforms = [
                p for p, alloc in allocations.items()
                if alloc.allocated_budget < alloc.cap
            ]
            
            if uncapped_platforms:
                redistribution = remaining / len(uncapped_platforms)
                for platform in uncapped_platforms:
                    allocations[platform].allocated_budget += redistribution
        
        return allocations
    
    def get_platform_statistics(self) -> Dict[str, Dict]:
        """
        Get statistics for all platforms.
        
        Returns:
            Dict with platform statistics including:
            - alpha, beta (posterior parameters)
            - mean (expected conversion rate)
            - sample_value (latest sample)
            - total_conversions, total_failures
        """
        stats = {}
        for platform, posterior in self.posteriors.items():
            stats[platform] = {
                "alpha": posterior.alpha,
                "beta": posterior.beta,
                "mean": posterior.alpha / (posterior.alpha + posterior.beta),
                "total_conversions": posterior.alpha - self.prior_alpha,
                "total_failures": posterior.beta - self.prior_beta
            }
        
        return stats
    
    def reset_platform(self, platform: str) -> None:
        """
        Reset a platform's posterior to prior.
        
        Args:
            platform: Platform name to reset
        """
        if platform in self.posteriors:
            self.posteriors[platform] = PlatformPosterior(
                platform=platform,
                alpha=self.prior_alpha,
                beta=self.prior_beta
            )
    
    def set_custom_posterior(
        self,
        platform: str,
        alpha: float,
        beta: float
    ) -> None:
        """
        Set custom posterior parameters for a platform.
        
        Args:
            platform: Platform name
            alpha: Alpha parameter
            beta: Beta parameter
        """
        self.posteriors[platform] = PlatformPosterior(
            platform=platform,
            alpha=alpha,
            beta=beta
        )


class BudgetManager:
    """
    High-level budget management with Thompson sampling.
    
    Manages budget allocation across platforms with periodic re-allocation
    based on performance data.
    """
    
    def __init__(
        self,
        platforms: List[str],
        total_budget: float,
        floors: Dict[str, float] = None,
        caps: Dict[str, float] = None
    ):
        """
        Initialize budget manager.
        
        Args:
            platforms: List of platform names
            total_budget: Total budget to manage
            floors: Minimum budget per platform
            caps: Maximum budget per platform
        """
        self.platforms = platforms
        self.total_budget = total_budget
        self.floors = floors or {}
        self.caps = caps or {}
        
        self.allocator = ThompsonSamplingAllocator()
        self.allocator.initialize_platforms(platforms)
        
        # Track actual spend vs allocated
        self.actual_spend = {platform: 0.0 for platform in platforms}
    
    def allocate_budget(self) -> Dict[str, BudgetAllocation]:
        """
        Allocate budget using Thompson sampling.
        
        Returns:
            Current budget allocation
        """
        return self.allocator.thompson_allocate(
            self.total_budget,
            self.floors,
            self.caps
        )
    
    def record_performance(
        self,
        platform: str,
        conversions: int,
        spend: float
    ) -> None:
        """
        Record performance data for a platform.
        
        Args:
            platform: Platform name
            conversions: Number of conversions
            spend: Total spend
        """
        # Update posterior
        non_converting_spend = max(0, spend - conversions)  # Simplified
        self.allocator.update_posterior(platform, conversions, non_converting_spend)
        
        # Track actual spend
        self.actual_spend[platform] += spend
    
    def get_allocation_summary(self) -> Dict:
        """
        Get summary of current allocation and performance.
        
        Returns:
            Dict with allocation summary and platform statistics
        """
        allocation = self.allocate_budget()
        stats = self.allocator.get_platform_statistics()
        
        summary = {
            "total_budget": self.total_budget,
            "allocations": {
                platform: {
                    "allocated": alloc.allocated_budget,
                    "raw": alloc.raw_allocation,
                    "floor": alloc.floor,
                    "cap": alloc.cap,
                    "sample_value": alloc.sample_value,
                    "actual_spend": self.actual_spend[platform],
                    "statistics": stats[platform]
                }
                for platform, alloc in allocation.items()
            }
        }
        
        return summary
    
    def reallocate_budget(
        self,
        new_total_budget: float = None
    ) -> Dict[str, BudgetAllocation]:
        """
        Reallocate budget (e.g., for new week/campaign).
        
        Args:
            new_total_budget: New total budget (uses current if not provided)
        
        Returns:
            New budget allocation
        """
        if new_total_budget is not None:
            self.total_budget = new_total_budget
        
        # Reset actual spend tracking
        self.actual_spend = {platform: 0.0 for platform in self.platforms}
        
        return self.allocate_budget()