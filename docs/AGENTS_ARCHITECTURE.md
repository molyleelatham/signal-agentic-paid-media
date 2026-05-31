# SIGNAL AI Agents Architecture

## Overview

SIGNAL uses a multi-agent AI system with Overmind integration to make intelligent, autonomous media buying decisions while keeping humans in the loop for creative and strategic choices.

## Agent System Design

### Core Philosophy

The agent system implements the **human-in-the-loop autonomous** philosophy from the technical spec:
- **AI agents handle**: Intelligence analysis, bid optimization, creative recommendations
- **Humans handle**: Creative direction, strategic goals, budget allocation, brand decisions
- **Overmind provides**: Continuous optimization through tracing and feedback loops

### Agent Hierarchy

```
OrchestrationAgent (Central Coordinator)
    ├── MarketAnalysisAgent (Intelligence Layer)
    ├── ContentBriefAgent (Creative Strategy)
    ├── BidStrategyAgent (Trading Decisions)
    └── CreativeOptimizationAgent (Performance Optimization)
```

## Individual Agents

### 1. OrchestrationAgent
**Role**: Central coordinator for all agent operations

**Responsibilities**:
- Coordinates execution of specialized agents
- Manages agent priorities and dependencies
- Aggregates agent outputs into unified decisions
- Handles agent failures with fallback mechanisms
- Provides overall system intelligence

**Key Methods**:
- `orchestrate_trading_decision()`: Complete trading decision flow
- `orchestrate_content_generation()`: Multi-topic content brief generation
- `orchestrate_daily_optimization()`: Daily optimization routine

**Overmind Integration**: Traces all orchestration decisions for optimization

### 2. MarketAnalysisAgent
**Role**: Transforms raw intelligence into strategic insights

**Responsibilities**:
- Analyzes Tavily market intelligence
- Identifies strategic opportunities and threats
- Provides competitive intelligence
- Generates actionable market insights
- Predicts future market trends

**Key Methods**:
- `analyze_market_intelligence()`: Generate strategic insights from raw data
- `analyze_competition()`: Competitive landscape analysis
- `predict_market_trends()`: Future trend prediction

**Quality Criteria** (for Overmind):
- Insights are grounded in provided intelligence data
- Opportunities are specific and actionable
- Threat assessment is realistic and prioritized
- Predictions include confidence levels

### 3. ContentBriefAgent
**Role**: Generates creative briefs based on gap analysis

**Responsibilities**:
- Analyzes gap matrix results for opportunities
- Generates creative briefs for high-priority gaps
- Ensures differentiation from competitor angles
- Tailors content to specific platforms and goals
- Evaluates brief quality against criteria

**Key Methods**:
- `generate_brief()`: Generate single creative brief
- `generate_multiple_briefs()`: Generate briefs for multiple topics
- `evaluate_brief_quality()`: Assess brief against quality criteria

**Quality Criteria** (for Overmind):
- Strategic angle is differentiated from competitor angles
- Hook type is appropriate for platform and format
- Proof point is specific and verifiable
- CTA matches intent stage of target audience
- Brief contains enough specificity for execution

### 4. BidStrategyAgent
**Role**: Makes strategic bidding decisions beyond algorithmic calculations

**Responsibilities**:
- Analyzes market conditions and competition
- Makes strategic bid adjustments
- Provides reasoning and risk assessment
- Suggests alternative strategies
- Learns from bid outcomes for improvement

**Key Methods**:
- `decide_bid()`: Make strategic bid decision for auction
- `analyze_bid_outcome()`: Learn from bid results
- `optimize_bidding_strategy()`: Overall strategy optimization

**Quality Criteria** (for Overmind):
- Bid is at or below DMR inflection point
- Cold start mode is correctly identified
- Bid reflects current posterior shrinkage weight
- Reasoning is grounded in market context

### 5. CreativeOptimizationAgent
**Role**: Analyzes and optimizes creative performance

**Responsibilities**:
- Analyzes creative performance beyond simple metrics
- Identifies creative strengths and weaknesses
- Suggests specific optimizations
- Generates creative variations for testing
- Detects creative fatigue and rotation timing

**Key Methods**:
- `analyze_creative()`: Comprehensive creative analysis
- `generate_creative_variations()`: A/B test variations
- `analyze_creative_fatigue()`: Fatigue detection and rotation timing

**Quality Criteria** (for Overmind):
- Analysis considers both creative and performance data
- Suggestions are specific and actionable
- Predicted lift is realistic and grounded
- Fatigue detection uses historical trends

## Overmind Integration

### Tracing Strategy

All agent methods are wrapped with Overmind tracing decorators:

