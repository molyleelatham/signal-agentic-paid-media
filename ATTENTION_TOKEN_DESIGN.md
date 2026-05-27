# Attention Token System - Financial Engineering & Gamification Design

## Overview

The Attention Token (ATTN) system creates a game-theoretic framework for media buying, where tokens represent successful attention acquisition and conversion. This design draws inspiration from attention economics theory and behavioral finance to create an engaging, performance-driven ecosystem.

## Theoretical Foundation

### Attention Economics

The core concept is that attention is a scarce resource, and media buying is essentially the purchase of attention. Traditional metrics (CPM, CPC) measure the cost of attention but not its value. Our token system measures the *efficiency* of attention acquisition.

**Key Insight**: Not all attention is equal. Attention that converts is valuable; attention that doesn't convert is waste. The token system rewards efficient converters and penalizes waste.

### Prospect Theory Integration

Drawing from Kahneman & Tversky's Prospect Theory:
- **Loss Aversion**: Losses loom larger than equivalent gains
- **Reference Points**: Users evaluate outcomes relative to expectations
- **Probability Weighting**: Users overestimate low-probability events

Our token system applies these principles:
- Token penalties for waste are amplified (2x multiplier)
- Staking creates reference points for risk-taking
- Leaderboards create social comparison (probability weighting)

## Token Mechanics

### Token Definition

```
Attention Token (ATTN)
- Symbol: ATTN
- Type: Utility token
- Supply: Dynamic (expands/contracts based on platform performance)
- Initial Supply: 1,000,000 tokens
- Decimal Places: 8
```

### Token Issuance (Proof-of-Conversion)

Tokens are minted when attention is efficiently converted to value.

#### Issuance Formula

```python
def calculate_token_issuance(
    gross_revenue: float,
    attention_cost: float,
    efficiency_ratio: float,
    market_difficulty: float,
    stake_multiplier: float = 1.0
) -> TokenIssuance:
    """
    Calculate token issuance based on attention conversion efficiency.
    
    Args:
        gross_revenue: Revenue generated from conversions
        attention_cost: Cost of acquiring attention (CPM + CPC waste)
        efficiency_ratio: revenue / attention_cost
        market_difficulty: Market competitiveness factor (0.5 - 2.0)
        stake_multiplier: Multiplier from staking (1.0 - 3.0)
    
    Returns:
        TokenIssuance with amount and breakdown
    """
    # Base issuance: 1 token per $10 of net revenue
    net_pnl = gross_revenue - attention_cost
    base_tokens = max(0, net_pnl / 10.0)
    
    # Efficiency bonus: Extra tokens for high efficiency ratios
    # efficiency_ratio > 1.0 = positive bonus
    # efficiency_ratio < 1.0 = no bonus (but also no penalty here)
    efficiency_bonus = max(0, (efficiency_ratio - 1.0) * 50)
    
    # Market difficulty adjustment: Harder markets = more tokens
    difficulty_adjustment = market_difficulty
    
    # Apply stake multiplier
    total_tokens = (base_tokens + efficiency_bonus) * difficulty_adjustment * stake_multiplier
    
    return TokenIssuance(
        base_amount=base_tokens,
        efficiency_bonus=efficiency_bonus,
        difficulty_multiplier=difficulty_adjustment,
        stake_multiplier=stake_multiplier,
        total_amount=total_tokens
    )
```

#### Market Difficulty Score

Market difficulty is calculated based on:
- **Competitor density** (from BERTopic competitor_score)
- **Intent saturation** (from Thrad intent volume)
- **Platform competition** (average CPM trends)

```python
def calculate_market_difficulty(
    competitor_score: float,  # 0-1, from BERTopic
    intent_volume: int,       # raw Thrad volume
    platform_cpm_trend: float # 0-2, 1 = baseline
) -> float:
    """
    Calculate market difficulty factor (0.5 - 2.0).
    
    Higher = more difficult = more token rewards for success.
    """
    # Normalize competitor score to difficulty
    competitor_difficulty = 0.5 + (competitor_score * 1.0)  # 0.5 - 1.5
    
    # Log-normalize intent volume (prevent dominance)
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
```

### Token Burning (Proof-of-Waste)

Tokens are burned when attention is wasted.

#### Burning Formula

