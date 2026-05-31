# Content Brief Agent Policy

## Agent Overview
**Name**: content_brief_agent
**Purpose**: Generates creative briefs based on gap analysis
**Location**: `services/agents/content_brief_agent.py`
**Base Class**: `BaseAgent`

## Agent Description
The Content Brief Generation Agent analyzes gap matrix results to identify content opportunities and generates creative briefs for high-priority gaps. It ensures differentiation from competitor angles and tailors content to specific platforms and goals.

## Capabilities
- Analyzes gap matrix results to identify opportunities
- Generates creative briefs for high-priority gaps
- Ensures differentiation from competitor angles
- Tailors content to specific platforms and goals
- Provides reasoning and confidence scores

## Input Schema
```python
{
  "gap_topic": str,
  "gap_score": float,
  "competitor_angles": List[str],
  "target_platform": str,  # meta, google, tiktok, microsoft
  "business_goal": str,  # awareness, consideration, performance
  "target_audience": str,
  "brand_guidelines": Dict,
  "performance_requirements": Dict
}
```

## Output Schema
```python
{
  "topic": str,
  "angle": str,
  "hook": str,
  "proof_point": str,
  "cta": str,
  "target_audience": str,
  "platform": str,
  "reasoning": str,
  "confidence": float,  # 0-1
  "differentiation_score": float  # 0-1
}
```

## Brief Components
- **Topic**: Content subject matter
- **Angle**: Unique perspective or approach
- **Hook**: Attention-grabbing opening
- **Proof Point**: Evidence or statistic supporting the angle
- **CTA**: Call to action aligned with business goal
- **Target Audience**: Specific audience segment
- **Platform**: Optimized for specific platform

## Differentiation Strategy
The agent ensures differentiation by:
1. Analyzing competitor angles in the gap
2. Identifying underserved perspectives
3. Leveraging brand unique selling propositions
4. Considering platform-specific best practices
5. Aligning with audience preferences

## Platform Guidelines
- **Meta**: Visual-first, lifestyle imagery, social proof
- **Google**: Search intent, clear value proposition, strong CTA
- **TikTok**: Authentic, trend-aware, short-form video
- **Microsoft**: Professional, B2B focus, clear benefit statement

## Funnel Stage Alignment
- **Awareness**: Educational content, broad appeal
- **Consideration**: Comparison content, social proof
- **Performance**: Direct response, strong urgency

## Constraints
- Differentiation score must be > 0.7
- Confidence threshold: 0.65
- Brief length: 50-200 words
- Must align with brand guidelines
- Must respect platform character limits

## Integration Points
- **Gap Matrix**: Receives gap analysis results
- **BERT Classification**: Uses keyword relevance scores
- **Tavily Intelligence**: Incorporates market trends
- **Overmind Tracer**: Logs brief generation for optimization

## Failure Handling
- If differentiation < 0.7, regenerate with alternative angle
- If confidence < 0.65, request additional gap context
- If platform guidelines violated, adjust for platform
- If brand guidelines conflict, flag for human review

## Optimization Targets
- Increase brief acceptance rate by 30%
- Improve differentiation score by 20%
- Reduce brief generation time by 25%
- Maintain confidence > 0.8 on 80% of briefs

## Evaluation Metrics
- Brief acceptance rate by creative team
- Differentiation score distribution
- Confidence calibration
- Brief-to-performance correlation
- Generation time per brief