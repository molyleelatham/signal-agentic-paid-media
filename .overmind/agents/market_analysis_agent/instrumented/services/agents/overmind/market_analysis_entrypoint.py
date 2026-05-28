"""Overmind harness for MarketAnalysisAgent (fixed — not optimized)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from services.agents.market_analysis_agent import MarketAnalysisAgent
from services.agents.overmind._common import (
    insights_to_eval_dict,
    make_cursor_composer,
    parse_json_field,
    parse_json_list,
    run_async,
)

_agent: Optional[MarketAnalysisAgent] = None


def _get_agent() -> MarketAnalysisAgent:
    global _agent
    if _agent is None:
        _agent = MarketAnalysisAgent(cursor_composer=make_cursor_composer())
    return _agent


def run(
    intelligence_data: str,
    campaign_context: str,
    historical_analysis: str = "[]",
) -> Dict[str, Any]:
    agent = _get_agent()
    insights = run_async(
        agent.analyze_market_intelligence(
            intelligence_data=parse_json_field(intelligence_data),
            campaign_context=parse_json_field(campaign_context),
            historical_analysis=parse_json_list(historical_analysis),
        )
    )
    return insights_to_eval_dict(insights)
