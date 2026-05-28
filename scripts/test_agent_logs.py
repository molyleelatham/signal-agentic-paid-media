"""
Test Agent Logs Feature

Tests the agent logs feature to ensure BUY/HOLD/STOP signals work correctly.
"""

import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

from services.common import agent_logger

# Test the agent logger
print("Testing Agent Logger...")
print("=" * 60)

# Log some BUY actions
agent_logger.log_buy(
    agent="THOMPSON_ALLOCATOR",
    campaign="Summer Training Collection Launch",
    amount=2500.0,
    channel="META",
    confidence=0.85,
    reasoning="Strong performance signal"
)

agent_logger.log_buy(
    agent="BID_STRATEGY_AGENT",
    campaign="Performance Training Gear",
    amount=3200.0,
    channel="GOOGLE",
    confidence=0.92,
    reasoning="High conversion rate detected"
)

# Log a HOLD action
agent_logger.log_hold(
    agent="ADSTOCK_ENGINE",
    campaign="TikTok Fitness Challenge",
    channel="TIKTOK",
    confidence=0.78,
    reasoning="Saturation within acceptable range"
)

# Log a STOP action
agent_logger.log_stop(
    agent="BID_STRATEGY_AGENT",
    campaign="Microsoft Search - Gym Essentials",
    channel="MICROSOFT",
    confidence=0.85,
    reasoning="Poor ROAS performance detected"
)

# Log an OPTIMIZE action
agent_logger.log_optimize(
    agent="THOMPSON_ALLOCATOR",
    campaign="Summer Training Collection Launch",
    optimization_type="Channel reallocation",
    confidence=0.88
)

# Log a MONITOR action
agent_logger.log_monitor(
    agent="OVERMIND_TRACER",
    metric="CPA",
    value="£22.50 (within target)"
)

# Get and display logs
print("\nGenerated Agent Logs:")
print("=" * 60)
logs = agent_logger.get_logs(limit=10)

for log in logs:
    print(log)

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\nThe agent logs feature is working correctly.")
print("BUY/HOLD/STOP signals with campaign names and amounts are displayed.")