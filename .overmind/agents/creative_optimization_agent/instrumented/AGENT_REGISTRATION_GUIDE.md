# Overmind Agent Registration Implementation Guide

## Overview

This guide provides step-by-step instructions for registering SIGNAL platform agents with Overmind using Cursor IDE skills.

## Prerequisites

### 1. Overmind Configuration

Ensure Overmind is configured:
```bash
make overmind-setup
```

This creates `.overmind/.env` with your API keys.

### 2. Set API Keys

Edit `.overmind/.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
OVERMIND_API_KEY=om-your-overmind-key-here
OVERMIND_PROJECT_ID=proj-your-project-id-here
```

### 3. Verify Agent Readiness

Run the test script to verify agents are ready:
```bash
python3 scripts/test_agent_registration.py
```

Expected output:
- ✅ All agent files exist
- ✅ All policy files exist
- ✅ All agents have BaseAgent, OvermindTracer, CursorComposerService
- ⚠️  API keys may not be set (that's OK for testing)

## Registration Process

### Step 1: Open Cursor IDE

Open your project in Cursor IDE.

### Step 2: Open Command Palette

Press `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux) to open the command palette.

### Step 3: Register Each Agent

Run the following commands in the command palette, one at a time:

#### 1. Bid Strategy Agent
```
/overmind-register-agent services/agents/bid_strategy_agent.py
```
Then optimize:
```
/overmind-optimize-agent bid_strategy_agent
```

#### 2. Content Brief Agent
```
/overmind-register-agent services/agents/content_brief_agent.py
```
Then optimize:
```
/overmind-optimize-agent content_brief_agent
```

#### 3. Creative Optimization Agent
```
/overmind-register-agent services/agents/creative_optimization_agent.py
```
Then optimize:
```
/overmind-optimize-agent creative_optimization_agent
```

#### 4. Market Analysis Agent
```
/overmind-register-agent services/agents/market_analysis_agent.py
```
Then optimize:
```
/overmind-optimize-agent market_analysis_agent
```

#### 5. Orchestration Agent
```
/overmind-register-agent services/agents/orchestration_agent.py
```
Then optimize:
```
/overmind-optimize-agent orchestration_agent
```

### Step 4: Verify Registration

Visit https://platform.overmind.ai to verify:
- All 5 agents are registered
- Each agent has its policy file linked
- Optimization metrics are visible

## Agent Policies

Each agent has a comprehensive policy file in `policies/`:

| Agent | Policy File | Purpose |
|-------|-------------|---------|
| bid_strategy_agent | policies/bid_strategy_agent.md | Strategic bidding decisions |
| content_brief_agent | policies/content_brief_agent.md | Creative brief generation |
| creative_optimization_agent | policies/creative_optimization_agent.md | Creative performance optimization |
| market_analysis_agent | policies/market_analysis_agent.md | Market intelligence analysis |
| orchestration_agent | policies/orchestration_agent.md | Agent coordination |

## What Happens During Registration

### /overmind-register-agent

1. **Analyzes Agent File**: Reads the Python agent file
2. **Extracts Metadata**: Identifies class name, methods, dependencies
3. **Links Policy**: Associates the policy MD file with the agent
4. **Creates Agent Entry**: Registers agent in Overmind platform
5. **Sets Up Tracing**: Configures automatic LLM call tracing

### /overmind-optimize-agent

1. **Analyzes Performance**: Reviews past executions (if available)
2. **Generates Datasets**: Creates test datasets for evaluation
3. **Quality Evaluation**: Evaluates agent against quality criteria
4. **Optimization Suggestions**: Provides improvement recommendations
5. **Fine-tuning**: Suggests prompt or parameter adjustments

## Troubleshooting

### Issue: "Overmind API key not found"

**Solution**: 
1. Check `.overmind/.env` exists
2. Verify `OVERMIND_API_KEY` is set
3. Restart Cursor IDE after setting keys

### Issue: "Agent file not found"

**Solution**:
1. Verify you're in the project root directory
2. Check the file path is correct
3. Run `python3 scripts/test_agent_registration.py` to verify

### Issue: "Policy file not linked"

**Solution**:
1. Ensure policy file exists in `policies/` directory
2. Check policy file has required sections
3. Re-register the agent

### Issue: "OpenAI API key required"

**Solution**:
1. Set `OPENAI_API_KEY` in `.overmind/.env`
2. Ensure you have credits on your OpenAI account
3. The key is used for LLM tracing and optimization

## Expected Registration Output

Each registration should show:
- ✅ Agent analyzed successfully
- ✅ Policy linked
- ✅ Agent registered with Overmind
- ✅ Tracing configured

Each optimization should show:
- ✅ Performance analysis complete
- ✅ Dataset generated
- ✅ Quality evaluation complete
- ✅ Optimization suggestions available

## Post-Registration

### 1. Monitor Agent Performance

After registration, agents will automatically:
- Trace all LLM calls
- Log execution metrics
- Capture quality scores
- Track token usage

View at: https://platform.overmind.ai

### 2. Review Optimization Suggestions

Overmind will provide:
- Prompt improvements
- Parameter tuning suggestions
- Performance benchmarks
- Quality criteria feedback

### 3. Continuous Improvement

As agents run:
- Collect execution data
- Identify optimization opportunities
- Suggest policy updates
- Track improvement over time

## Quick Reference

### View Registration Commands
```bash
make register-agents
```

### Test Agent Readiness
```bash
python3 scripts/test_agent_registration.py
```

### View Policy Documentation
```bash
cat policies/README.md
```

### View Individual Policies
```bash
cat policies/bid_strategy_agent.md
cat policies/content_brief_agent.md
cat policies/creative_optimization_agent.md
cat policies/market_analysis_agent.md
cat policies/orchestration_agent.md
```

## Support

- **Overmind Documentation**: https://docs.overmind.ai
- **Cursor Skills**: `.cursor/skills/` directory
- **Local Development**: `LOCAL_DEVELOPMENT.md`
- **Agent Policies**: `policies/README.md`

## Summary

1. ✅ All 5 agents have policy files created
2. ✅ All agents are properly structured with BaseAgent, OvermindTracer, CursorComposerService
3. ✅ Registration script provides commands for Cursor IDE
4. ✅ Test script verifies agent readiness
5. ⏳ Registration must be done in Cursor IDE (cannot be automated)
6. ⏳ Requires valid API keys to complete

**Next Action**: Open Cursor IDE and run the registration commands shown above.