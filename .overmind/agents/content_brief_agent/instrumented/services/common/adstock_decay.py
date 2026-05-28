"""
Unified Adstock Decay Module

This module provides a single source of truth for adstock decay modeling,
used by both Planning and Media Buying flows.

Mathematical Model:
- Classical adstock: A_t = x_t + λ · A_{t-1}
- Lambda (λ) is the retention rate (0–1)
- λ close to 1 → slow decay, creative still working
- λ close to 0 → fast decay, creative exhausted
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import curve_fit
import logging

logger = logging.getLogger(__name__)


@dataclass
class AdstockDecayResult:
    """Result of adstock decay fitting."""
    decay_rate: float
    std_error: float
    initial_effect: float
    confidence: str
    signal: str  # "hold", "reduce", "exit"


@dataclass
class AdstockSaturation:
    """Adstock saturation analysis."""
    channel: str
    current_saturation: float  # 0-1, current saturation level
    decay_rate: float  # Lambda decay parameter
    days_until_refresh: int  # Recommended days until creative refresh
    saturation_velocity: str  # "increasing", "stable", "decreasing"
    refresh_urgency: str  # "immediate", "soon", "monitor"


class AdstockDecayEngine:
    """
    Unified adstock decay engine for both Planning and Media Buying flows.
    
    Provides:
    - Lambda parameter estimation from performance data
    - Saturation analysis and refresh timing
    - Signal generation (hold/reduce/exit)
    """
    
    def __init__(
        self,
        hold_threshold: float = 0.7,
        reduce_threshold: float = 0.4,
        saturation_threshold: float = 0.6
    ):
        """
        Initialize adstock decay engine.
        
        Args:
            hold_threshold: Lambda above this = hold signal
            reduce_threshold: Lambda below this but above exit = reduce signal
            saturation_threshold: Saturation level below which to recommend refresh
        """
        self.hold_threshold = hold_threshold
        self.reduce_threshold = reduce_threshold
        self.saturation_threshold = saturation_threshold
    
    def fit_decay_rate(
        self,
        daily_conversions: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> AdstockDecayResult:
        """
        Fit adstock decay model to observed daily conversion time series.
        
        Recovers decay_rate (retention rate) and initial_effect using scipy curve_fit.
        
        Args:
            daily_conversions: Array of daily conversions
            timestamps: Optional array of timestamps (for validation)
        
        Returns:
            AdstockDecayResult with fitted parameters
        """
        if len(daily_conversions) < 3:
            # Not enough data for fitting
            return AdstockDecayResult(
                decay_rate=0.5,
                std_error=0.5,
                initial_effect=float(daily_conversions[0]) if len(daily_conversions) > 0 else 0.0,
                confidence="low",
                signal="monitor"
            )
        
        t = np.arange(len(daily_conversions))
        
        def adstock_curve(t, decay_rate, initial_effect):
            """Adstock decay function: A_t = initial_effect * (decay_rate ** t)"""
            return initial_effect * (decay_rate ** t)
        
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
            
            decay_rate, initial_effect = params
            std_error = np.sqrt(np.diag(covariance))[0] if covariance.size > 0 else 0.5
            
            # Determine signal based on decay_rate
            if decay_rate >= self.hold_threshold:
                signal = "hold"
                confidence = "high" if std_error < 0.1 else "moderate"
            elif decay_rate >= self.reduce_threshold:
                signal = "reduce"
                confidence = "moderate" if std_error < 0.15 else "low"
            else:
                signal = "exit"
                confidence = "low"
            
            return AdstockDecayResult(
                decay_rate=float(decay_rate),
                std_error=float(std_error),
                initial_effect=float(initial_effect),
                confidence=confidence,
                signal=signal
            )
            
        except Exception as e:
            logger.error(f"Adstock curve fitting failed: {e}")
            return AdstockDecayResult(
                decay_rate=0.5,
                std_error=0.5,
                initial_effect=float(daily_conversions[0]) if len(daily_conversions) > 0 else 0.0,
                confidence="low",
                signal="monitor"
            )
    
    def analyze_saturation(
        self,
        channel: str,
        days_since_refresh: int,
        decay_rate: float,
        historical_performance: Optional[Dict] = None
    ) -> AdstockSaturation:
        """
        Analyze adstock saturation and recommend refresh timing.
        
        Args:
            channel: Channel name
            days_since_refresh: Days since creative was last refreshed
            decay_rate: Fitted decay rate parameter (0-1)
            historical_performance: Optional historical performance data
        
        Returns:
            Adstock saturation analysis with refresh recommendations
        """
        # Calculate current saturation using exponential decay
        # Formula: saturation = 1 - (decay_rate ^ days)
        current_saturation = min(1.0, 1 - (decay_rate ** days_since_refresh))
        
        # Calculate days until refresh (when saturation drops below threshold)
        if decay_rate > 0:
            try:
                days_until_refresh = int(
                    np.log(self.saturation_threshold) / np.log(decay_rate)
                )
            except (ValueError, ZeroDivisionError):
                days_until_refresh = 0
        else:
            days_until_refresh = 0
        
        # Determine saturation velocity and refresh urgency
        if current_saturation > 0.8:
            saturation_velocity = "increasing"
            refresh_urgency = "immediate"
        elif current_saturation > self.saturation_threshold:
            saturation_velocity = "stable"
            refresh_urgency = "soon"
        else:
            saturation_velocity = "decreasing"
            refresh_urgency = "monitor"
        
        return AdstockSaturation(
            channel=channel,
            current_saturation=current_saturation,
            decay_rate=decay_rate,
            days_until_refresh=max(0, days_until_refresh),
            saturation_velocity=saturation_velocity,
            refresh_urgency=refresh_urgency
        )
    
    def calculate_decay_from_performance(
        self,
        channel: str,
        performance_data: List[Dict],
        metric_key: str = "conversions"
    ) -> Tuple[float, float]:
        """
        Calculate decay rate from performance data.
        
        Args:
            channel: Channel name
            performance_data: List of performance dictionaries
            metric_key: Key to extract from performance data (e.g., "conversions", "clicks")
        
        Returns:
            Tuple of (decay_rate, std_error)
        """
        if not performance_data:
            return 0.7, 0.5  # Default values
        
        # Extract metric values
        values = [float(d.get(metric_key, 0)) for d in performance_data if metric_key in d]
        
        if len(values) < 3:
            return 0.7, 0.5  # Not enough data
        
        # Fit decay model
        result = self.fit_decay_rate(np.array(values))
        
        return result.decay_rate, result.std_error