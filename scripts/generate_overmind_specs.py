#!/usr/bin/env python3
"""Generate minimal Overmind eval_spec + dataset for all SIGNAL agents."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

READ_ONLY = [
    "services/agents/overmind/**/*.py",
    "services/agents/overmind/_common.py",
]

OPTIMIZABLE = [
    "services/agents/bid_strategy_agent.py",
    "services/agents/content_brief_agent.py",
    "services/agents/creative_optimization_agent.py",
    "services/agents/market_analysis_agent.py",
    "services/agents/orchestration_agent.py",
    "shared/agents/overmind_integration.py",
    "shared/agents/cursor_integration.py",
]

AGENT_SPECS = {
    "bid_strategy_agent": {
        "description": "Strategic media bidding decisions for SIGNAL auctions.",
        "input_schema": {
            "auction_context": {"type": "text", "description": "JSON auction context"},
            "algorithmic_bid": {"type": "number", "description": "Algorithmic bid suggestion"},
            "campaign_context": {"type": "text", "description": "JSON campaign context"},
            "performance_history": {"type": "text", "description": "JSON performance history list"},
        },
        "output_fields": {
            "recommended_bid": {"type": "number", "weight": 35, "description": "Final bid amount"},
            "confidence": {"type": "number", "weight": 25, "description": "Decision confidence 0-1"},
            "reasoning": {"type": "text", "weight": 25, "description": "Strategic reasoning"},
            "risk_assessment": {"type": "text", "weight": 15, "description": "Risk summary"},
        },
        "sample_input": {
            "auction_context": '{"platform": "meta", "competition_level": "medium"}',
            "algorithmic_bid": 2.5,
            "campaign_context": '{"campaign_id": "camp_001", "target_cpa": 25}',
            "performance_history": "[]",
        },
        "sample_output": {
            "recommended_bid": 2.5,
            "confidence": 0.8,
            "reasoning": "Maintain algorithmic bid under medium competition.",
            "risk_assessment": "Medium competition; efficiency-focused bid.",
        },
    },
    "content_brief_agent": {
        "description": "Generate creative content briefs from gap analysis.",
        "input_schema": {
            "gap_topic": {"type": "text", "description": "JSON gap topic"},
            "platform": {"type": "text", "description": "Target platform"},
            "goal_type": {"type": "text", "description": "Campaign goal"},
            "competitor_angles": {"type": "text", "description": "JSON competitor angles"},
        },
        "output_fields": {
            "topic": {"type": "text", "weight": 15, "description": "Brief topic"},
            "angle": {"type": "text", "weight": 30, "description": "Creative angle"},
            "hook": {"type": "text", "weight": 25, "description": "Hook copy"},
            "cta": {"type": "text", "weight": 15, "description": "Call to action"},
            "confidence": {"type": "number", "weight": 15, "description": "Brief confidence"},
        },
        "sample_input": {
            "gap_topic": '{"topic": "sustainable activewear", "priority": "high"}',
            "platform": "meta",
            "goal_type": "lead_generation",
            "competitor_angles": '["eco-friendly"]',
        },
        "sample_output": {
            "topic": "sustainable activewear",
            "angle": "Performance meets sustainability",
            "hook": "Train harder, waste less",
            "cta": "Shop the sustainable collection",
            "confidence": 0.85,
        },
    },
    "creative_optimization_agent": {
        "description": "Analyze creative performance and suggest optimizations.",
        "input_schema": {
            "creative_data": {"type": "text", "description": "JSON creative metadata"},
            "performance_metrics": {"type": "text", "description": "JSON performance metrics"},
            "benchmark_data": {"type": "text", "description": "JSON benchmark data"},
        },
        "output_fields": {
            "performance_score": {"type": "number", "weight": 35, "description": "Overall score"},
            "confidence": {"type": "number", "weight": 25, "description": "Analysis confidence"},
            "optimization_suggestions_count": {
                "type": "number",
                "weight": 20,
                "description": "Count of suggestions",
            },
            "predicted_lift": {"type": "number", "weight": 20, "description": "Predicted lift"},
        },
        "sample_input": {
            "creative_data": '{"creative_id": "cr_001", "headline": "Train harder"}',
            "performance_metrics": '{"ctr": 0.04, "cvr": 0.02}',
            "benchmark_data": '{"ctr": 0.03}',
        },
        "sample_output": {
            "performance_score": 0.75,
            "confidence": 0.8,
            "optimization_suggestions_count": 2,
            "predicted_lift": 0.12,
        },
    },
    "market_analysis_agent": {
        "description": "Transform intelligence into strategic market insights.",
        "input_schema": {
            "intelligence_data": {"type": "text", "description": "JSON intelligence payload"},
            "campaign_context": {"type": "text", "description": "JSON campaign context"},
            "historical_analysis": {"type": "text", "description": "JSON historical analyses"},
        },
        "output_fields": {
            "insight_count": {"type": "number", "weight": 20, "description": "Number of insights"},
            "insights_summary": {"type": "text", "weight": 40, "description": "Summary text"},
            "has_actionable_insights": {
                "type": "boolean",
                "weight": 40,
                "description": "Whether insights are actionable",
            },
        },
        "sample_input": {
            "intelligence_data": '{"trends": ["sustainable fashion"]}',
            "campaign_context": '{"client": "gymshark"}',
            "historical_analysis": "[]",
        },
        "sample_output": {
            "insight_count": 2,
            "insights_summary": "Sustainable fashion momentum with competitor pressure.",
            "has_actionable_insights": True,
        },
    },
    "orchestration_agent": {
        "description": "Coordinate specialized agents for unified trading decisions.",
        "input_schema": {
            "auction_context": {"type": "text", "description": "JSON auction context"},
            "campaign_context": {"type": "text", "description": "JSON campaign context"},
            "intelligence_data": {"type": "text", "description": "JSON intelligence data"},
            "performance_history": {"type": "text", "description": "JSON performance history"},
        },
        "output_fields": {
            "final_bid": {"type": "number", "weight": 35, "description": "Final orchestrated bid"},
            "bid_confidence": {"type": "number", "weight": 25, "description": "Bid confidence"},
            "reasoning": {"type": "text", "weight": 25, "description": "Orchestration reasoning"},
            "market_insights_count": {
                "type": "number",
                "weight": 15,
                "description": "Insights used",
            },
        },
        "sample_input": {
            "auction_context": '{"platform": "google", "competition_level": "low"}',
            "campaign_context": '{"campaign_id": "camp_002", "budget": 10000}',
            "intelligence_data": '{"signals": ["rising demand"]}',
            "performance_history": "[]",
        },
        "sample_output": {
            "final_bid": 1.0,
            "bid_confidence": 0.82,
            "reasoning": "Low competition supports modest bid increase.",
            "market_insights_count": 1,
        },
    },
}


def build_eval_spec(agent_name: str, spec: dict) -> dict:
    policy_path = ROOT / "policies" / f"{agent_name}.md"
    policy_text = policy_path.read_text() if policy_path.is_file() else ""
    optimizable = OPTIMIZABLE.copy()
    if agent_name == "bid_strategy_agent":
        optimizable = ["services/agents/bid_strategy_agent.py", "shared/agents/overmind_integration.py"]
    elif agent_name == "content_brief_agent":
        optimizable = ["services/agents/content_brief_agent.py", "shared/agents/overmind_integration.py"]
    elif agent_name == "creative_optimization_agent":
        optimizable = [
            "services/agents/creative_optimization_agent.py",
            "shared/agents/overmind_integration.py",
        ]
    elif agent_name == "market_analysis_agent":
        optimizable = ["services/agents/market_analysis_agent.py", "shared/agents/overmind_integration.py"]
    elif agent_name == "orchestration_agent":
        optimizable = [
            "services/agents/orchestration_agent.py",
            "services/agents/bid_strategy_agent.py",
            "services/agents/market_analysis_agent.py",
            "shared/agents/overmind_integration.py",
        ]

    entrypoint_map = {
        "bid_strategy_agent": "services/agents/overmind/bid_strategy_entrypoint.py",
        "content_brief_agent": "services/agents/overmind/content_brief_entrypoint.py",
        "creative_optimization_agent": "services/agents/overmind/creative_optimization_entrypoint.py",
        "market_analysis_agent": "services/agents/overmind/market_analysis_entrypoint.py",
        "orchestration_agent": "services/agents/overmind/orchestration_entrypoint.py",
    }
    output_fields = {}
    for field, meta in spec["output_fields"].items():
        output_fields[field] = {
            **meta,
            "importance": "critical" if meta["weight"] >= 30 else "important",
            "eval_mode": "similarity" if meta["type"] == "text" else None,
            "optional": False,
        }
        if output_fields[field]["eval_mode"] is None:
            del output_fields[field]["eval_mode"]

    return {
        "agent_name": agent_name,
        "agent_description": spec["description"],
        "agent_path": str(ROOT / entrypoint_map[agent_name]),
        "entrypoint_fn": "run",
        "input_schema": spec["input_schema"],
        "output_fields": output_fields,
        "consistency_rules": [],
        "structure_weight": 20,
        "tool_usage_weight": 0,
        "llm_judge_weight": 10,
        "total_points": 100,
        "scope": {
            "optimizable_paths": optimizable,
            "read_only_paths": READ_ONLY + [entrypoint_map[agent_name]],
        },
        "policy_markdown": policy_text,
    }


def build_dataset(spec: dict) -> dict:
    cases = []
    for i in range(5):
        cases.append(
            {
                "id": f"case_{i + 1}",
                "input": spec["sample_input"],
                "expected_output": spec["sample_output"],
                "metadata": {"synthetic": True, "split": "train" if i < 4 else "holdout"},
            }
        )
    return {"test_cases": cases}


def main() -> None:
    for agent_name, spec in AGENT_SPECS.items():
        setup_dir = ROOT / ".overmind" / "agents" / agent_name / "setup_spec"
        setup_dir.mkdir(parents=True, exist_ok=True)
        eval_spec = build_eval_spec(agent_name, spec)
        dataset = build_dataset(spec)
        (setup_dir / "eval_spec.json").write_text(json.dumps(eval_spec, indent=2))
        (setup_dir / "dataset.json").write_text(json.dumps(dataset, indent=2))
        policy_src = ROOT / "policies" / f"{agent_name}.md"
        if policy_src.is_file():
            (setup_dir / "policies.md").write_text(policy_src.read_text())
        print(f"Wrote setup_spec for {agent_name}")


if __name__ == "__main__":
    main()
