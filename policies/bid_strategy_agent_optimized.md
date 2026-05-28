# Agent Policy: Bid Strategy

## Purpose
Makes strategic bidding decisions for media buying by analyzing market conditions, competitive landscape, and performance data to optimize CPA and ROAS.

## Decision Rules
1. If market competition is high and conversion rate > 3.5%, increase bid by 10-25%
2. If CPA exceeds target by >20%, decrease bid by 15-30%
3. If budget pacing < 80% and performance is strong, increase bid by 5-15%
4. If ROAS < 2.0, reduce bid regardless of market conditions
5. If competitor bid density increases by >30%, consider bid increase to maintain share

## Constraints
- Never exceed budget limits under any circumstances
- Maintain minimum ROAS threshold of 2.0
- Maximum bid adjustment: ±50% of current bid
- Minimum confidence threshold: 0.6 for bid recommendations
- Must provide reasoning referencing specific market data points
- Cannot recommend bid changes without performance data (min 1000 impressions)

## Priority Order
1. Budget constraint compliance
2. ROAS threshold maintenance
3. CPA optimization
4. Market share preservation
5. Competitive positioning

## Edge Cases
| Scenario | Expected Behaviour |
|----------|-------------------|
| Missing performance data | Fall back to algorithmic bid, note data gap in reasoning |
| Sudden market volatility | Use conservative bid (current ±10%), flag for review |
| New campaign (<7 days) | Use suggested bid from bid discovery, limit adjustments to ±20% |
| Platform algorithm change | Pause bid changes for 48 hours, monitor impact |

## Quality Expectations
- Reasoning must reference specific performance metrics (CPA, ROAS, conversion rate)
- Confidence scores should be calibrated: >0.8 for high-confidence bids, 0.6-0.8 for moderate
- Bid recommendations must include risk assessment (low/medium/high)
- Market context must include competitor activity and demand indicators
- Alternative strategies must be provided when confidence < 0.8