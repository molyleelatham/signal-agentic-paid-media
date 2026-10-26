"""Offline tests for the LOESS bid curve and Bayesian cold start."""

import numpy as np
import pytest
from scipy.interpolate import UnivariateSpline

from services.trading.bid_discovery import BayesianColdStart, LOESSBidDiscovery


def _sigmoid(bids: np.ndarray, midpoint: float = 1.5, steepness: float = 5.0) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-steepness * (bids - midpoint)))


def test_few_points_use_the_mean_bid():
    discovery = LOESSBidDiscovery()
    bids = np.array([1.0, 2.0, 3.0, 4.0])
    rates = np.array([0.1, 0.2, 0.15, 0.3])

    result = discovery.find_dmr_optimal(bids, rates)

    assert result.optimal_bid == pytest.approx(float(bids.mean()))
    assert result.inflection_point == pytest.approx(float(bids.mean()))
    assert result.expected_conv_rate == pytest.approx(float(rates.mean()))
    assert result.marginal_return == 0.0
    assert result.curve_confidence == "low"


def test_unsmoothed_curve_below_ten_points_and_high_confidence_at_fifty():
    discovery = LOESSBidDiscovery()
    short_bids = np.array([1.0, 2.0, 3.0])
    short_rates = np.array([0.1, 0.2, 0.3])

    short = discovery.fit_loess_curve(short_bids, short_rates)

    assert short.confidence == "low"
    assert np.array_equal(short.bid_grid, short_bids)
    assert np.array_equal(short.smoothed_conv_rate, short_rates)

    long_bids = np.linspace(0.2, 3.0, 50)
    long = discovery.fit_loess_curve(long_bids, _sigmoid(long_bids))

    assert long.confidence == "high"
    assert len(long.bid_grid) == len(long_bids)


def test_optimal_bid_sits_at_the_buffer_below_the_inflection():
    discovery = LOESSBidDiscovery(buffer=0.92)
    bids = np.linspace(0.2, 3.0, 40)
    rates = _sigmoid(bids, midpoint=1.5)

    result = discovery.find_dmr_optimal(bids, rates)
    second_derivative = UnivariateSpline(bids, rates, s=0.01, k=4).derivative(n=2)

    assert bids.min() <= result.inflection_point <= bids.max()
    assert second_derivative(result.inflection_point) == pytest.approx(0.0, abs=1e-5)
    assert result.optimal_bid == pytest.approx(result.inflection_point * discovery.buffer)
    assert result.optimal_bid < result.inflection_point
    assert result.curve_confidence == "low"


def test_custom_buffer_is_applied():
    discovery = LOESSBidDiscovery(buffer=0.5)
    bids = np.linspace(0.2, 3.0, 40)
    rates = _sigmoid(bids, midpoint=1.5)

    result = discovery.find_dmr_optimal(bids, rates)

    assert result.optimal_bid == pytest.approx(result.inflection_point * 0.5)


def test_monotonic_curve_uses_the_steepest_slope():
    discovery = LOESSBidDiscovery(buffer=1.0)
    bids = np.linspace(0.2, 2.0, 25)
    # Concave and strictly increasing: the second derivative does not change sign.
    rates = 1.0 - np.exp(-bids)

    result = discovery.find_dmr_optimal(bids, rates)

    spline_bids = bids
    # The fallback is the bid where the fitted first derivative is largest.
    spline = UnivariateSpline(spline_bids, rates, s=0.01, k=4)
    steepest = float(spline_bids[np.argmax(spline.derivative(n=1)(spline_bids))])
    assert result.inflection_point == pytest.approx(steepest)
    assert result.optimal_bid == pytest.approx(steepest)


def test_shrinkage_weight_and_cold_start_mode():
    cold = BayesianColdStart(min_observations=50, pseudo_count=30)
    prior = {"mean_optimal_bid": 2.0, "pseudo_count": 30, "std": 0.2}
    discovery = LOESSBidDiscovery()

    empty = cold.bayesian_bid([], prior, discovery)

    assert empty.mode == "cold_start"
    assert empty.n_observations == 0
    assert empty.confidence == 0.0
    assert empty.bid == pytest.approx(2.0)

    thin = [{"bid_price": 1.0, "conversion_rate": 0.2}] * 10
    thin_result = cold.bayesian_bid(thin, prior, discovery)

    assert thin_result.mode == "cold_start"
    assert thin_result.confidence == pytest.approx(10 / 40)
    # Below 50 observations the cluster optimum is the global prior, so the blend is the prior.
    assert thin_result.bid == pytest.approx(2.0)


def test_fitted_bid_is_the_shrinkage_blend():
    cold = BayesianColdStart(min_observations=50, pseudo_count=30)
    discovery = LOESSBidDiscovery()
    bids = np.linspace(0.4, 3.0, 60)
    rates = _sigmoid(bids, midpoint=1.8)
    cluster = [
        {"bid_price": float(bid), "conversion_rate": float(rate)}
        for bid, rate in zip(bids, rates)
    ]
    prior = {"mean_optimal_bid": 1.0, "pseudo_count": 30, "std": 0.1}

    result = cold.bayesian_bid(cluster, prior, discovery)
    curve = discovery.fit_loess_curve(bids, rates)
    dmr = discovery.find_dmr_optimal(curve.bid_grid, curve.smoothed_conv_rate)
    weight = 60 / 90
    expected = weight * dmr.optimal_bid + (1 - weight) * 1.0

    assert result.mode == "fitted"
    assert result.n_observations == 60
    assert result.confidence == pytest.approx(weight)
    assert result.bid == pytest.approx(expected)


def test_cold_start_explores_then_exploits():
    cold = BayesianColdStart(min_observations=50, explore_range=0.25)
    np.random.seed(0)

    exploring = cold.cold_start_bid(0, 2.0)

    assert exploring.mode == "exploring"
    assert exploring.epsilon == pytest.approx(1.0)
    assert 2.0 * 0.75 <= exploring.bid <= 2.0 * 1.25

    exploiting = cold.cold_start_bid(50, 2.0)

    assert exploiting.mode == "exploiting"
    assert exploiting.epsilon == pytest.approx(0.0)
    assert exploiting.bid == pytest.approx(2.0)


def test_empty_global_prior_uses_the_documented_defaults():
    prior = BayesianColdStart(pseudo_count=30).calculate_global_prior([])

    assert prior["mean_optimal_bid"] == pytest.approx(1.0)
    assert prior["pseudo_count"] == 30
    assert prior["std"] == pytest.approx(0.5)


def test_temporal_surface_skips_sparse_weeks():
    discovery = LOESSBidDiscovery()

    assert discovery.build_temporal_surface([]).size == 0

    sparse = [
        {"week_cohort": 1, "bid_price": 1.0, "conversion_rate": 0.1},
        {"week_cohort": 1, "bid_price": 1.2, "conversion_rate": 0.2},
    ]
    assert discovery.build_temporal_surface(sparse).size == 0
