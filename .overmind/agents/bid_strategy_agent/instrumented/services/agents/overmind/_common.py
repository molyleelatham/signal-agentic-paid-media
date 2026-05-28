"""Shared helpers for Overmind evaluation harnesses."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar

from shared.agents.cursor_integration import CursorComposerService
from shared.utils.settings import get_settings

T = TypeVar("T")


def parse_json_field(value: Any, default: Optional[Any] = None) -> Any:
    if value is None or value == "":
        return default if default is not None else {}
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default if default is not None else {}
    return value


def parse_json_list(value: Any) -> List[Dict]:
    parsed = parse_json_field(value, [])
    return parsed if isinstance(parsed, list) else []


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def make_cursor_composer() -> CursorComposerService:
    settings = get_settings()
    return CursorComposerService(
        api_key=settings.cursor_api_key,
        model=settings.cursor_model,
        cwd=settings.cursor_agent_cwd,
    )


def dataclass_to_eval_dict(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        raw = {k: getattr(obj, k) for k in obj.__dataclass_fields__}
    elif isinstance(obj, dict):
        raw = obj
    else:
        return {"result_text": str(obj)}

    out: Dict[str, Any] = {}
    for key, value in raw.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value if value is not None else ""
        elif isinstance(value, list):
            out[f"{key}_count"] = len(value)
            out[f"{key}_json"] = json.dumps(value)[:4000]
        elif isinstance(value, dict):
            out[f"{key}_json"] = json.dumps(value)[:4000]
        else:
            out[f"{key}_text"] = str(value)[:4000]
    return out


def insights_to_eval_dict(insights: List[Any]) -> Dict[str, Any]:
    summaries = []
    for item in insights:
        if hasattr(item, "summary"):
            summaries.append(str(item.summary))
        elif isinstance(item, dict):
            summaries.append(str(item.get("summary", item)))
        else:
            summaries.append(str(item))
    return {
        "insight_count": len(insights),
        "insights_summary": " | ".join(summaries)[:4000] if summaries else "",
        "has_actionable_insights": bool(summaries),
        "insights_json": json.dumps(
            [dataclass_to_eval_dict(i) for i in insights],
            default=str,
        )[:4000],
    }