```python
@overmind_tracer.trace(
    name="content_brief_generator",
    tags=["gap_zone", "purchase_intent"],
    quality_criteria=[
        "Strategic angle is differentiated from competitor angles",
        "Hook type is appropriate for platform",
        "Proof point is specific and verifiable",
        "CTA matches intent stage",
        "Brief contains execution specificity"
    ]
)
async def generate_brief(self, gap_topic: Dict, platform: str, goal_type: str) -> ContentBrief:
    # Agent implementation
```

### Ground Truth Feedback Loop

The asymmetric P&L scorer provides ground truth for Overmind optimization:

```python
# After campaign performance is available
overmind_tracer.log_outcome(
    trace_id=trace_id,
    outcome_label="net_pnl",
    outcome_value=pnl_result["net_pnl"]
)
```

### Optimization Cycle

1. **Trace Collection**: Overmind collects traces from all agent decisions
2. **Quality Evaluation**: LLM judge evaluates against quality criteria
3. **Prompt Engineering**: Overmind generates improved prompt variations
4. **A/B Testing**: New prompts tested on holdout traces
5. **Recommendations**: Overmind suggests model swaps, prompt rewrites, control flow changes

## Agent Memory System

### Short-term Memory
- Current context (auction, campaign, intelligence)
- Recent decisions and reasoning
- Temporary calculations

### Long-term Memory
- Historical performance data
- Decision outcomes and learnings
- Market evolution patterns

### Decision History
- Complete audit trail of all agent decisions
- Reasoning and context for each decision
- Performance feedback for learning

## Agent Coordination Patterns

### Sequential Execution
Agents execute in sequence when dependencies exist:
```
Market Analysis → Bid Strategy → Final Decision
```

### Parallel Execution
Independent agents execute in parallel:
```
Market Analysis + Creative Optimization → Orchestration
```

### Fallback Mechanism
If an agent fails, system falls back to algorithmic components:
```
Agent Failure → Algorithmic Fallback → Continue Execution
```

## Integration with Trading Engine

The agent system sits **on top of** the algorithmic trading engine:

```
User Request
    ↓
OrchestrationAgent
    ↓
├── MarketAnalysisAgent (uses Tavily + BERTopic data)
├── Algorithmic Components (LOESS, Bayesian, Thompson)
├── BidStrategyAgent (adjusts algorithmic bid)
└── CreativeOptimizationAgent (suggests improvements)
    ↓
Final Decision (Agent-informed, algorithmically grounded)
```

## Example Trading Decision Flow

```python
# 1. Auction event received
auction_context = {
    "platform": "thrad",
    "competition_level": "high",
    "base_bid": 1.50
}

# 2. Orchestrate decision
decision = await orchestration_agent.orchestrate_trading_decision(
    auction_context=auction_context,
    campaign_context=campaign_context,
    intelligence_data=market_intelligence,
    performance_history=performance_data
)

# 3. Decision includes:
# - Market insights from MarketAnalysisAgent
# - Strategic bid adjustment from BidStrategyAgent
# - Creative suggestions from CreativeOptimizationAgent
# - Final bid with reasoning and confidence
```

## Token Economy Integration

Agents contribute to the attention token economy:

- **Performance-based rewards**: Agent decisions that lead to positive P&L generate token rewards
- **Quality scoring**: Agent output quality affects token multipliers
- **Leaderboard rankings**: Agent performance contributes to user rankings
- **Staking decisions**: Agents can inform staking strategies on campaign approaches

## Technical Excellence Features

### Open-Source Models
- Local Thrad DistilBERT for intent classification
- BERTopic for topic modeling
- Sentence transformers for embeddings

### Auditable Decisions
- Complete trace of all agent decisions
- Reasoning recorded for every decision
- Context preserved for audit trails

### Error Handling
- Graceful fallbacks for agent failures
- Algorithmic safety nets
- Comprehensive logging

### Performance Optimization
- Async execution for parallel agent operations
- Caching for frequently used data
- Efficient memory management

## Future Enhancements

1. **Multi-Model Support**: Integrate multiple LLM providers (Anthropic, OpenAI, etc.)
2. **Agent Learning**: Reinforcement learning for agent improvement
3. **Real-time Adaptation**: Dynamic agent behavior based on market conditions
4. **Collaborative Agents**: Multi-agent debate and consensus building
5. **Explainable AI**: Enhanced decision explanation capabilities

## Conclusion

The SIGNAL agent system provides intelligent, autonomous decision-making while maintaining human oversight. Through Overmind integration, the system continuously improves based on real-world performance, creating a self-optimizing platform that gets smarter with every decision.