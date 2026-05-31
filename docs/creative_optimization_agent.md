# Creative Optimization Agent Policy

## Agent Overview
**Name**: creative_optimization_agent
**Purpose**: Analyzes and optimizes creative performance
**Location**: `services/agents/creative_optimization_agent.py`
**Base Class**: `BaseAgent`

## Agent Description
The Creative Optimization Agent analyzes creative performance data to identify strengths and weaknesses, suggests specific optimizations, and generates creative variations for testing. It uses LLM reasoning to provide actionable optimization recommendations.

## Capabilities
- Analyzes creative performance data
- Identifies strengths and weaknesses
- Suggests specific optimizations
- Generates creative variations for testing
- Predicts performance lift from optimizations

## Input Schema
```python
{
  "creative_id": str,
  "creative_type": str,  # image, video, carousel, text
  "platform": str,
  "performance_metrics": Dict,
  "creative_assets": Dict,
  "target_audience": str,
  "campaign_goal": str,
  "historical_performance": Dict
}
```

## Output Schema
```python
{
  "creative_id": str,
  "performance_score": float,  # 0-100
  "strengths": List[str],
  "weaknesses": List[str],
  "optimization_suggestions": List[str],
  "predicted_lift": float,  # percentage
  "confidence": float  # 0-1
}
```

## Performance Analysis Dimensions
The agent analyzes:
1. **Visual Elements**: Color, composition, imagery quality
2. **Copy Elements**: Headline, body text, CTA clarity
3. **Platform Fit**: Alignment with platform best practices
4. **Audience Resonance**: Engagement with target audience
5. **Brand Consistency**: Alignment with brand guidelines
6. **Historical Context**: Performance over time

## Optimization Categories
- **Visual**: Image quality, color scheme, composition
- **Copy**: Headline, body text, CTA optimization
- **Format**: Aspect ratio, duration, layout
- **Targeting**: Audience segment refinement
- **Timing**: Dayparting, scheduling optimization

## Variation Generation
For each optimization, the agent generates:
- Variation type (headline, image, CTA, etc.)
- Suggested change with specific details
- Reasoning for the change
- Expected improvement with prediction

## Performance Scoring
- **90-100**: Excellent, maintain and scale
- **70-89**: Good, minor optimizations recommended
- **50-69**: Average, significant optimizations needed
- **<50**: Poor, major overhaul or replacement needed

## Platform-Specific Guidelines
- **Meta**: Visual quality, social proof, clear CTA
- **Google**: Relevance score, ad extensions, landing page alignment
- **TikTok**: Authenticity, trend alignment, first 3 seconds
- **Microsoft**: Professional tone, clear value, B2B relevance

## Constraints
- Minimum confidence: 0.6 for recommendations
- Maximum variations per creative: 5
- Predicted lift must be > 5% to suggest change
- Performance score must be based on at least 1000 impressions

## Integration Points
- **Campaign Performance**: Receives creative performance data
- **Adstock Decay**: Considers creative fatigue
- **A/B Testing**: Provides variations for testing
- **Overmind Tracer**: Logs analysis for optimization

## Failure Handling
- If confidence < 0.6, request more performance data
- If performance < 50 on low impressions, flag as inconclusive
- If variations exceed 5, prioritize top 3 by predicted lift
- If brand guidelines conflict, flag for human review

## Optimization Targets
- Improve average creative performance score by 25%
- Increase prediction accuracy to 80%
- Reduce creative fatigue by 30%
- Maintain > 70% acceptance rate of suggestions

## Evaluation Metrics
- Performance score distribution
- Prediction accuracy (actual vs. predicted lift)
- Suggestion acceptance rate
- Time to performance improvement
- Creative lifespan extension