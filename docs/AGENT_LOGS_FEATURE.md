# Agent Logs Feature

## Overview

The Agent Logs feature provides real-time visibility into agent decisions during media planning. It displays actions like "BUY Campaign XYZ £5000" in a Bloomberg Terminal-style CLI format.

## Features

### Action Types
- **BUY**: Agent recommends increasing spend on a campaign
- **HOLD**: Agent recommends maintaining current spend
- **STOP**: Agent recommends pausing a campaign
- **OPTIMIZE**: Agent is optimizing parameters
- **MONITOR**: Agent is monitoring metrics

### Log Format
```
HH:MM:SS [AGENT_NAME] ACTION Campaign Name £Amount (Confidence%) → Result
```

### Example Output
```
21:04:19 [THOMPSON_ALLOCATOR] BUY Summer Training Collection Launch £2,500 (85%) → Executing bid
21:04:19 [BID_STRATEGY_AGENT] BUY Performance Training Gear £3,200 (92%) → Executing bid
21:04:19 [ADSTOCK_ENGINE] HOLD TikTok Fitness Challenge (78%) → Maintaining current spend
21:04:19 [BID_STRATEGY_AGENT] STOP Microsoft Search - Gym Essentials (85%) → Campaign paused
```

## Usage

### Test Agent Logs
```bash
make test-agent-logs
```

### Via API
```bash
curl http://localhost:8000/terminal/agent-logs?limit=20
```

### Via Full Dashboard
```bash
curl http://localhost:8000/terminal/full-dashboard
```
The response includes an `agent_logs` field with all recent agent actions.

## Implementation

### Agent Logger Service
**File**: `services/common/agent_logger.py`

The `AgentLogger` class provides methods to log different action types:
- `log_buy()` - Log BUY action with amount and campaign
- `log_hold()` - Log HOLD action with reasoning
- `log_stop()` - Log STOP action with reasoning
- `log_optimize()` - Log OPTIMIZE action
- `log_monitor()` - Log MONITOR action
- `log_analyze()` - Log ANALYZE action
- `log_execute()` - Log EXECUTE action

### Terminal API Integration
**File**: `api/routes/terminal.py`

The `/terminal/agent-logs` endpoint returns agent logs with:
- Timestamp
- Agent name
- Action type (BUY/HOLD/STOP/OPTIMIZE/MONITOR)
- Campaign name
- Channel
- Amount (in £)
- Confidence score
- Result

### Gymshark-Specific Data

The logs use Gymshark's actual campaign names:
- Summer Training Collection Launch
- Performance Training Gear
- TikTok Fitness Challenge
- Microsoft Search - Gym Essentials

And Gymshark's actual channels:
- META, GOOGLE, TIKTOK, MICROSOFT, INSTAGRAM, REDDIT, OOH

## Integration with Media Buying Flow

To integrate with the actual media buying flow, add logging calls in the media buying service:

```python
from services.common import agent_logger

# When Thompson sampling recommends increasing spend
if allocation_increase > 0:
    agent_logger.log_buy(
        agent="THOMPSON_ALLOCATOR",
        campaign=campaign.name,
        amount=allocation_increase,
        channel=channel,
        confidence=0.85
    )

# When adstock detects saturation
if saturation > 0.85:
    agent_logger.log_stop(
        agent="ADSTOCK_ENGINE",
        campaign=campaign.name,
        channel=channel,
        confidence=saturation,
        reasoning=f"Saturation at {saturation:.2f}"
    )
```

## Testing

Run the test script to verify the feature:
```bash
python3 scripts/test_agent_logs.py
```

Or use the Makefile:
```bash
make test-agent-logs
```

## Display in Bloomberg Terminal UI

The agent logs are designed for CLI-style display in the Bloomberg Terminal UI:
- Shows real-time agent activity
- Displays BUY/HOLD/STOP decisions prominently
- Includes campaign names and spend amounts in £
- Shows confidence scores for transparency
- Timestamped for chronological tracking

## Future Enhancements

- Real-time WebSocket streaming of logs
- Filter logs by agent, campaign, or action type
- Log persistence to database
- Log analytics and trends
- Alert system for critical decisions (STOP actions)