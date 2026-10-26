"""Offline tests for adstock decay and creative rotation."""

import numpy as np
import pytest

from services.trading.adstock_decay import AdstockDecayMonitor, CreativeRotationManager


def _geometric(initial: float, lambda_decay: float, days: int) -> np.ndarray:
    t = np.arange(days)
    return initial * (lambda_decay ** t)


def test_fit_recovers_a_geometric_decay():
    monitor = AdstockDecayMonitor()
    series = _geometric(initial=80.0, lambda_decay=0.85, days=25)

    result = monitor.fit_adstock_lambda(series)

    assert result.lambda_decay == pytest.approx(0.85, abs=1e-3)
    assert result.initial_effect == pytest.approx(80.0, rel=1e-3)
    assert result.signal == "hold"
    assert result.confidence == "high"


def test_decay_signal_thresholds():
    monitor = AdstockDecayMonitor()

    assert monitor.classify_decay_signal(0.71) == "hold"
    assert monitor.classify_decay_signal(0.70) == "reduce"
    assert monitor.classify_decay_signal(0.41) == "reduce"
    assert monitor.classify_decay_signal(0.40) == "exit"
    assert monitor.classify_decay_signal(0.2) == "exit"


def test_short_series_is_a_monitor_signal():
    result = AdstockDecayMonitor().fit_adstock_lambda(np.array([10.0, 8.0]))

    assert result.lambda_decay == pytest.approx(0.5)
    assert result.signal == "monitor"
    assert result.confidence == "low"
    assert result.initial_effect == pytest.approx(10.0)


def test_half_life_and_daily_decay():
    monitor = AdstockDecayMonitor()

    assert monitor.estimate_half_life(0.5) == pytest.approx(1.0)
    assert monitor.estimate_half_life(0.0) == float("inf")
    assert monitor.calculate_decay_rate(0.8) == pytest.approx(0.2)


def test_fast_decay_recommends_rotation():
    monitor = AdstockDecayMonitor()
    manager = CreativeRotationManager(monitor)
    series = _geometric(initial=100.0, lambda_decay=0.2, days=12)
    for value in series:
        manager.add_creative_data("creative-1", float(value))

    recommendations = manager.get_rotation_recommendations()

    assert len(recommendations) == 1
    assert recommendations[0]["creative_id"] == "creative-1"
    assert recommendations[0]["signal"] == "exit"
    assert recommendations[0]["recommendation"] == (
        "Creative effectiveness is exhausted. Rotate immediately."
    )
    assert recommendations[0]["half_life_days"] == pytest.approx(
        monitor.estimate_half_life(recommendations[0]["lambda_decay"])
    )


def test_fewer_than_three_points_has_no_recommendation():
    manager = CreativeRotationManager()
    manager.add_creative_data("creative-1", 10.0)
    manager.add_creative_data("creative-1", 9.0)

    assert manager.get_creative_decay_status("creative-1") is None
    assert manager.get_rotation_recommendations() == []
