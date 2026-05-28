"""Overmind harness for OrchestrationAgent (fixed — not optimized)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from services.agents.orchestration_agent import OrchestrationAgent
from services.agents.overmind._common import (
    make_cursor_composer,
    parse_json_field,
    parse_json_list,
    run_async,
)

_agent: Optional[OrchestrationAgent] = None


def _get_agent() -> OrchestrationAgent:
    global _agent
    if _agent is None:
        _agent = OrchestrationAgent(cursor_composer=make_cursor_composer())
    return _agent


def run(
    auction_context: str,
    campaign_context: str,
    intelligence_data: str,
    performance_history: str = "[]",
) -> Dict[str, Any]:
    agent = _get_agent()
    result = run_async(
        agent.orchestrate_trading_decision(
            auction_context=parse_json_field(auction_context),
            campaign_context=parse_json_field(campaign_context),
            intelligence_data=parse_json_field(intelligence_data),
            performance_history=parse_json_list(performance_history),
        )
    )
    return {
        "final_bid": float(result.get("final_bid", 0)),
        "bid_confidence": float(result.get("bid_confidence", 0)),
        "reasoning": str(result.get("bid_reasoning", ""))[:4000],
        "market_insights_count": int(result.get("market_insights_count", 0)),
        "agents_executed_count": len(result.get("agents_executed", [])),
        "decision_source": str(result.get("decision_source", "")),
        "result_json": str(result)[:4000],
    }
