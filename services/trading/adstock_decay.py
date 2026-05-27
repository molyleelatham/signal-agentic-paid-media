"""
Adstock Theta Decay Monitor.

This implements Module 7 from the technical spec:
- Adstock model fitting
- Lambda decay parameter estimation
- Creative effectiveness tracking
- Rotation recommendations
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
from scipy.optimize import curve_fit


@dataclass
class AdstockDecayResult:
    """Result of adstock decay fitting."""
    
    lambda_decay: float
    std_error: float
    initial_effect: float
    confidence: str
    signal: str  # "hold", "reduce", "exit"


class AdstockDecayMonitor:
    """
    Adstock Theta Decay Monitor implementation.
    
    This implements Module 7 from the technical spec:
    - Classical adstock model: A_t = x_t + λ · A_{t-1}
    - Lambda (λ) is the retention rate (0–1)
    - λ close to 1 → slow decay, creative still working
    - λ close to 0 → fast decay, creative exhausted
    """
    
    def __init__(
        self,
        hold_threshold: float = 0.7,
        reduce_threshold: float = 0.4
    ):
        """
        Initialize adstock decay monitor.
        
        Args:
            hold_threshold: Lambda above this = hold signal
            reduce_threshold: Lambda below this but above exit = reduce signal
        """
        self.hold_threshold = hold_threshold
        self.reduce_threshold = reduce_threshold
    
    def fit_adstock_lambda(
        self,
        daily_conversions: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> AdstockDecayResult:
        """
        Fit adstock decay model to observed daily conversion time series.
        
        Recovers λ (retention rate) and initial_effect.
        
        Args:
            daily_conversions: Array of daily conversions
            timestamps: Optional array of timestamps (for validation)
        
        Returns:
            AdstockDecayResult with fitted parameters
        """
        if len(daily_conversions) < 3:
            # Not enough data for fitting
            return AdstockDecayResult(
                lambda_decay=0.5,
                std_error=0.5,
                initial_effect=float(daily_conversions[0]) if len(daily_conversions) > 0 else 0.0,
                confidence="low",
                signal="monitor"
            )
        
        t = np.arange(len(daily_conversions))
        
        def adstock_curve(t, lambda_decay, initial_effect):
            """Adstock decay function."""
            return initial_effect * (lambda_decay ** t)
        
        try:
            # Fit the curve
            params, covariance = curve_fit(
                adstock_curve,
                xdata=t,
                ydata=daily_conversions,
                p0=[0.5, daily_conversions[0]],
                bounds=([0, 0], [1, np.inf]),
                maxfev=5000
            )
            
            lambda_decay, initial_effect = params
            std_error = np.sqrt(np.diag(covariance))[0] if covariance.size > 0 else 0.5
            
            # Classify signal
            signal = self.classify_decay_signal(lambda_decay)
            confidence = "high" if std_error < 0.1 else "low"
            
            return AdstockDecayResult(
                lambda_decay=float(lambda_decay),
                std_error=float(std_error),
                initial_effect=float(initial_effect),
                confidence=confidence,
                signal=signal
            )
        
        except RuntimeError:
            # Fit failed — insufficient data or flat signal
            return AdstockDecayResult(
                lambda_decay=0.5,
                std_error=0.5,
                initial_effect=float(daily_conversions[0]) if len(daily_conversions) > 0 else 0.0,
                confidence="low",
                signal="monitor"
            )
    
    def classify_decay_signal(self, lambda_val: float) -> str:
        """
        Classify decay signal based on lambda value.
        
        Args:
            lambda_val: Lambda decay parameter
        
        Returns:
            Signal: "hold", "reduce", or "exit"
        """
        if lambda_val > self.hold_threshold:
            return "hold"  # strong residual, keep running
        elif lambda_val > self.reduce_threshold:
            return "reduce"  # fading, reduce budget on this position
        else:
            return "exit"  # alpha exhausted, rotate creative
    
    def predict_future_performance(
        self,
        current_conversions: np.ndarray,
        days_ahead: int = 7
    ) -> np.ndarray:
        """
        Predict future performance based on adstock model.
        
        Args:
            current_conversions: Historical daily conversions
            days_ahead: Number of days to predict ahead
        
        Returns:
            Array of predicted conversions for future days
        """
        if len(current_conversions) < 3:
            # Not enough data, return flat prediction
            return np.full(days_ahead, current_conversions[-1] if len(current_conversions) > 0 else 0)
        
        # Fit model
        result = self.fit_adstock_lambda(current_conversions)
        lambda_decay = result.lambda_decay
        initial_effect = result.initial_effect
        
        # Predict future
        t_current = len(current_conversions)
        t_future = np.arange(t_current, t_current + days_ahead)
        
        predictions = initial_effect * (lambda_decay ** t_future)
        
        return predictions
    
    def calculate_decay_rate(self, lambda_val: float) -> float:
        """
        Calculate daily decay rate from lambda.
        
        Args:
            lambda_val: Lambda decay parameter
        
        Returns:
            Daily decay rate (0-1)
        """
        return 1.0 - lambda_val
    
    def estimate_half_life(self, lambda_val: float) -> float:
        """
        Estimate half-life of creative effectiveness.
        
        Args:
            lambda_val: Lambda decay parameter
        
        Returns:
            Half-life in days
        """
        if lambda_val <= 0:
            return float('inf')
        
        half_life = np.log(0.5) / np.log(lambda_val)
        return abs(half_life)


class CreativeRotationManager:
    """
    High-level creative rotation management based on adstock decay.
    
    Monitors multiple creatives and provides rotation recommendations.
    """
    
    def __init__(self, adstock_monitor: AdstockDecayMonitor = None):
        """
        Initialize creative rotation manager.
        
        Args:
            adstock_monitor: Adstock decay monitor instance
        """
        self.adstock_monitor = adstock_monitor or AdstockDecayMonitor()
        
        # Track creative performance
        self.creative_performance: Dict[str, List[float]] = {}
        self.creative_timestamps: Dict[str, List[datetime]] = {}
    
    def add_creative_data(
        self,
        creative_id: str,
        conversions: float,
        timestamp: datetime = None
    ) -> None:
        """
        Add performance data for a creative.
        
        Args:
            creative_id: Creative identifier
            conversions: Number of conversions
            timestamp: Timestamp of data point
        """
        if creative_id not in self.creative_performance:
            self.creative_performance[creative_id] = []
            self.creative_timestamps[creative_id] = []
        
        self.creative_performance[creative_id].append(conversions)
        
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.creative_timestamps[creative_id].append(timestamp)
    
    def get_creative_decay_status(
        self,
        creative_id: str
    ) -> Optional[AdstockDecayResult]:
        """
        Get decay status for a creative.
        
        Args:
            creative_id: Creative identifier
        
        Returns:
            AdstockDecayResult or None if not enough data
        """
        if creative_id not in self.creative_performance:
            return None
        
        conversions = np.array(self.creative_performance[creative_id])
        
        if len(conversions) < 3:
            return None
        
        return self.adstock_monitor.fit_adstock_lambda(conversions)
    
    def get_rotation_recommendations(
        self,
        campaign_id: str = None
    ) -> List[Dict]:
        """
        Get rotation recommendations for all creatives.
        
        Args:
            campaign_id: Optional campaign ID for filtering
        
        Returns:
            List of rotation recommendations
        """
        recommendations = []
        
        for creative_id in self.creative_performance.keys():
            status = self.get_creative_decay_status(creative_id)
            
            if status is None:
                continue
            
            recommendation = {
                "creative_id": creative_id,
                "lambda_decay": status.lambda_decay,
                "signal": status.signal,
                "confidence": status.confidence,
                "recommendation": self._get_recommendation_text(status.signal),
                "half_life_days": self.adstock_monitor.estimate_half_life(status.lambda_decay),
                "data_points": len(self.creative_performance[creative_id])
            }
            
            recommendations.append(recommendation)
        
        # Sort by urgency (exit signals first)
        urgency_order = {"exit": 0, "reduce": 1, "hold": 2, "monitor": 3}
        recommendations.sort(key=lambda x: urgency_order.get(x["signal"], 4))
        
        return recommendations
    
    def _get_recommendation_text(self, signal: str) -> str:
        """Get human-readable recommendation text."""
        recommendations = {
            "hold": "Creative is performing well. Continue running.",
            "reduce": "Creative effectiveness is fading. Consider reducing budget.",
            "exit": "Creative effectiveness is exhausted. Rotate immediately.",
            "monitor": "Insufficient data for recommendation. Monitor performance."
        }
        return recommendations.get(signal, "Unknown signal")
    
    def get_top_performing_creatives(
        self,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Get top performing creatives based on decay parameters.
        
        Args:
            top_n: Number of top creatives to return
        
        Returns:
            List of top performing creatives
        """
        creative_scores = []
        
        for creative_id in self.creative_performance.keys():
            status = self.get_creative_decay_status(creative_id)
            
            if status is None:
                continue
            
            # Score based on lambda (higher is better) and initial effect
            score = status.lambda_decay * status.initial_effect
            
            creative_scores.append({
                "creative_id": creative_id,
                "score": score,
                "lambda_decay": status.lambda_decay,
                "initial_effect": status.initial_effect,
                "signal": status.signal
            })
        
        # Sort by score (descending)
        creative_scores.sort(key=lambda x: x["score"], reverse=True)
        
        return creative_scores[:top_n]