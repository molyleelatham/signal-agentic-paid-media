"""
Asymmetric P&L Scorer with Attention Token Rewards.

This implements Module 8 from the technical spec:
- Asymmetric P&L scoring with loss aversion
- Attention token reward/penalty calculation
- Integration with token economy
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional


@dataclass
class PnLResult:
    """Result of P&L calculation."""
    
    gross_revenue: float
    attention_waste_cost: float
    net_pnl: float
    efficiency_ratio: float
    lambda_applied: float


@dataclass
class TokenTransaction:
    """Token transaction result."""
    
    transaction_type: str  # "reward" or "penalty"
    amount: float
    metadata: Dict


class AsymmetricPnLScorer:
    """
    Asymmetric P&L Scorer implementation.
    
    This implements Module 8 from the technical spec:
    - Gross revenue: conversion value
    - Wasted attention cost: spend on impressions + clicks that didn't convert
    - Net P&L: asymmetric — wasted attention penalised at 2× rate
    - Grounded in Prospect Theory (losses loom larger than gains)
    """
    
    def __init__(self, lambda_penalty: float = 2.0):
        """
        Initialize asymmetric P&L scorer.
        
        Args:
            lambda_penalty: Loss aversion multiplier (default 2.0 from behavioral economics)
        """
        self.lambda_penalty = lambda_penalty
    
    def position_pnl(
        self,
        conversions: int,
        avg_order_value: float,
        total_impressions: int,
        converting_impressions: int,
        total_clicks: int,
        converting_clicks: int,
        cpm: float,
        cpc: float
    ) -> PnLResult:
        """
        Calculate asymmetric P&L for a position.
        
        Args:
            conversions: Number of conversions
            avg_order_value: Average order value per conversion
            total_impressions: Total impressions
            converting_impressions: Impressions that led to conversion
            total_clicks: Total clicks
            converting_clicks: Clicks that led to conversion
            cpm: Cost per mille (cost per 1000 impressions)
            cpc: Cost per click
        
        Returns:
            PnLResult with detailed P&L breakdown
        """
        # Gross revenue: conversion value
        gross_revenue = conversions * avg_order_value
        
        # Wasted attention cost
        wasted_impressions = total_impressions - converting_impressions
        wasted_clicks = total_clicks - converting_clicks
        
        attention_waste_cost = (
            (wasted_impressions * cpm / 1000) +
            (wasted_clicks * cpc)
        )
        
        # Net P&L: asymmetric — wasted attention penalised at λ× rate
        net_pnl = gross_revenue - (self.lambda_penalty * attention_waste_cost)
        
        # Efficiency ratio
        efficiency_ratio = gross_revenue / max(attention_waste_cost, 0.01)
        
        return PnLResult(
            gross_revenue=float(gross_revenue),
            attention_waste_cost=float(attention_waste_cost),
            net_pnl=float(net_pnl),
            efficiency_ratio=float(efficiency_ratio),
            lambda_applied=self.lambda_penalty
        )
    
    def calculate_token_reward(
        self,
        pnl_result: PnLResult,
        difficulty_multiplier: float = 1.0,
        stake_multiplier: float = 1.0
    ) -> TokenTransaction:
        """
        Calculate token reward based on P&L efficiency.
        
        Implements the token issuance formula from ATTENTION_TOKEN_DESIGN.md:
        - Base reward: net P&L converted to tokens
        - Efficiency bonus: higher efficiency ratio = bonus tokens
        - Difficulty multiplier: harder markets = more tokens
        
        Args:
            pnl_result: P&L calculation result
            difficulty_multiplier: Market difficulty factor (0.5 - 2.0)
            stake_multiplier: Multiplier from staking (1.0 - 3.0)
        
        Returns:
            TokenTransaction with reward details
        """
        if pnl_result.net_pnl < 0:
            # No reward for negative P&L (penalties handled separately)
            return TokenTransaction(
                transaction_type="reward",
                amount=0.0,
                metadata={"reason": "negative_pnl_no_reward"}
            )
        
        # Base reward: 1 token per $10 of net revenue
        base_reward = pnl_result.net_pnl / 10.0
        
        # Efficiency bonus: higher efficiency ratio = bonus tokens
        efficiency_bonus = max(0.0, (pnl_result.efficiency_ratio - 1.0) * 50)
        
        # Apply multipliers
        total_reward = (base_reward + efficiency_bonus) * difficulty_multiplier * stake_multiplier
        
        return TokenTransaction(
            transaction_type="reward",
            amount=float(total_reward),
            metadata={
                "base_amount": float(base_reward),
                "efficiency_bonus": float(efficiency_bonus),
                "difficulty_multiplier": difficulty_multiplier,
                "stake_multiplier": stake_multiplier,
                "net_pnl": pnl_result.net_pnl,
                "efficiency_ratio": pnl_result.efficiency_ratio
            }
        )
    
    def calculate_token_penalty(
        self,
        pnl_result: PnLResult,
        stake_amount: float = 0.0,
        stake_multiplier: float = 1.0
    ) -> TokenTransaction:
        """
        Calculate token penalty for wasted attention.
        
        Implements the token burning formula from ATTENTION_TOKEN_DESIGN.md:
        - Base burn: 1 token per $20 of losses (with 2x loss aversion)
        - If staked: burn from stake first with multiplier
        
        Args:
            pnl_result: P&L calculation result
            stake_amount: Tokens staked on this position
            stake_multiplier: Current stake multiplier
        
        Returns:
            TokenTransaction with penalty details
        """
        if pnl_result.net_pnl >= 0:
            # No penalty for positive P&L
            return TokenTransaction(
                transaction_type="penalty",
                amount=0.0,
                metadata={"reason": "positive_pnl_no_penalty"}
            )
        
        # Base burn: 1 token per $20 of losses (with 2x loss aversion)
        base_burn = abs(pnl_result.net_pnl) / 20.0 * 2.0
        
        stake_burn = 0.0
        balance_burn = base_burn
        
        # If staked, burn from stake first with multiplier
        if stake_amount > 0:
            # Stake burn: 1.5x multiplier on stakes
            stake_burn = min(stake_amount, base_burn * 1.5 * stake_multiplier)
            balance_burn = max(0.0, base_burn - stake_burn)
        
        total_penalty = stake_burn + balance_burn
        
        return TokenTransaction(
            transaction_type="penalty",
            amount=-float(total_penalty),  # Negative for burning
            metadata={
                "stake_burn": float(stake_burn),
                "balance_burn": float(balance_burn),
                "total_penalty": float(total_penalty),
                "base_burn": float(base_burn),
                "stake_amount": stake_amount,
                "stake_multiplier": stake_multiplier,
                "net_pnl": pnl_result.net_pnl
            }
        )
    
    def pnl_to_tokens(
        self,
        pnl_result: PnLResult,
        stake_amount: float = 0.0,
        stake_multiplier: float = 1.0,
        difficulty_multiplier: float = 1.0
    ) -> Dict:
        """
        Convert P&L result to token transaction.
        
        This is the bridge between Module 8 (P&L) and the token system.
        
        Args:
            pnl_result: P&L calculation result
            stake_amount: Tokens staked on this position
            stake_multiplier: Current stake multiplier
            difficulty_multiplier: Market difficulty factor
        
        Returns:
            Dict with reward/penalty breakdown
        """
        if pnl_result.net_pnl >= 0:
            reward = self.calculate_token_reward(
                pnl_result,
                difficulty_multiplier,
                stake_multiplier
            )
            return {
                "transaction_type": "reward",
                "amount": reward.amount,
                "reward": reward.metadata,
                "penalty": None
            }
        else:
            penalty = self.calculate_token_penalty(
                pnl_result,
                stake_amount,
                stake_multiplier
            )
            return {
                "transaction_type": "penalty",
                "amount": penalty.amount,
                "reward": None,
                "penalty": penalty.metadata
            }


class AttentionTokenCalculator:
    """
    High-level attention token calculator integrating P&L scoring.
    
    Provides a unified interface for calculating token rewards/penalties
    based on campaign performance.
    """
    
    def __init__(
        self,
        lambda_penalty: float = 2.0,
        token_issuance_rate: float = 0.1,
        token_burn_rate: float = 0.05
    ):
        """
        Initialize attention token calculator.
        
        Args:
            lambda_penalty: Loss aversion multiplier for P&L
            token_issuance_rate: Tokens per $10 revenue (0.1 = 1 token per $10)
            token_burn_rate: Tokens per $20 loss (0.05 = 1 token per $20)
        """
        self.pnl_scorer = AsymmetricPnLScorer(lambda_penalty)
        self.token_issuance_rate = token_issuance_rate
        self.token_burn_rate = token_burn_rate
    
    def calculate_market_difficulty(
        self,
        competitor_score: float,
        intent_volume: int,
        platform_cpm_trend: float
    ) -> float:
        """
        Calculate market difficulty factor.
        
        Args:
            competitor_score: Competitor coverage score (0-1)
            intent_volume: Thrad intent volume
            platform_cpm_trend: Platform CPM trend (0-2, 1 = baseline)
        
        Returns:
            Market difficulty factor (0.5 - 2.0)
        """
        import numpy as np
        
        # Normalize competitor score to difficulty
        competitor_difficulty = 0.5 + (competitor_score * 1.0)  # 0.5 - 1.5
        
        # Log-normalize intent volume
        intent_difficulty = 0.5 + min(1.0, np.log1p(intent_volume) / np.log1p(100000))
        
        # Platform trend adjustment
        platform_difficulty = max(0.5, min(1.5, platform_cpm_trend))
        
        # Weighted average
        difficulty = (
            competitor_difficulty * 0.4 +
            intent_difficulty * 0.4 +
            platform_difficulty * 0.2
        )
        
        return max(0.5, min(2.0, difficulty))
    
    def calculate_complete_token_transaction(
        self,
        performance_data: Dict,
        stake_info: Dict = None,
        market_context: Dict = None
    ) -> Dict:
        """
        Calculate complete token transaction from performance data.
        
        Args:
            performance_data: Dict with performance metrics
            stake_info: Dict with stake information
            market_context: Dict with market difficulty parameters
        
        Returns:
            Complete token transaction with all components
        """
        # Extract performance data
        pnl_result = self.pnl_scorer.position_pnl(
            conversions=performance_data.get("conversions", 0),
            avg_order_value=performance_data.get("avg_order_value", 0),
            total_impressions=performance_data.get("total_impressions", 0),
            converting_impressions=performance_data.get("converting_impressions", 0),
            total_clicks=performance_data.get("total_clicks", 0),
            converting_clicks=performance_data.get("converting_clicks", 0),
            cpm=performance_data.get("cpm", 0),
            cpc=performance_data.get("cpc", 0)
        )
        
        # Extract stake info
        stake_amount = stake_info.get("amount", 0.0) if stake_info else 0.0
        stake_multiplier = stake_info.get("multiplier", 1.0) if stake_info else 1.0
        
        # Calculate market difficulty
        if market_context:
            difficulty_multiplier = self.calculate_market_difficulty(
                competitor_score=market_context.get("competitor_score", 0.5),
                intent_volume=market_context.get("intent_volume", 1000),
                platform_cpm_trend=market_context.get("cpm_trend", 1.0)
            )
        else:
            difficulty_multiplier = 1.0
        
        # Convert P&L to tokens
        token_result = self.pnl_scorer.pnl_to_tokens(
            pnl_result,
            stake_amount,
            stake_multiplier,
            difficulty_multiplier
        )
        
        return {
            "pnl_result": {
                "gross_revenue": pnl_result.gross_revenue,
                "attention_waste_cost": pnl_result.attention_waste_cost,
                "net_pnl": pnl_result.net_pnl,
                "efficiency_ratio": pnl_result.efficiency_ratio,
                "lambda_applied": pnl_result.lambda_applied
            },
            "token_transaction": token_result,
            "market_difficulty": difficulty_multiplier,
            "stake_applied": stake_amount > 0
        }