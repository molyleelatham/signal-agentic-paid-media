"""Offline tests for asymmetric P&L and the attention-token score."""

import pytest

from services.analytics.asymmetric_pnl import AsymmetricPnLScorer


def test_wasted_attention_is_penalised_at_lambda_two():
    scorer = AsymmetricPnLScorer()
    result = scorer.position_pnl(
        conversions=10,
        avg_order_value=50.0,
        total_impressions=2000,
        converting_impressions=1000,
        total_clicks=20,
        converting_clicks=10,
        cpm=10.0,
        cpc=1.0,
    )

    # Wasted impressions: 1000 * 10 / 1000 = 10. Wasted clicks: 10 * 1 = 10.
    assert result.gross_revenue == pytest.approx(500.0)
    assert result.attention_waste_cost == pytest.approx(20.0)
    assert result.lambda_applied == pytest.approx(2.0)
    assert result.net_pnl == pytest.approx(500.0 - 2.0 * 20.0)
    assert result.efficiency_ratio == pytest.approx(500.0 / 20.0)


def test_custom_lambda_changes_only_the_penalty():
    scorer = AsymmetricPnLScorer(lambda_penalty=3.0)
    result = scorer.position_pnl(
        conversions=1,
        avg_order_value=100.0,
        total_impressions=1000,
        converting_impressions=0,
        total_clicks=0,
        converting_clicks=0,
        cpm=10.0,
        cpc=1.0,
    )

    assert result.attention_waste_cost == pytest.approx(10.0)
    assert result.net_pnl == pytest.approx(100.0 - 30.0)
    assert result.lambda_applied == pytest.approx(3.0)


def test_positive_pnl_pays_a_reward_and_no_penalty():
    scorer = AsymmetricPnLScorer()
    result = scorer.position_pnl(
        conversions=10,
        avg_order_value=50.0,
        total_impressions=2000,
        converting_impressions=1000,
        total_clicks=20,
        converting_clicks=10,
        cpm=10.0,
        cpc=1.0,
    )

    reward = scorer.calculate_token_reward(result)
    penalty = scorer.calculate_token_penalty(result, stake_amount=5.0)

    # Base reward is net P&L / 10. Efficiency bonus is (ratio - 1) * 50.
    assert reward.transaction_type == "reward"
    assert reward.amount == pytest.approx(460.0 / 10.0 + (25.0 - 1.0) * 50.0)
    assert penalty.amount == 0.0
    assert penalty.metadata["reason"] == "positive_pnl_no_penalty"


def test_negative_pnl_burns_tokens_from_stake_first():
    scorer = AsymmetricPnLScorer()
    result = scorer.position_pnl(
        conversions=1,
        avg_order_value=10.0,
        total_impressions=10000,
        converting_impressions=0,
        total_clicks=90,
        converting_clicks=0,
        cpm=10.0,
        cpc=1.0,
    )

    # Waste = 10000 * 10 / 1000 + 90 = 190. Net = 10 - 2 * 190 = -370.
    assert result.net_pnl == pytest.approx(-370.0)
    base_burn = 370.0 / 20.0 * 2.0

    unstaked = scorer.calculate_token_penalty(result)
    assert unstaked.amount == pytest.approx(-base_burn)
    assert unstaked.metadata["stake_burn"] == pytest.approx(0.0)

    staked = scorer.calculate_token_penalty(result, stake_amount=100.0, stake_multiplier=1.0)
    stake_burn = min(100.0, base_burn * 1.5)
    assert staked.metadata["base_burn"] == pytest.approx(base_burn)
    assert staked.metadata["stake_burn"] == pytest.approx(stake_burn)
    assert staked.amount == pytest.approx(-(stake_burn + max(0.0, base_burn - stake_burn)))


def test_reward_multipliers_scale_the_payout():
    scorer = AsymmetricPnLScorer()
    result = scorer.position_pnl(
        conversions=10,
        avg_order_value=50.0,
        total_impressions=2000,
        converting_impressions=1000,
        total_clicks=20,
        converting_clicks=10,
        cpm=10.0,
        cpc=1.0,
    )
    plain = scorer.calculate_token_reward(result)
    scaled = scorer.calculate_token_reward(
        result,
        difficulty_multiplier=2.0,
        stake_multiplier=1.5,
    )

    assert scaled.amount == pytest.approx(plain.amount * 2.0 * 1.5)