```python
def calculate_token_burning(
    gross_revenue: float,
    attention_cost: float,
    stake_amount: float = 0.0,
    stake_multiplier: float = 1.0
) -> TokenBurning:
    """
    Calculate token burning for wasted attention.
    
    Args:
        gross_revenue: Revenue generated
        attention_cost: Cost of attention
        stake_amount: Tokens staked on this position
        stake_multiplier: Current stake multiplier
    
    Returns:
        TokenBurning with amount and source
    """
    net_pnl = gross_revenue - attention_cost
    
    if net_pnl >= 0:
        return TokenBurning(amount=0.0, source="none")
    
    # Base burn: 1 token per $20 of losses (half the issuance rate)
    # Loss aversion: Apply 2x multiplier to losses
    base_burn = abs(net_pnl) / 20.0 * 2.0
    
    # If staked, burn from stake first with multiplier
    if stake_amount > 0:
        # Stake burn: Higher multiplier (1.5x) to discourage risky stakes
        stake_burn = min(stake_amount, base_burn * 1.5 * stake_multiplier)
        remaining_burn = max(0, base_burn - stake_burn)
        
        return TokenBurning(
            amount=stake_burn + remaining_burn,
            stake_burn=stake_burn,
            balance_burn=remaining_burn,
            source="stake_and_balance"
        )
    
    return TokenBurning(
        amount=base_burn,
        source="balance_only"
    )
```

### Staking Mechanism

Users can stake tokens on campaign strategies to earn multipliers on rewards.

#### Staking Tiers

```python
STAKE_TIERS = {
    "bronze": {"min_stake": 100, "multiplier": 1.1, "duration_days": 7},
    "silver": {"min_stake": 500, "multiplier": 1.25, "duration_days": 14},
    "gold": {"min_stake": 2000, "multiplier": 1.5, "duration_days": 30},
    "platinum": {"min_stake": 10000, "multiplier": 2.0, "duration_days": 90}
}

def calculate_stake_multiplier(
    stake_amount: float,
    duration_days: int,
    strategy_performance: float = 1.0  # Historical performance of strategy
) -> float:
    """
    Calculate stake multiplier based on amount and duration.
    
    Also considers strategy historical performance (bonus for proven strategies).
    """
    # Base multiplier from tier
    tier = get_stake_tier(stake_amount)
    base_multiplier = STAKE_TIERS[tier]["multiplier"]
    
    # Duration bonus: Longer stakes = higher multiplier
    duration_bonus = 1.0 + (duration_days / 180.0)  # Max 2.0x at 180 days
    
    # Strategy performance bonus
    performance_bonus = min(1.5, max(0.5, strategy_performance))
    
    total_multiplier = base_multiplier * duration_bonus * performance_bonus
    
    return min(3.0, total_multiplier)  # Cap at 3.0x
```

#### Liquidation Conditions

Stakes can be liquidated (forcibly burned) if:
1. P&L drops below -50% of stake amount
2. Campaign is paused for fraud/policy violations
3. User manually unstakes (with penalty if before minimum duration)

```python
def check_liquidation_conditions(
    stake: TokenStake,
    current_pnl: float,
    campaign_status: str
) -> LiquidationStatus:
    """
    Check if stake should be liquidated.
    """
    # P&L-based liquidation
    pnl_threshold = -0.5 * stake.stake_amount
    if current_pnl < pnl_threshold:
        return LiquidationStatus(
            should_liquidate=True,
            reason="pnl_threshold",
            recovery_amount=max(0, stake.stake_amount + current_pnl)
        )
    
    # Policy violation liquidation
    if campaign_status in ["fraud", "policy_violation"]:
        return LiquidationStatus(
            should_liquidate=True,
            reason="policy_violation",
            recovery_amount=0.0  # Full loss
        )
    
    return LiquidationStatus(should_liquidate=False, reason="none")
```

### Token Marketplace (Optional)

Enable peer-to-peer token trading for advanced gamification.

#### Marketplace Mechanics

