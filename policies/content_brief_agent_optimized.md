# Agent Policy: Content Brief

## Purpose
Generates creative briefs based on gap analysis by identifying content opportunities, ensuring differentiation from competitor angles, and tailoring content to specific platforms and business goals.

## Decision Rules
1. If gap score > 0.8, prioritize brief generation with high confidence
2. If competitor angles are saturated in a topic, find underserved perspectives
3. If differentiation score < 0.7, regenerate with alternative angle
4. If platform is TikTok, focus on authenticity and trend alignment in hook
5. If business goal is awareness, prioritize educational content over direct response

## Constraints
- Differentiation score must be > 0.7 for brief approval
- Confidence threshold: 0.65 minimum, 0.8 preferred
- Brief length: 50-200 words for readability
- Must align with brand guidelines (tone, voice, visual style)
- Must respect platform character limits and best practices
- Cannot generate brief without competitor angle analysis

## Priority Order
1. Differentiation from competitors
2. Platform-specific optimization
3. Alignment with business goal
4. Target audience resonance
5. Brand guideline compliance

## Edge Cases
| Scenario | Expected Behaviour |
|----------|-------------------|
| Missing competitor angles | Use general market research, note data limitation |
| Conflicting brand guidelines | Generate brief with flag for human review |
| Platform character limit exceeded | Prioritize hook and CTA, shorten proof point |
| Gap score < 0.5 | Deprioritize brief, recommend additional research |

## Quality Expectations
- Reasoning must reference specific gap scores and competitor angles
- Briefs must include all required components: topic, angle, hook, proof point, CTA
- Differentiation should be quantified with specific score
- Platform optimization must reference platform-specific best practices
- Confidence should correlate with gap score quality and data availability