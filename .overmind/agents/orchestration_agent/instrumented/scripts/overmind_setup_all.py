#!/usr/bin/env python3
"""Run overmind setup --fast for all registered agents."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AGENTS = [
    "bid_strategy_agent",
    "content_brief_agent",
    "creative_optimization_agent",
    "market_analysis_agent",
    "orchestration_agent",
]

POLICY_MAP = {
    "bid_strategy_agent": "policies/bid_strategy_agent.md",
    "content_brief_agent": "policies/content_brief_agent.md",
    "creative_optimization_agent": "policies/creative_optimization_agent.md",
    "market_analysis_agent": "policies/market_analysis_agent.md",
    "orchestration_agent": "policies/orchestration_agent.md",
}


def main() -> None:
    for name in AGENTS:
        policy = ROOT / POLICY_MAP[name]
        cmd = [
            "overmind",
            "setup",
            name,
            "--fast",
            "--policy",
            str(policy),
            "--scope",
            "services/agents/**/*.py",
            "--scope",
            "shared/agents/**/*.py",
        ]
        print("$", " ".join(cmd))
        subprocess.run(cmd, cwd=ROOT, check=False)


if __name__ == "__main__":
    main()
