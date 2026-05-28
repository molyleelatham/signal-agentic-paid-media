# Agent Policies

This directory contains policy documentation for all SIGNAL platform AI agents.

## Overview

Each agent has a corresponding policy MD file that documents:
- Agent purpose and capabilities
- Input/output schemas
- Decision criteria and constraints
- Integration points
- Optimization targets
- Evaluation metrics

## Agents

### 1. Bid Strategy Agent
**File**: `bid_strategy_agent.md`
**Purpose**: Makes strategic bidding decisions for media buying
**Key Capabilities**:
- Analyzes market conditions and competitive landscape
- Makes strategic bidding decisions beyond algorithmic calculations
- Provides reasoning and risk assessment
- Suggests alternative strategies

### 2. Content Brief Agent
**File**: `content_brief_agent.md`
**Purpose**: Generates creative briefs based on gap analysis
**Key Capabilities**:
- Analyzes gap matrix results
- Generates creative briefs for high-priority gaps
- Ensures differentiation from competitor angles
- Tailors content to specific platforms

### 3. Creative Optimization Agent
**File**: `creative_optimization_agent.md`
**Purpose**: Analyzes and optimizes creative performance
**Key Capabilities**:
- Analyzes creative performance data
- Identifies strengths and weaknesses
- Suggests specific optimizations
- Generates creative variations for testing

### 4. Market Analysis Agent
**File**: `market_analysis_agent.md`
**Purpose**: Analyzes market intelligence and provides strategic insights
**Key Capabilities**:
- Analyzes market intelligence from multiple sources
- Identifies strategic opportunities and threats
- Provides competitive intelligence
- Generates actionable market insights

### 5. Orchestration Agent
**File**: `orchestration_agent.md`
**Purpose**: Central coordinator for all AI agents
**Key Capabilities**:
- Coordinates execution of specialized agents
- Manages agent priorities and dependencies
- Aggregates agent outputs into unified decisions
- Handles agent failures and fallbacks

## Registration with Overmind

To register these agents with Overmind for tracing and optimization:

```bash
# View registration commands
make register-agents

# Or run the script directly
python3 scripts/register_overmind_agents.py
```

This will output the Cursor IDE commands to register each agent:
```
/overmind-register-agent services/agents/bid_strategy_agent.py
/overmind-optimize-agent bid_strategy_agent
```

## Policy Structure

Each policy follows a consistent structure:

1. **Agent Overview**: Name, purpose, location, base class
2. **Agent Description**: Detailed description of capabilities
3. **Input/Output Schemas**: Expected data structures
4. **Decision Criteria**: How the agent makes decisions
5. **Constraints**: Limits and requirements
6. **Integration Points**: Connections to other systems
7. **Failure Handling**: How to handle errors
8. **Optimization Targets**: Goals for improvement
9. **Evaluation Metrics**: How to measure success

## Updating Policies

When modifying agent behavior:

1. Update the corresponding policy MD file
2. Update the agent implementation
3. Re-register with Overmind if needed
4. Test changes against evaluation metrics

## Policy Enforcement

Policies are enforced through:
- Code-level constraints in agent implementations
- Overmind tracing and evaluation
- Unit tests for policy compliance
- Integration tests for end-to-end behavior

## Related Documentation

- `LOCAL_DEVELOPMENT.md` - Overmind setup and configuration
- `AGENTS_ARCHITECTURE.md` - Agent architecture overview
- `COMPLETE_ARCHITECTURE_FIXES.md` - Architecture details
- `.cursor/skills/` - Cursor IDE skills for Overmind integration