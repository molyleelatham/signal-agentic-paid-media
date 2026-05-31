# Bid Strategy Agent Policy

## Agent Overview
**Name**: bid_strategy_agent
**Purpose**: Makes strategic bidding decisions for media buying
**Location**: `services/agents/bid_strategy_agent.py`
**Base Class**: `BaseAgent`

## Agent Description
The Bid Strategy Agent uses LLM reasoning to make strategic bidding decisions beyond algorithmic calculations. It analyzes market conditions, competitive landscape, and provides reasoning for bid decisions with risk assessment.

## Capabilities
- Analyzes market conditions and competitive landscape
- Makes strategic bidding decisions
- Provides reasoning and risk assessment for bid decisions
- Suggests alternative strategies
- Integrates with Thompson sampling and bid discovery algorithms

## Input Schema
```python
{
  "campaign_id": str,
  "platform": str,  # meta, google, tiktok, microsoft
  "current_bid": float,
  "target_cpa": float,
  "market_conditions": Dict,
  "performance_data": Dict,
  "budget_remaining": float,
  "time_period": str
}
```

## Output Schema
```python
{
  "recommended_bid": float,
  "confidence": float,  # 0-1
  "reasoning": str,
  "risk_assessment": str,
  "alternative_strategies": List[str],
  "market_context": Dict
}
```

## Decision Criteria
The agent considers:
1. **Market Conditions**: Current demand, competition levels
2. **Performance History**: Past CPA, conversion rates
3. **Budget Constraints**: Remaining budget, pacing
4. **Time Period**: Dayparting, seasonal factors
5. **Competitor Activity**: Bid density, auction dynamics
6. **Platform Specifics**: Algorithm preferences, best practices

## Risk Management
- **Low Risk**: Conservative bids, maintain current performance
- **Medium Risk**: Moderate bid adjustments, test new strategies
- **High Risk**: Aggressive bidding for high-opportunity scenarios

## Integration Points
- **Thompson Sampling**: Receives bandit allocation suggestions
- **Bid Discovery**: Uses bid range recommendations
- **Adstock Decay**: Considers saturation levels
- **Overmind Tracer**: Logs all decisions for optimization

## Constraints
- Never exceed budget limits
- Maintain minimum ROAS threshold (2.0)
- Maximum bid adjustment: ±50% of current bid
- Minimum confidence threshold: 0.6

## Failure Handling
- If confidence < 0.6, fall back to algorithmic bid
- If market data unavailable, use historical averages
- If budget constraints violated, recommend budget adjustment

## Optimization Targets
- Reduce CPA by 20% over 30 days
- Improve bid accuracy by 15%
- Increase win rate in auctions by 10%
- Maintain ROAS > 2.0

## Evaluation Metrics
- Bid accuracy vs. actual optimal bid
- CPA improvement over time
- Auction win rate
- Confidence calibration
- Risk assessment accuracy