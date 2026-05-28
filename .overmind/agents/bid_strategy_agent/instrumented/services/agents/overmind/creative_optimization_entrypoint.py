"""Overmind harness for CreativeOptimizationAgent (fixed — not optimized)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from services.agents.creative_optimization_agent import CreativeOptimizationAgent
from services.agents.overmind._common import (
    dataclass_to_eval_dict,
    make_cursor_composer,
    parse_json_field,
    run_async,
)

_agent: Optional[CreativeOptimizationAgent] = None


def _get_agent() -> CreativeOptimizationAgent:
    global _agent
    if _agent is None:
        _agent = CreativeOptimizationAgent(cursor_composer=make_cursor_composer())
    return _agent


def run(
    creative_data: str,
    performance_metrics: str,
    benchmark_data: str = "{}",
) -> Dict[str, Any]:
    agent = _get_agent()
    analysis = run_async(
        agent.analyze_creative(
            creative_data=parse_json_field(creative_data),
            performance_metrics=parse_json_field(performance_metrics),
            benchmark_data=parse_json_field(benchmark_data),
        )
    )
    return dataclass_to_eval_dict(analysis)
