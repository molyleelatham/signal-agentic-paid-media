#!/usr/bin/env python3
"""
Sync API keys from .env.local into .overmind/.env (no secret output).

Architecture:
  - CURSOR_API_KEY + CURSOR_MODEL  → agent harness / Composer 2.5 (agent under test)
  - OPENAI_API_KEY + ANALYZER_*      → Overmind setup, optimize, synthetic datagen
  - OVERMIND_API_KEY                 → Overmind platform tracing
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".env.local"
TARGET = ROOT / ".overmind" / ".env"

# Keys synced from .env.local when present and non-placeholder
SYNC_KEYS = [
    "OVERMIND_API_KEY",
    "OVERMIND_PROJECT_ID",
    "CURSOR_API_KEY",
    "CURSOR_MODEL",
    "OPENAI_API_KEY",
]

# Overmind analyzer / datagen defaults (OpenAI — not Composer)
OVERMIND_LLM_DEFAULTS = {
    "ANALYZER_MODEL": "gpt-4o-mini",
    "SYNTHETIC_DATAGEN_MODEL": "gpt-4o-mini",
    "DEFAULT_LLM_PROVIDER": "openai",
    "OVERMIND_ENVIRONMENT": "development",
    "OVERMIND_SERVICE_NAME": "signal-platform",
}

AGENT_LLM_DEFAULTS = {
    "CURSOR_MODEL": "composer-2.5",
}


def parse_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def key_ok(value: str) -> bool:
    v = (value or "").strip()
    if not v or v == "<set-me>":
        return False
    if "your_" in v.lower() or "_here" in v.lower():
        return False
    return not bool(
        re.fullmatch(
            r"your[-_]?key[-_]?here|your[-_]?openai[-_]?api[-_]?key[-_]?here|changeme|xxx+",
            v,
            re.I,
        )
    )


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    local = parse_env(LOCAL)
    current = parse_env(TARGET) if TARGET.is_file() else {}

    merged = {**OVERMIND_LLM_DEFAULTS, **AGENT_LLM_DEFAULTS, **current}
    for key in SYNC_KEYS:
        if key in local and key_ok(local[key]):
            merged[key] = local[key]

    for key, default in OVERMIND_LLM_DEFAULTS.items():
        if not merged.get(key):
            merged[key] = default
    if not merged.get("SYNTHETIC_DATAGEN_MODEL"):
        merged["SYNTHETIC_DATAGEN_MODEL"] = merged["ANALYZER_MODEL"]
    if not merged.get("CURSOR_MODEL"):
        merged["CURSOR_MODEL"] = AGENT_LLM_DEFAULTS["CURSOR_MODEL"]

    header = """# Overmind project environment
# Agent evals: CURSOR_API_KEY + composer-2.5 (Cursor SDK)
# Overmind analyzer/setup: OPENAI_API_KEY + ANALYZER_MODEL
# See docs/LLM_ARCHITECTURE.md

"""
    lines = [header]
    order = [
        "OVERMIND_API_KEY",
        "OVERMIND_PROJECT_ID",
        "OVERMIND_ENVIRONMENT",
        "OVERMIND_SERVICE_NAME",
        "OPENAI_API_KEY",
        "ANALYZER_MODEL",
        "SYNTHETIC_DATAGEN_MODEL",
        "DEFAULT_LLM_PROVIDER",
        "CURSOR_API_KEY",
        "CURSOR_MODEL",
    ]
    written = set()
    for key in order:
        if key in merged:
            lines.append(f"{key}={merged[key]}\n")
            written.add(key)
    for key in sorted(merged):
        if key not in written:
            lines.append(f"{key}={merged[key]}\n")

    TARGET.write_text("".join(lines))
    print(f"Wrote {TARGET}")
    print("agent (Cursor):", "ready" if key_ok(merged.get("CURSOR_API_KEY", "")) else "CURSOR_API_KEY missing")
    print(
        "overmind generative (OpenAI):",
        "ready" if key_ok(merged.get("OPENAI_API_KEY", "")) else "OPENAI_API_KEY missing",
    )
    print("overmind platform:", "ready" if key_ok(merged.get("OVERMIND_API_KEY", "")) else "OVERMIND_API_KEY missing")


if __name__ == "__main__":
    main()
