"""
Bid Discovery Engine - LOESS/DMR + Bayesian Cold Start.

This implements Module 3 (LOESS/DMR Bid Discovery) and Module 4 (Bayesian Cold Start)
from the technical spec.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import brentq
from statsmodels.nonparametric.smoothers_lowess import lowess


@dataclass
class BidCurveResult:
    """Result of LOESS curve fitting."""
    
    bid_grid: np.ndarray
    smoothed_conv_rate: np.ndarray
    confidence: str


@dataclass
class DMROptimalResult:
    """Result of DMR optimal bid calculation."""
    
    optimal_bid: float
    inflection_point: float
    expected_conv_rate: float
    marginal_return: float
    curve_confidence: str


@dataclass
class BayesianBidResult:
    """Result of Bayesian bid calculation."""
    
    bid: float
    confidence: float
    n_observations: int
    mode: str  # "cold_start" or "fitted"


@dataclass
class ColdStartResult:
    """Result of cold start exploration/exploitation."""
    
    bid: float
    mode: str  # "exploring" or "exploiting"
    epsilon: float


class LOESSBidDiscovery:
    """
    LOESS/DMR Bid Discovery implementation.
    
    This implements Module 3 from the technical spec:
    - LOESS fitting for non-parametric regression
    - DMR inflection point detection
    - Temporal surface for non-stationarity handling
    """
    
    def __init__(self, frac: float = 0.3, it: int = 3, buffer: float = 0.92):
        """
        Initialize LOESS bid discovery.
        
        Args:
            frac: Bandwidth - fraction of data used in each local regression
            it: Robustness iterations - downweights outliers
            buffer: Bid at buffer% of inflection point (stay on efficient part)
        """
        self.frac = frac
        self.it = it
        self.buffer = buffer
    
    def fit_loess_curve(
        self,
        bid_prices: np.ndarray,
        conversion_rates: np.ndarray
    ) -> BidCurveResult:
        """
        Fit LOESS curve to bid vs conversion rate data.
        
        Args:
            bid_prices: Array of bid prices
            conversion_rates: Array of conversion rates
        
        Returns:
            BidCurveResult with fitted curve
        """
        if len(bid_prices) < 10:
            # Not enough data for stable fit
            return BidCurveResult(
                bid_grid=bid_prices,
                smoothed_conv_rate=conversion_rates,
                confidence="low"
            )
        
        # Fit LOESS
        smoothed = lowess(
            endog=conversion_rates,
            exog=bid_prices,
            frac=self.frac,
            it=self.it,
            return_sorted=True
        )
        
        bid_grid = smoothed[:, 0]
        smoothed_conv_rate = smoothed[:, 1]
        
        confidence = "high" if len(bid_prices) >= 50 else "low"
        
        return BidCurveResult(
            bid_grid=bid_grid,
            smoothed_conv_rate=smoothed_conv_rate,
            confidence=confidence
        )
    
    def find_dmr_optimal(
        self,
        bid_grid: np.ndarray,
        conv_grid: np.ndarray
    ) -> DMROptimalResult:
        """
        Find DMR (Diminishing Marginal Returns) optimal bid.
        
        Fits a spline to LOESS output, takes derivatives, and finds
        the inflection point where second derivative crosses zero.
        
        Args:
            bid_grid: Bid prices from LOESS
            conv_grid: Smoothed conversion rates from LOESS
        
        Returns:
            DMROptimalResult with optimal bid and metadata
        """
        if len(bid_grid) < 5:
            # Not enough points for spline fitting
            return DMROptimalResult(
                optimal_bid=float(bid_grid.mean()),
                inflection_point=float(bid_grid.mean()),
                expected_conv_rate=float(conv_grid.mean()),
                marginal_return=0.0,
                curve_confidence="low"
            )
        
        try:
            # Fit spline
            spline = UnivariateSpline(bid_grid, conv_grid, s=0.01, k=4)
            d1 = spline.derivative(n=1)  # First derivative
            d2 = spline.derivative(n=2)  # Second derivative
            
            # Find inflection point (where second derivative crosses zero)
            try:
                inflection = brentq(d2, bid_grid.min(), bid_grid.max())
            except ValueError:
                # No sign change - curve is monotonic
                # Fall back to point of maximum first derivative
                inflection = bid_grid[np.argmax(d1(bid_grid))]
            
            optimal_bid = inflection * self.buffer
            expected_conv_rate = float(spline(optimal_bid))
            marginal_return = float(d1(optimal_bid))
            
            confidence = "high" if len(bid_grid) >= 50 else "low"
            
            return DMROptimalResult(
                optimal_bid=float(optimal_bid),
                inflection_point=float(inflection),
                expected_conv_rate=expected_conv_rate,
                marginal_return=marginal_return,
                curve_confidence=confidence
            )
        
        except Exception as e:
            print(f"Error finding DMR optimal: {e}")
            # Fallback to mean bid
            return DMROptimalResult(
                optimal_bid=float(bid_grid.mean()),
                inflection_point=float(bid_grid.mean()),
                expected_conv_rate=float(conv_grid.mean()),
                marginal_return=0.0,
                curve_confidence="low"
            )
    
    def build_temporal_surface(
        self,
        historical_data: List[Dict]
    ) -> np.ndarray:
        """
        Build temporal surface for non-stationarity handling.
        
        Fits LOESS per weekly cohort, then LOESS across time series
        of optimal bids to produce smoothed forward signal.
        
        Args:
            historical_data: List of dicts with 'week_cohort', 'bid_price', 'conversion_rate'
        
        Returns:
            Smoothed trajectory of optimal bids over time
        """
        import pandas as pd
        
        df = pd.DataFrame(historical_data)
        
        if df.empty:
            return np.array([])
        
        weekly_optima = []
        
        # Fit LOESS per week cohort
        for week, cohort in df.groupby("week_cohort"):
            if len(cohort) < 20:
                continue  # Too sparse for stable fit
            
            bid_prices = cohort["bid_price"].values
            conversion_rates = cohort["conversion_rate"].values
            
            curve_result = self.fit_loess_curve(bid_prices, conversion_rates)
            dmr_result = self.find_dmr_optimal(
                curve_result.bid_grid,
                curve_result.smoothed_conv_rate
            )
            
            weekly_optima.append({
                "week": week,
                "optimal_bid": dmr_result.optimal_bid
            })
        
        if not weekly_optima:
            return np.array([])
        
        # Sort by week
        weekly_df = pd.DataFrame(weekly_optima).sort_values("week")
        
        # LOESS on time series of optimal bids
        if len(weekly_df) < 3:
            return weekly_df["optimal_bid"].values
        
        smoothed_trajectory = lowess(
            endog=weekly_df["optimal_bid"].values,
            exog=np.arange(len(weekly_df)),
            frac=0.4,
            it=2
        )
        
        return smoothed_trajectory[:, 1]  # Return smoothed bids


class BayesianColdStart:
    """
    Bayesian Cold Start using James-Stein shrinkage.
    
    This implements Module 4 from the technical spec:
    - James-Stein shrinkage toward global prior
    - Epsilon-greedy exploration during cold start
    """
    
    def __init__(
        self,
        min_observations: int = 50,
        pseudo_count: int = 30,
        explore_range: float = 0.25
    ):
        """
        Initialize Bayesian cold start.
        
        Args:
            min_observations: Minimum observations for stable LOESS fit
            pseudo_count: Effective prior sample size for shrinkage
            explore_range: Range for exploration (±explore_range around posterior)
        """
        self.min_observations = min_observations
        self.pseudo_count = pseudo_count
        self.explore_range = explore_range
    
    def calculate_global_prior(self, historical_data: List[Dict]) -> Dict:
        """
        Calculate global prior from historical data across all clusters.
        
        Args:
            historical_data: List of historical bid/performance data
        
        Returns:
            Dict with mean_optimal_bid, pseudo_count, std
        """
        if not historical_data:
            return {
                "mean_optimal_bid": 1.0,
                "pseudo_count": self.pseudo_count,
                "std": 0.5
            }
        
        # Extract all optimal bids (would come from historical LOESS fits)
        optimal_bids = [d.get("optimal_bid", 1.0) for d in historical_data]
        
        return {
            "mean_optimal_bid": float(np.mean(optimal_bids)),
            "pseudo_count": self.pseudo_count,
            "std": float(np.std(optimal_bids))
        }
    
    def bayesian_bid(
        self,
        cluster_data: List[Dict],
        global_prior: Dict,
        loess_discovery: LOESSBidDiscovery
    ) -> BayesianBidResult:
        """
        Calculate Bayesian bid with James-Stein shrinkage.
        
        Args:
            cluster_data: Data for specific cluster/topic
            global_prior: Global prior parameters
            loess_discovery: LOESS discovery instance for fitting
        
        Returns:
            BayesianBidResult with shrunk bid estimate
        """
        n = len(cluster_data)
        
        # Calculate shrinkage weight
        shrinkage_weight = n / (n + global_prior["pseudo_count"])
        
        if n >= self.min_observations:
            # Enough data for cluster-specific LOESS fit
            bid_prices = np.array([d["bid_price"] for d in cluster_data])
            conversion_rates = np.array([d["conversion_rate"] for d in cluster_data])
            
            curve_result = loess_discovery.fit_loess_curve(bid_prices, conversion_rates)
            dmr_result = loess_discovery.find_dmr_optimal(
                curve_result.bid_grid,
                curve_result.smoothed_conv_rate
            )
            
            cluster_optimal = dmr_result.optimal_bid
            mode = "fitted"
        else:
            # Not enough data - use global prior
            cluster_optimal = global_prior["mean_optimal_bid"]
            mode = "cold_start"
        
        # Posterior estimate: weighted combination
        posterior_bid = (
            shrinkage_weight * cluster_optimal +
            (1 - shrinkage_weight) * global_prior["mean_optimal_bid"]
        )
        
        return BayesianBidResult(
            bid=float(posterior_bid),
            confidence=float(shrinkage_weight),
            n_observations=n,
            mode=mode
        )
    
    def cold_start_bid(
        self,
        n_obs: int,
        posterior_bid: float
    ) -> ColdStartResult:
        """
        Apply epsilon-greedy exploration during cold start.
        
        Args:
            n_obs: Number of observations so far
            posterior_bid: Posterior bid from Bayesian shrinkage
        
        Returns:
            ColdStartResult with exploration/exploitation decision
        """
        # Epsilon decreases linearly as observations accumulate
        epsilon = max(0.0, 1.0 - (n_obs / self.min_observations))
        
        if np.random.random() < epsilon:
            # Explore: sample uniformly around posterior bid
            bid = posterior_bid * np.random.uniform(
                1 - self.explore_range,
                1 + self.explore_range
            )
            mode = "exploring"
        else:
            # Exploit: use posterior bid
            bid = posterior_bid
            mode = "exploiting"
        
        return ColdStartResult(
            bid=float(bid),
            mode=mode,
            epsilon=float(epsilon)
        )


class BidDiscoveryEngine:
    """
    Complete bid discovery engine combining LOESS/DMR and Bayesian cold start.
    
    This integrates Module 3 and Module 4 into a unified service.
    """
    
    def __init__(self):
        """Initialize bid discovery engine."""
        self.loess_discovery = LOESSBidDiscovery()
        self.bayesian_cold_start = BayesianColdStart()
    
    def compute_optimal_bid(
        self,
        cluster_data: List[Dict],
        global_prior: Optional[Dict] = None
    ) -> Dict:
        """
        Compute optimal bid for a cluster.
        
        Args:
            cluster_data: Historical bid/performance data for cluster
            global_prior: Global prior parameters (computed if not provided)
        
        Returns:
            Dict with optimal bid and metadata
        """
        if global_prior is None:
            global_prior = self.bayesian_cold_start.calculate_global_prior(cluster_data)
        
        # Step 1: Bayesian bid with shrinkage
        bayesian_result = self.bayesian_cold_start.bayesian_bid(
            cluster_data,
            global_prior,
            self.loess_discovery
        )
        
        # Step 2: Cold start exploration if needed
        cold_start_result = self.bayesian_cold_start.cold_start_bid(
            bayesian_result.n_observations,
            bayesian_result.bid
        )
        
        return {
            "optimal_bid": cold_start_result.bid,
            "mode": cold_start_result.mode,
            "epsilon": cold_start_result.epsilon,
            "confidence": bayesian_result.confidence,
            "n_observations": bayesian_result.n_observations,
            "bayesian_mode": bayesian_result.mode,
            "global_prior": global_prior
        }
    
    def update_global_prior(
        self,
        all_cluster_data: Dict[str, List[Dict]]
    ) -> Dict:
        """
        Update global prior from all cluster data.
        
        Args:
            all_cluster_data: Dict mapping cluster IDs to their data
        
        Returns:
            Updated global prior
        """
        # Flatten all cluster data
        all_data = []
        for cluster_id, data in all_cluster_data.items():
            all_data.extend(data)
        
        return self.bayesian_cold_start.calculate_global_prior(all_data)