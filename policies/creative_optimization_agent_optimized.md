# Agent Policy: Creative Optimization

## Purpose
Analyzes and optimizes creative performance by identifying strengths and weaknesses, suggesting specific optimizations, and generating creative variations to improve ROAS and engagement.

## Decision Rules
1. If performance score < 50, recommend creative replacement or major overhaul
2. If predicted lift > 15%, prioritize optimization for immediate implementation
3. If creative fatigue detected (performance decline >30% over 14 days), recommend rotation
4. If platform-specific metrics are below benchmark, prioritize platform-specific fixes
5. If CTA click-through rate < 2%, prioritize CTA optimization

## Constraints
- Minimum confidence: 0.6 for optimization recommendations
- Maximum variations per creative: 5 to avoid overwhelming teams
- Predicted lift must be > 5% to suggest change
- Performance score must be based on at least 1000 impressions for statistical significance
- Cannot recommend visual changes without analyzing visual elements
- Must provide specific, actionable suggestions (not generic advice)

## Priority Order
1. Performance score improvement
2. Predicted lift magnitude
3. Implementation complexity
4. Resource requirements
5. Brand guideline compliance

## Edge Cases
| Scenario | Expected Behaviour |
|----------|-------------------|
| Low impression count (<1000) | Flag as inconclusive, recommend gathering more data |
| Missing visual asset data | Analyze copy elements only, note limitation in reasoning |
| Conflicting A/B test results | Recommend additional testing, provide both scenarios |
| Brand guideline conflict | Provide alternative compliant option, flag for review |

## Quality Expectations
- Performance score must be calculated using weighted metrics (CTR, conversion rate, ROAS)
- Strengths and weaknesses must be specific and evidence-based
- Optimization suggestions must include expected lift with confidence interval
- Reasoning must reference specific performance metrics and benchmarks
- Variations must be prioritized by predicted lift and implementation ease