```python
@dataclass
class TokenOrder:
    order_id: str
    user_id: str
    order_type: str  # "buy" or "sell"
    amount: float
    price: float  # ATTN per USD
    created_at: datetime
    status: str = "open"

def match_orders(buy_orders: list[TokenOrder], 
                 sell_orders: list[TokenOrder]) -> list[Trade]:
    """
    Match buy and sell orders using price-time priority.
    """
    trades = []
    
    # Sort orders
    buys = sorted(buy_orders, key=lambda x: (-x.price, x.created_at))
    sells = sorted(sell_orders, key=lambda x: (x.price, x.created_at))
    
    # Match orders
    while buys and sells:
        buy = buys[0]
        sell = sells[0]
        
        if buy.price >= sell.price:
            # Match found
            trade_amount = min(buy.amount, sell.amount)
            trade_price = (buy.price + sell.price) / 2  # Midpoint
            
            trades.append(Trade(
                buy_user=buy.user_id,
                sell_user=sell.user_id,
                amount=trade_amount,
                price=trade_price
            ))
            
            # Update orders
            buy.amount -= trade_amount
            sell.amount -= trade_amount
            
            if buy.amount == 0:
                buys.pop(0)
            if sell.amount == 0:
                sells.pop(0)
        else:
            # No match possible at current prices
            break
    
    return trades
```

## Leaderboard System

### Ranking Algorithm

Users are ranked based on a composite score:

```python
def calculate_leaderboard_score(
    token_balance: float,
    risk_adjusted_return: float,
    total_conversions: int,
    efficiency_score: float,
    stake_success_rate: float
) -> LeaderboardScore:
    """
    Calculate composite leaderboard score.
    
    Weights:
    - Token balance: 30% (raw accumulation)
    - Risk-adjusted return: 25% (Sharpe-like ratio)
    - Total conversions: 20% (scale of operations)
    - Efficiency score: 15% (attention efficiency)
    - Stake success rate: 10% (strategic skill)
    """
    # Normalize each component to 0-100 scale
    normalized_balance = min(100, token_balance / 100.0)  # 100 tokens = 100 points
    normalized_rar = min(100, max(0, (risk_adjusted_return + 2) * 25))  # -2 to +2 range
    normalized_conversions = min(100, total_conversions / 10.0)  # 10 conversions = 100 points
    normalized_efficiency = min(100, efficiency_score * 100)
    normalized_stake = min(100, stake_success_rate * 100)
    
    composite_score = (
        normalized_balance * 0.30 +
        normalized_rar * 0.25 +
        normalized_conversions * 0.20 +
        normalized_efficiency * 0.15 +
        normalized_stake * 0.10
    )
    
    return LeaderboardScore(
        composite_score=composite_score,
        token_balance_score=normalized_balance,
        risk_adjusted_score=normalized_rar,
        conversion_score=normalized_conversions,
        efficiency_score=normalized_efficiency,
        stake_score=normalized_stake
    )
```

### Leaderboard Categories

1. **All-Time**: Lifetime performance
2. **Monthly**: Performance in current month
3. **Weekly**: Performance in current week
4. **Rising Stars**: New users (< 30 days) with high growth rate
5. **Risk Masters**: Highest risk-adjusted returns
6. **Efficiency Kings**: Best attention efficiency ratios

### Achievement System

Unlockable achievements based on milestones:

```python
ACHIEVEMENTS = {
    "first_conversion": {
        "name": "First Blood",
        "description": "Complete your first conversion",
        "token_reward": 10,
        "condition": lambda stats: stats.total_conversions >= 1
    },
    "efficient_buyer": {
        "name": "Efficient Buyer",
        "description": "Achieve efficiency ratio > 2.0",
        "token_reward": 50,
        "condition": lambda stats: stats.efficiency_score > 2.0
    },
    "stake_master": {
        "name": "Stake Master",
        "description": "Successfully complete 10 stakes",
        "token_reward": 100,
        "condition": lambda stats: stats.completed_stakes >= 10
    },
    "market_pioneer": {
        "name": "Market Pioneer",
        "description": "Trade in a gap zone topic",
        "token_reward": 75,
        "condition": lambda stats: stats.gap_zones_traded > 0
    },
    "risk_taker": {
        "name": "Risk Taker",
        "description": "Achieve risk-adjusted return > 1.5",
        "token_reward": 200,
        "condition": lambda stats: stats.risk_adjusted_return > 1.5
    },
    "token_tycoon": {
        "name": "Token Tycoon",
        "description": "Accumulate 10,000 tokens",
        "token_reward": 500,
        "condition": lambda stats: stats.token_balance >= 10000
    }
}
```

## Game Loop Design

### Daily Token Cycle

