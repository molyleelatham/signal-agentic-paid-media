# Agent Policy: Orchestration

## Purpose
Central coordinator for all AI agents that manages execution, priorities, dependencies, aggregates outputs into unified decisions, handles failures and fallbacks, and provides overall system intelligence.

## Decision Rules
1. If task priority is critical, execute required agents sequentially with 5-minute timeout each
2. If all agents agree on decision, use consensus with high confidence
3. If agents disagree, use weighted confidence based on historical agent accuracy
4. If agent fails, retry up to 3 times with exponential backoff before fallback
5. If deadline approaching and partial results available, return partial with degradation flag

## Constraints
- Maximum concurrent agents: 4 to prevent resource overload
- Maximum total execution time: 30 minutes for any task
- Minimum confidence for unified decision: 0.5
- Must log all agent executions with timestamps and outcomes
- Must handle all agent failures gracefully without system crash
- Cannot proceed without required agents unless fallback is available

## Priority Order
1. Task completion and deadline adherence
2. Agent success rate and reliability
3. Decision confidence and quality
4. Resource efficiency and execution time
5. Fallback minimization

## Edge Cases
| Scenario | Expected Behaviour |
|----------|-------------------|
| Required agent unavailable | Use fallback algorithmic approach, note degradation |
| Agent timeout on critical task | Escalate to human intervention, provide partial results |
| Conflicting agent outputs | Use weighted confidence voting, flag for review if <0.7 confidence |
| Resource exhaustion | Queue lower-priority tasks, prioritize critical tasks |

## Quality Expectations
- Execution time must be tracked and optimized for each agent
- Confidence scores must reflect agreement level among agents
- Fallback usage must be minimized (<10% target) and logged
- Aggregation strategy must be documented and consistent
- All failures must be logged with root cause analysis
- Decision reasoning must reference specific agent outputs and weights