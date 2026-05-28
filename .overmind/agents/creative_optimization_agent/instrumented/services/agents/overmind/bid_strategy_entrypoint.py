"""Overmind harness for BidStrategyAgent (fixed — not optimized)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.agents.bid_strategy_agent import BidStrategyAgent
from services.agents.overmind._common import (
    dataclass_to_eval_dict,
    make_cursor_composer,
    parse_json_field,
    parse_json_list,
    run_async,
)

_agent: Optional[BidStrategyAgent] = None


def _get_agent() -> BidStrategyAgent:
    global _agent
    if _agent is None:
        _agent = BidStrategyAgent(cursor_composer=make_cursor_composer())
    return _agent


def run(
    auction_context: str,
    algorithmic_bid: float,
    campaign_context: str,
    performance_history: str = "[]",
) -> Dict[str, Any]:
    agent = _get_agent()
    decision = run_async(
        agent.decide_bid(
            auction_context=parse_json_field(auction_context),
            algorithmic_bid=float(algorithmic_bid),
            campaign_context=parse_json_field(campaign_context),
            performance_history=parse_json_list(performance_history),
        )
    )
    return dataclass_to_eval_dict(decision)