```
1. Campaigns run throughout the day
   ↓
2. Performance data accumulated
   ↓
3. Midnight: Daily P&L calculation
   ↓
4. Token rewards/penalties calculated
   ↓
5. Token balances updated
   ↓
6. Leaderboards recalculated
   ↓
7. Achievements checked and unlocked
   ↓
8. Users notified of earnings/losses
```

### Weekly Token Cycle

```
1. Monday: Market intelligence updated (Tavily + BERTopic)
   ↓
2. Tuesday: Gap matrix recalculated
   ↓
3. Wednesday: Budget allocations adjusted (Thompson sampling)
   ↓
4. Thursday: Bid curves refitted (LOESS)
   ↓
5. Friday: Weekly leaderboard finalized
   ↓
6. Saturday-Sunday: Market analysis (read-only)
```

### Monthly Token Cycle

```
1. Month-end: Monthly P&L finalization
   ↓
2. Token issuance/burning for month
   ↓
3. Stake maturity checks
   ↓
4. Monthly leaderboard rewards distributed
   ↓
5. Market difficulty scores recalculated
   ↓
6. Strategy performance scores updated
```

## Risk Management

### Token Supply Controls

To prevent hyperinflation or deflation:

```python
def manage_token_supply(
    current_supply: float,
    target_supply: float,
    issuance_rate: float,
    burning_rate: float
) -> SupplyAdjustment:
    """
    Manage token supply to maintain stability.
    
    Target: Keep annual supply growth at 5-10%
    """
    supply_growth_rate = (current_supply - target_supply) / target_supply
    
    if supply_growth_rate > 0.15:  # > 15% growth
        # Too much issuance: increase burn multiplier
        return SupplyAdjustment(
            action="increase_burn_multiplier",
            multiplier=1.5,
            reason="high_growth"
        )
    elif supply_growth_rate < -0.05:  # < -5% growth (deflation)
        # Too much burning: decrease burn multiplier
        return SupplyAdjustment(
            action="decrease_burn_multiplier",
            multiplier=0.75,
            reason="deflation_risk"
        )
    else:
        return SupplyAdjustment(
            action="none",
            multiplier=1.0,
            reason="stable"
        )
```

### Position Limits

Prevent excessive risk-taking:

```python
def calculate_position_limit(
    user_token_balance: float,
    user_risk_score: float,
    campaign_risk_level: str
) -> float:
    """
    Calculate maximum position size based on user's risk profile.
    """
    # Base limit: 10% of token balance
    base_limit = user_token_balance * 0.10
    
    # Risk score adjustment: Higher risk score = lower limit
    risk_adjustment = max(0.5, min(1.5, 1.0 - user_risk_score * 0.5))
    
    # Campaign risk adjustment
    campaign_multipliers = {
        "low": 1.2,
        "medium": 1.0,
        "high": 0.7
    }
    
    campaign_adjustment = campaign_multipliers.get(campaign_risk_level, 1.0)
    
    return base_limit * risk_adjustment * campaign_adjustment
```

## Integration with P&L Scorer

The token system integrates directly with the asymmetric P&L scorer from Module 8:

```python
def pnl_to_tokens(pnl_result: dict, user_context: dict) -> TokenTransaction:
    """
    Convert P&L result to token transaction.
    
    This is the bridge between Module 8 (P&L) and the token system.
    """
    # Calculate market difficulty
    market_difficulty = calculate_market_difficulty(
        competitor_score=user_context.get("competitor_score", 0.5),
        intent_volume=user_context.get("intent_volume", 1000),
        platform_cpm_trend=user_context.get("cpm_trend", 1.0)
    )
    
    # Get stake info if any
    stake_info = user_context.get("stake", {"amount": 0.0, "multiplier": 1.0})
    
    if pnl_result["net_pnl"] >= 0:
        # Issue tokens
        issuance = calculate_token_issuance(
            gross_revenue=pnl_result["gross_revenue"],
            attention_cost=pnl_result["attention_waste_cost"],
            efficiency_ratio=pnl_result["efficiency_ratio"],
            market_difficulty=market_difficulty,
            stake_multiplier=stake_info["multiplier"]
        )
        
        return TokenTransaction(
            transaction_type="reward",
            amount=issuance.total_amount,
            metadata={
                "base_amount": issuance.base_amount,
                "efficiency_bonus": issuance.efficiency_bonus,
                "difficulty_multiplier": issuance.difficulty_multiplier,
                "stake_multiplier": issuance.stake_multiplier
            }
        )
    else:
        # Burn tokens
        burning = calculate_token_burning(
            gross_revenue=pnl_result["gross_revenue"],
            attention_cost=pnl_result["attention_waste_cost"],
            stake_amount=stake_info["amount"],
            stake_multiplier=stake_info["multiplier"]
        )
        
        return TokenTransaction(
            transaction_type="penalty",
            amount=-burning.amount,  # Negative for burning
            metadata={
                "stake_burn": burning.stake_burn,
                "balance_burn": burning.balance_burn,
                "source": burning.source
            }
        )
```

