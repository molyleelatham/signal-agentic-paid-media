# Orchestration Agent Policy

## Agent Overview
**Name**: orchestration_agent
**Purpose**: Central coordinator for all AI agents
**Location**: `services/agents/orchestration_agent.py`
**Base Class**: `BaseAgent`

## Agent Description
The Orchestration Agent is the central coordinator for the SIGNAL platform. It manages the execution of specialized agents, handles agent priorities and dependencies, aggregates agent outputs into unified decisions, handles agent failures and fallbacks, and provides overall system intelligence.

## Capabilities
- Coordinates execution of specialized agents
- Manages agent priorities and dependencies
- Aggregates agent outputs into unified decisions
- Handles agent failures and fallbacks
- Provides overall system intelligence
- Manages agent lifecycle and resource allocation

## Input Schema
```python
{
  "task_type": str,  # planning, media_buying, intelligence, optimization
  "context": Dict,
  "priority": str,  # critical, high, medium, low
  "deadline": Optional[datetime],
  "required_agents": List[str],
  "constraints": Dict
}
```

## Output Schema
```python
{
  "task_id": str,
  "status": str,  # completed, partial, failed
  "agent_results": Dict[str, Any],
  "aggregated_decision": Dict,
  "confidence": float,
  "fallback_used": bool,
  "execution_time": float
}
```

## Managed Agents
1. **Market Analysis Agent**: Market intelligence and insights
2. **Content Brief Agent**: Creative brief generation
3. **Bid Strategy Agent**: Strategic bidding decisions
4. **Creative Optimization Agent**: Creative performance optimization

## Priority Framework
- **Critical**: System-critical tasks, must complete within 5 minutes
- **High**: Important tasks, complete within 15 minutes
- **Medium**: Standard tasks, complete within 30 minutes
- **Low**: Background tasks, complete within 1 hour

## Dependency Management
The agent manages dependencies:
- **Sequential**: Agents must execute in specific order
- **Parallel**: Agents can execute simultaneously
- **Conditional**: Agent execution depends on previous results
- **Optional**: Agent provides enhancement but not required

## Aggregation Strategy
When multiple agents provide input:
1. **Weighted Confidence**: Weight by agent confidence scores
2. **Consensus**: Require agreement for critical decisions
3. **Voting**: Majority rule for non-critical decisions
4. **Expert System**: Use domain-specific agent as authority

## Failure Handling
For each agent failure:
1. **Retry**: Attempt up to 3 times with exponential backoff
2. **Fallback**: Use simpler algorithmic approach
3. **Degradation**: Continue with reduced functionality
4. **Escalation**: Flag for human intervention

## Resource Management
- **Timeout**: Maximum execution time per agent (5 min)
- **Memory Limit**: Maximum memory per agent (1GB)
- **Rate Limiting**: Prevent agent overload
- **Queue Management**: Prioritize critical tasks

## Integration Points
- **All Agents**: Coordinates execution of all specialized agents
- **Planning Service**: Provides planning context
- **Media Buying Service**: Provides execution context
- **Overmind Tracer**: Logs orchestration decisions
- **Thrad Integration**: Manages auction-based decisions

## Constraints
- Maximum concurrent agents: 4
- Maximum total execution time: 30 minutes
- Minimum confidence for decision: 0.5
- Must log all agent executions
- Must handle all agent failures gracefully

## Decision Rules
- If all agents agree: Use consensus decision
- If agents disagree: Use weighted confidence
- If critical disagreement: Flag for human review
- If insufficient confidence: Request additional context

## Optimization Targets
- Reduce average orchestration time by 20%
- Improve agent success rate to 95%
- Reduce fallback usage to < 10%
- Maintain > 0.8 confidence on 90% of decisions

## Evaluation Metrics
- Task completion rate
- Average execution time
- Agent failure rate
- Fallback usage rate
- Decision confidence distribution
- Human intervention rate