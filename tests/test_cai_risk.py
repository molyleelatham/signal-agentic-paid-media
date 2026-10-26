"""Offline tests for the concentration-risk index."""

import pytest

from services.analytics.cai_risk import CAIRiskMonitor


def test_cai_is_the_herfindahl_index_of_impression_share():
    monitor = CAIRiskMonitor()

    assert monitor.compute_cai({}) == 0.0
    assert monitor.compute_cai({"only": 10.0}) == pytest.approx(1.0)
    assert monitor.compute_cai({"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0}) == pytest.approx(0.25)
    # Shares are normalised, so raw impression counts are fine.
    assert monitor.compute_cai({"a": 25.0, "b": 75.0}) == pytest.approx(0.25**2 + 0.75**2)


def test_goal_adjustment_flags_concentration_outside_tolerance():
    monitor = CAIRiskMonitor()

    brand = monitor.goal_adjusted_risk(actual_cai=0.25, goal_type="brand_awareness")
    assert brand.target_cai == pytest.approx(0.20)
    assert brand.flag is False
    assert brand.direction == "too_concentrated"

    retargeting = monitor.goal_adjusted_risk(actual_cai=0.25, goal_type="retargeting")
    # Target 0.80, tolerance 0.10, so deviation 0.55 leaves a risk score of 0.45.
    assert retargeting.target_cai == pytest.approx(0.80)
    assert retargeting.risk_score == pytest.approx(0.45)
    assert retargeting.flag is True
    assert retargeting.direction == "too_dispersed"


def test_unknown_goal_is_rejected():
    with pytest.raises(ValueError, match="Unknown goal type"):
        CAIRiskMonitor().goal_adjusted_risk(0.5, "not_a_goal")
