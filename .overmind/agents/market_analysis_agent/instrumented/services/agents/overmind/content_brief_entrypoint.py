"""Overmind harness for ContentBriefAgent (fixed — not optimized)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.agents.content_brief_agent import ContentBriefAgent
from services.agents.overmind._common import (
    dataclass_to_eval_dict,
    make_cursor_composer,
    parse_json_field,
    parse_json_list,
    run_async,
)

_agent: Optional[ContentBriefAgent] = None


def _get_agent() -> ContentBriefAgent:
    global _agent
    if _agent is None:
        _agent = ContentBriefAgent(cursor_composer=make_cursor_composer())
    return _agent


def run(
    gap_topic: str,
    platform: str,
    goal_type: str,
    competitor_angles: str = "[]",
) -> Dict[str, Any]:
    agent = _get_agent()
    brief = run_async(
        agent.generate_brief(
            gap_topic=parse_json_field(gap_topic),
            platform=platform,
            goal_type=goal_type,
            competitor_angles=parse_json_list(competitor_angles) or None,
        )
    )
    return dataclass_to_eval_dict(brief)
