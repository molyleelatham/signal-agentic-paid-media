#!/usr/bin/env python3
"""Register all SIGNAL agents with Overmind and create validate stubs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AGENTS = [
    {
        "name": "bid_strategy_agent",
        "entrypoint": "services.agents.overmind.bid_strategy_entrypoint:run",
        "stub": {
            "input": {
                "auction_context": json.dumps(
                    {"platform": "meta", "competition_level": "medium", "audience": "fitness"}
                ),
                "algorithmic_bid": 2.5,
                "campaign_context": json.dumps(
                    {"campaign_id": "camp_001", "target_cpa": 25.0, "goal": "conversions"}
                ),
                "performance_history": "[]",
            }
        },
    },
    {
        "name": "content_brief_agent",
        "entrypoint": "services.agents.overmind.content_brief_entrypoint:run",
        "stub": {
            "input": {
                "gap_topic": json.dumps(
                    {"topic": "sustainable activewear", "priority": "high", "volume": 1200}
                ),
                "platform": "meta",
                "goal_type": "lead_generation",
                "competitor_angles": json.dumps(["eco-friendly", "performance"]),
            }
        },
    },
    {
        "name": "creative_optimization_agent",
        "entrypoint": "services.agents.overmind.creative_optimization_entrypoint:run",
        "stub": {
            "input": {
                "creative_data": json.dumps(
                    {"creative_id": "cr_001", "headline": "Train harder", "format": "video"}
                ),
                "performance_metrics": json.dumps({"ctr": 0.04, "cvr": 0.02, "spend": 500}),
                "benchmark_data": json.dumps({"ctr": 0.03, "cvr": 0.015}),
            }
        },
    },
    {
        "name": "market_analysis_agent",
        "entrypoint": "services.agents.overmind.market_analysis_entrypoint:run",
        "stub": {
            "input": {
                "intelligence_data": json.dumps(
                    {"trends": ["sustainable fashion"], "competitors": ["brand_a"]}
                ),
                "campaign_context": json.dumps({"client": "gymshark", "goal": "growth"}),
                "historical_analysis": "[]",
            }
        },
    },
    {
        "name": "orchestration_agent",
        "entrypoint": "services.agents.overmind.orchestration_entrypoint:run",
        "stub": {
            "input": {
                "auction_context": json.dumps({"platform": "google", "competition_level": "low"}),
                "campaign_context": json.dumps({"campaign_id": "camp_002", "budget": 10000}),
                "intelligence_data": json.dumps({"signals": ["rising demand"]}),
                "performance_history": "[]",
            }
        },
    },
]


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    stubs_dir = ROOT / ".overmind" / "_validate_stubs"
    stubs_dir.mkdir(parents=True, exist_ok=True)

    for agent in AGENTS:
        name = agent["name"]
        stub_path = stubs_dir / f"{name}.json"
        stub_path.write_text(json.dumps(agent["stub"], indent=2))

        run(
            [
                "overmind",
                "agent",
                "register",
                "--non-interactive",
                name,
                agent["entrypoint"],
            ]
        )
        run(["overmind", "agent", "validate", name, "--data", str(stub_path)])

    print("All agents registered and validated.")


if __name__ == "__main__":
    main()
