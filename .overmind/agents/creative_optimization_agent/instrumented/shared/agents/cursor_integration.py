"""
Cursor Agent SDK integration with Composer 2.5.

Provides a service layer for one-shot prompts and streaming multi-turn agents
using the official cursor-sdk Python package.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

try:
    from cursor_sdk import Agent, AgentOptions, Cursor, CursorAgentError, LocalAgentOptions
    from cursor_sdk import AsyncClient

    CURSOR_SDK_AVAILABLE = True
except ImportError:
    CURSOR_SDK_AVAILABLE = False
    Agent = None  # type: ignore[misc, assignment]
    AgentOptions = None  # type: ignore[misc, assignment]
    Cursor = None  # type: ignore[misc, assignment]
    CursorAgentError = Exception  # type: ignore[misc, assignment]
    LocalAgentOptions = None  # type: ignore[misc, assignment]
    AsyncClient = None  # type: ignore[misc, assignment]

DEFAULT_MODEL = "composer-2.5"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class CursorComposerService:
    """
    Cursor Agent SDK wrapper configured for Composer 2.5 local agents.

    Uses explicit local runtime and setting_sources=[] so service behavior
    does not depend on ambient Cursor IDE settings.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        cwd: Optional[str] = None,
    ):
        self.api_key = (api_key or os.getenv("CURSOR_API_KEY") or "").strip()
        self.model = model or DEFAULT_MODEL
        self.cwd = str(Path(cwd or os.getenv("CURSOR_AGENT_CWD", PROJECT_ROOT)).resolve())

    @property
    def is_configured(self) -> bool:
        return bool(CURSOR_SDK_AVAILABLE and self.api_key)

    def _agent_options(self) -> "AgentOptions":
        return AgentOptions(
            api_key=self.api_key,
            model=self.model,
            local=LocalAgentOptions(
                cwd=self.cwd,
                setting_sources=[],
            ),
        )

    def _build_prompt(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        if system_prompt:
            return f"{system_prompt.strip()}\n\n---\n\n{user_prompt.strip()}"
        return user_prompt.strip()

    def prompt_sync(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        One-shot prompt via Agent.prompt (sync). Disposes the agent automatically.
        """
        if not self.is_configured:
            raise CursorAgentError(
                "Cursor SDK not configured. Set CURSOR_API_KEY.",
                code="missing_api_key",
            )

        message = self._build_prompt(user_prompt, system_prompt)
        try:
            result = Agent.prompt(message, self._agent_options())
        except CursorAgentError:
            raise
        except Exception as exc:
            raise CursorAgentError(str(exc), code="prompt_failed") from exc

        if result.status == "error":
            raise CursorAgentError(
                f"Run failed: {result.id}",
                code="run_error",
            )

        return {
            "text": result.result or "",
            "run_id": result.id,
            "agent_id": result.agent_id,
            "status": result.status,
            "model": self.model,
            "duration_ms": result.duration_ms,
        }

    async def complete(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Async wrapper around prompt_sync for FastAPI and BaseAgent."""
        outcome = await asyncio.to_thread(
            self.prompt_sync,
            user_prompt,
            system_prompt,
        )
        return outcome["text"]

    async def stream_chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream assistant text deltas from a single send() on a local agent.
        Yields dicts: {"type": "text", "text": "..."} or {"type": "done", ...}.
        """
        if not self.is_configured:
            yield {"type": "error", "message": "Cursor SDK not configured"}
            return

        if not system_prompt:
            system_prompt = (
                "You are SIGNAL, an autonomous media trading platform assistant. "
                "Answer concisely with actionable media-buying and marketing insights."
            )
        full_message = self._build_prompt(message, system_prompt)

        try:
            async with await AsyncClient.launch_bridge(workspace=self.cwd) as client:
                async with await client.agents.create(
                    model=self.model,
                    api_key=self.api_key,
                    local=LocalAgentOptions(cwd=self.cwd, setting_sources=[]),
                ) as agent:
                    run = await agent.send(full_message)
                    run_meta = {"run_id": run.id, "agent_id": agent.agent_id, "model": self.model}
                    yield {"type": "started", **run_meta}

                    async for event in run.messages():
                        if event.type == "assistant":
                            for block in event.message.content:
                                if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                                    yield {"type": "text", "text": block.text}

                    result = await run.wait()
                    if result.status == "error":
                        yield {
                            "type": "error",
                            "message": f"Run failed: {result.id}",
                            **run_meta,
                        }
                        return

                    yield {
                        "type": "done",
                        "text": result.result or "",
                        "status": result.status,
                        **run_meta,
                    }
        except CursorAgentError as err:
            yield {
                "type": "error",
                "message": err.message,
                "retryable": getattr(err, "is_retryable", False),
            }
        except Exception as exc:
            yield {"type": "error", "message": str(exc)}

    async def list_models(self) -> List[Dict[str, Any]]:
        """List models available for the configured API key."""
        if not self.is_configured:
            return []

        def _list() -> List[Dict[str, Any]]:
            models = Cursor.models.list(api_key=self.api_key)
            return [
                {
                    "id": getattr(m, "id", None) or m.get("id") if isinstance(m, dict) else str(m),
                    "name": getattr(m, "name", None),
                }
                for m in models
            ]

        try:
            return await asyncio.to_thread(_list)
        except Exception:
            return [{"id": self.model, "name": "Composer 2.5 (configured default)"}]

    def status(self) -> Dict[str, Any]:
        return {
            "sdk_installed": CURSOR_SDK_AVAILABLE,
            "api_key_configured": bool(self.api_key),
            "ready": self.is_configured,
            "model": self.model,
            "cwd": self.cwd,
        }
