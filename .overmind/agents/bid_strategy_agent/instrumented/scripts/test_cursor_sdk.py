#!/usr/bin/env python3
"""
Smoke test for Cursor Agent SDK integration.

Requires CURSOR_API_KEY in the environment for live tests.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.agents.cursor_integration import CursorComposerService
from shared.utils.settings import get_settings


async def main() -> None:
    settings = get_settings()
    service = CursorComposerService(
        api_key=settings.cursor_api_key,
        model=settings.cursor_model,
        cwd=settings.cursor_agent_cwd,
    )
    print("Status:", service.status())

    if not service.is_configured:
        print("⚠️  CURSOR_API_KEY not set — skipping live prompt test.")
        return

    print("Running one-shot Composer 2.5 prompt...")
    text = await service.complete(
        user_prompt="Reply with exactly: SIGNAL Cursor SDK OK",
        system_prompt="You are a test harness. Be brief.",
    )
    print("Response:", text[:500])


if __name__ == "__main__":
    asyncio.run(main())