## Dashboard Elements

### User Token Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  ATTN Balance: 1,234.56789012                          │
│  +24.56 today  |  +156.78 this week  |  +678.90 this month│
└─────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────┬──────────────────┐
│  Staked Tokens   │  Available       │  Total Earned    │
│  500.00000000    │  734.56789012    │  2,456.78901234  │
└──────────────────┴──────────────────┴──────────────────┘

Recent Transactions:
- +15.67890000  Reward    Campaign #1234  Efficiency bonus 2h ago
- +10.00000000  Reward    Achievement: First Blood  5h ago
- -5.23456789   Penalty   Campaign #5678  Waste penalty  1d ago
+100.00000000  Stake     Campaign #9012  Gold tier  3d ago
```

### Leaderboard Display

```
┌─────────────────────────────────────────────────────────┐
│  🏆 Weekly Leaderboard - Top 10                        │
├─────────────────────────────────────────────────────────┤
│  #1  @trading_wizard    12,456 ATTN   🚀 +234 today    │
│  #2  @attention_master  11,234 ATTN   🚀 +189 today    │
│  #3  @efficiency_king   10,567 ATTN   🚀 +156 today    │
│  #4  @you               1,234 ATTN    🚀 +24 today     │
│  ...                                                  │
└─────────────────────────────────────────────────────────┘

Your Rank: #4 out of 1,234 traders
Risk-Adjusted Return: 1.23 (Top 15%)
Efficiency Score: 1.89 (Top 10%)
```

### Achievement Display

```
🏅 Achievements (5/15 unlocked)

✅ First Blood (+10 ATTN)
✅ Efficient Buyer (+50 ATTN)
✅ Market Pioneer (+75 ATTN)
⬜ Stake Master (8/10 stakes)
⬜ Risk Taker (RAR: 1.23/1.5)
⬜ Token Tycoon (1,234/10,000 ATTN)
```

## Technical Implementation Notes

### Token Precision

- Use DECIMAL(18, 8) for database storage
- Use Python's `decimal.Decimal` for calculations
- Avoid floating-point arithmetic for token operations

### Transaction Atomicity

All token transactions must be atomic:
```python
@transaction.atomic
def process_token_transaction(user_id: str, transaction: TokenTransaction):
    # Lock user row
    user = User.objects.select_for_update().get(id=user_id)
    
    # Calculate new balance
    new_balance = user.token_balance + transaction.amount
    
    # Validate
    if new_balance < 0:
        raise InsufficientTokensError()
    
    # Update balance
    user.token_balance = new_balance
    user.save()
    
    # Record transaction
    TokenTransaction.objects.create(
        user_id=user_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        balance_after=new_balance,
        metadata=transaction.metadata
    )
```

### Audit Trail

Maintain complete audit trail for all token operations:
- Every issuance logged with P&L reference
- Every burning logged with reason
- Every stake/unstake logged with multiplier calculation
- Every leaderboard change logged

## Future Enhancements

1. **Token Governance**: Allow token holders to vote on platform parameters
2. **Strategy Market**: Allow users to sell/buy successful strategies
3. **Tournaments**: Weekly trading competitions with prize pools
4. **Token Lending**: Allow users to lend tokens for staking at interest
5. **Derivatives**: Options/futures on token prices (advanced)
6. **Social Features**: Follow successful traders, copy their strategies

## Conclusion

The Attention Token system creates a engaging, performance-driven ecosystem that aligns user incentives with platform goals. By gamifying the financial engineering of media buying, we create a self-reinforcing cycle where:

1. Efficient attention acquisition is rewarded
2. Wasted attention is penalized
3. Strategic risk-taking is encouraged through staking
4. Social comparison drives performance improvement
5. The platform benefits from overall improved efficiency

This system transforms media buying from a cost center into a strategic game where attention is the currency and efficiency is the winning strategy.