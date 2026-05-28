"""
Cursor Agent SDK API routes (Composer 2.5).

Exposes one-shot prompts and streaming chat backed by the Cursor SDK.
"""
import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from shared.agents.cursor_integration import CursorComposerService
from shared.utils.settings import settings

try:
    from cursor_sdk import CursorAgentError
except ImportError:
    CursorAgentError = Exception  # type: ignore[misc, assignment]

router = APIRouter(prefix="/api/v1/cursor", tags=["cursor-agent"])


class CursorPromptRequest(BaseModel):
    prompt: str = Field(..., description="User prompt for the agent")
    system_prompt: Optional[str] = Field(
        None,
        description="Optional system instructions prepended to the prompt",
    )


class CursorPromptResponse(BaseModel):
    text: str
    run_id: str
    agent_id: str
    status: str
    model: str
    duration_ms: int = 0


class CursorChatRequest(BaseModel):
    message: str = Field(..., description="Chat message")
    system_prompt: Optional[str] = None


def _get_cursor_service(request: Request) -> CursorComposerService:
    service = getattr(request.app.state, "cursor_composer", None)
    if service is None:
        service = CursorComposerService(
            api_key=settings.cursor_api_key,
            model=settings.cursor_model,
            cwd=settings.cursor_agent_cwd,
        )
    return service


@router.get("/status")
async def cursor_status(request: Request) -> Dict[str, Any]:
    """Return Cursor SDK configuration status."""
    service = _get_cursor_service(request)
    return service.status()


@router.get("/models")
async def cursor_models(request: Request) -> Dict[str, Any]:
    """List models available for the configured Cursor API key."""
    service = _get_cursor_service(request)
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cursor SDK not configured. Set CURSOR_API_KEY.",
        )
    models = await service.list_models()
    return {"models": models, "default_model": service.model}


@router.post("/prompt", response_model=CursorPromptResponse)
async def cursor_prompt(
    body: CursorPromptRequest,
    request: Request,
) -> CursorPromptResponse:
    """
    One-shot prompt using Cursor Composer 2.5 (Agent.prompt).

    Suitable for stateless inference from the SIGNAL API.
    """
    service = _get_cursor_service(request)
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cursor SDK not configured. Set CURSOR_API_KEY.",
        )

    try:
        outcome = await _run_prompt_async(service, body.prompt, body.system_prompt)
    except CursorAgentError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": getattr(err, "message", str(err)),
                "retryable": getattr(err, "is_retryable", False),
            },
        ) from err

    return CursorPromptResponse(**outcome)


async def _run_prompt_async(
    service: CursorComposerService,
    prompt: str,
    system_prompt: Optional[str],
) -> Dict[str, Any]:
    import asyncio

    return await asyncio.to_thread(service.prompt_sync, prompt, system_prompt)


@router.post("/chat")
async def cursor_chat_stream(
    body: CursorChatRequest,
    request: Request,
) -> StreamingResponse:
    """
    Streaming chat with Composer 2.5 via Server-Sent Events.

    Event types: started, text, done, error.
    """
    service = _get_cursor_service(request)
    if not service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cursor SDK not configured. Set CURSOR_API_KEY.",
        )

    async def event_generator():
        async for chunk in service.stream_chat(body.message, body.system_prompt):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
