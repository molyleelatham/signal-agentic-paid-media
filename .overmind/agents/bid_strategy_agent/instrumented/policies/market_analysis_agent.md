# Market Analysis Agent Policy

## Agent Overview
**Name**: market_analysis_agent
**Purpose**: Analyzes market intelligence and provides strategic insights
**Location**: `services/agents/market_analysis_agent.py`
**Base Class**: `BaseAgent`

## Agent Description
The Market Analysis Agent analyzes market intelligence from Tavily and other sources to identify strategic opportunities and threats, provides competitive intelligence, and generates actionable market insights for media buying decisions.

## Capabilities
- Analyzes market intelligence from multiple sources
- Identifies strategic opportunities and threats
- Provides competitive intelligence
- Generates actionable market insights
- Assesses urgency and actionability of insights

## Input Schema
```python
{
  "query": str,
  "intelligence_sources": List[str],  # tavily, internal, third-party
  "time_range": str,  # day, week, month, quarter
  "industry": str,
  "geography": str,
  "competitors": List[str],
  "focus_areas": List[str]
}
```

## Output Schema
```python
{
  "insight_type": str,
  "summary": str,
  "evidence": List[str],
  "confidence": float,  # 0-1
  "actionability": str,  # immediate, short-term, long-term
  "urgency": str,  # critical, high, medium, low
  "recommendations": List[str]
}
```

## Insight Categories
- **Trend Analysis**: Emerging market trends
- **Competitive Intelligence**: Competitor movements and strategies
- **Opportunity Detection**: Untapped market segments
- **Threat Assessment**: Risks to current strategy
- **Audience Insights**: Changing audience behaviors
- **Platform Changes**: Algorithm updates, policy changes

## Intelligence Sources
- **Tavily**: Real-time web search and analysis
- **Internal Data**: Campaign performance, customer feedback
- **Third-party**: Industry reports, market research
- **Social Listening**: Social media sentiment analysis
- **Competitor Monitoring**: Competitor campaigns and messaging

## Actionability Framework
- **Immediate**: Can be acted on within 24 hours
- **Short-term**: Can be acted on within 1 week
- **Long-term**: Strategic planning horizon (1-3 months)

## Urgency Framework
- **Critical**: Requires immediate attention (competitive threat, major opportunity)
- **High**: Should be addressed within 3 days
- **Medium**: Should be addressed within 1 week
- **Low**: Monitor and reassess periodically

## Confidence Scoring
- **0.9-1.0**: Very high confidence, multiple corroborating sources
- **0.7-0.89**: High confidence, strong evidence
- **0.5-0.69**: Moderate confidence, some uncertainty
- **<0.5**: Low confidence, treat as hypothesis

## Integration Points
- **Tavily Client**: Receives market intelligence
- **Content Brief Agent**: Provides insights for brief generation
- **Bid Strategy Agent**: Informs bid strategy decisions
- **Planning Service**: Influences allocation decisions
- **Overmind Tracer**: Logs insights for optimization

## Constraints
- Minimum confidence: 0.5 for insight generation
- Must provide at least 2 evidence sources
- Recommendations must be actionable
- Insights must be time-bound
- Must avoid speculation without evidence

## Failure Handling
- If confidence < 0.5, flag as hypothesis requiring validation
- If insufficient evidence, request additional intelligence sources
- If actionability unclear, provide multiple scenarios
- If urgency misclassified, provide time-to-impact estimate

## Optimization Targets
- Increase insight accuracy by 30%
- Improve prediction of market shifts by 25%
- Reduce false positive rate to < 15%
- Maintain > 80% actionability of insights

## Evaluation Metrics
- Insight accuracy (validated vs. actual market changes)
- Prediction horizon accuracy
- False positive/negative rates
- Time from insight to action
- Business impact of insights (ROI)