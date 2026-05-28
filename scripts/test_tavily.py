#!/usr/bin/env python3
"""Smoke test for Tavily integration (SIGNAL TavilyClient + MarketScanner)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.utils.settings import get_settings


async def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    if not settings.tavily_api_key:
        print("❌ TAVILY_API_KEY is not set in .env.local or environment")
        print("   Add: TAVILY_API_KEY=tvly-... to .env.local")
        print("   Get a key at: https://tavily.com")
        return 1

    from services.intelligence.tavily_client import TavilyClient, MarketScanner

    print("Testing Tavily search_and_answer...")
    client = TavilyClient()
    try:
        result = await client.search_and_answer(
            query="sustainable activewear market trends 2026",
            max_results=3,
            search_depth="basic",
        )
        print(f"✅ Search OK — query: {result.query!r}")
        print(f"   Answer preview: {(result.answer or '')[:200]}...")
        print(f"   Results: {len(result.results)}")
        for i, r in enumerate(result.results[:3], 1):
            print(f"   [{i}] {r.title[:60]} — score={r.score:.2f}")

        print("\nTesting MarketScanner.scan_market...")
        scanner = MarketScanner(client)
        scan = await scanner.scan_market(
            category="sustainable fashion",
            competitors=["Gymshark"],
            scan_depth="basic",
        )
        print(f"✅ Market scan OK — keys: {list(scan.keys())}")
        return 0
    except Exception as exc:
        print(f"❌ Tavily request failed: {exc}")
        return 1
    finally:
        await client.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
