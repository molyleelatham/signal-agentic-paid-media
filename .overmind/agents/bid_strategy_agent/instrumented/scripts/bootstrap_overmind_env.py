#!/usr/bin/env python3
"""Sync API keys from .env.local into .overmind/.env (no secret output)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".env.local"
TARGET = ROOT / ".overmind" / ".env"

SYNC_KEYS = [
    "OVERMIND_API_KEY",
    "OVERMIND_PROJECT_ID",
    "CURSOR_API_KEY",
    "CURSOR_MODEL",
    "OPENAI_API_KEY",
]


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
    return not bool(re.fullmatch(r"your[-_]?key[-_]?here|changeme|xxx+", v, re.I))


def main() -> None:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    local = parse_env(LOCAL)
    current = parse_env(TARGET) if TARGET.is_file() else {}

    merged = dict(current)
    for key in SYNC_KEYS:
        if key in local and key_ok(local[key]):
            merged[key] = local[key]

    if not merged.get("ANALYZER_MODEL"):
        merged["ANALYZER_MODEL"] = "openai/gpt-4o-mini"
    if not merged.get("SYNTHETIC_DATAGEN_MODEL"):
        merged["SYNTHETIC_DATAGEN_MODEL"] = merged["ANALYZER_MODEL"]

    lines = ["# Overmind environment (synced from .env.local where present)\n"]
    for key in sorted(merged):
        lines.append(f"{key}={merged[key]}\n")

    TARGET.write_text("".join(lines))
    print(f"Wrote {TARGET}")
    print("configured:", [k for k in ["OVERMIND_API_KEY", "CURSOR_API_KEY", "OPENAI_API_KEY"] if key_ok(merged.get(k, ""))])
    print("missing:", [k for k in ["OVERMIND_API_KEY", "CURSOR_API_KEY", "OPENAI_API_KEY"] if not key_ok(merged.get(k, ""))])


if __name__ == "__main__":
    main()
