"""
Register Optimized Agents with Overmind

This script registers all 5 optimized SIGNAL platform agents
with Overmind using the new policy structure and evaluation framework.
"""

import os
import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

from shared.utils.settings import settings


def generate_registration_commands():
    """Generate Cursor IDE commands for registering optimized agents."""
    
    overmind_api_key = settings.overmind_api_key
    
    if not overmind_api_key:
        print("❌ OVERMIND_API_KEY not configured")
        return None
    
    agents = [
        {
            "name": "bid_strategy_agent",
            "policy_file": "policies/bid_strategy_agent_optimized.md",
            "description": "Optimized bid strategy agent with Overmind evaluation",
            "function_name": "bid_strategy_recommend"
        },
        {
            "name": "content_brief_agent",
            "policy_file": "policies/content_brief_agent_optimized.md",
            "description": "Optimized content brief agent with Overmind evaluation",
            "function_name": "content_brief_generate"
        },
        {
            "name": "creative_optimization_agent",
            "policy_file": "policies/creative_optimization_agent_optimized.md",
            "description": "Optimized creative optimization agent with Overmind evaluation",
            "function_name": "creative_optimization_analyze"
        },
        {
            "name": "market_analysis_agent",
            "policy_file": "policies/market_analysis_agent_optimized.md",
            "description": "Optimized market analysis agent with Overmind evaluation",
            "function_name": "market_analysis_insight"
        },
        {
            "name": "orchestration_agent",
            "policy_file": "policies/orchestration_agent_optimized.md",
            "description": "Optimized orchestration agent with Overmind evaluation",
            "function_name": "orchestration_coordinate"
        }
    ]
    
    print("=" * 80)
    print("OPTIMIZED AGENT REGISTRATION COMMANDS")
    print("=" * 80)
    print()
    print("Copy and paste these commands into Cursor IDE to register the optimized agents:")
    print()
    
    for agent in agents:
        policy_path = os.path.join("/Users/molyleelatham/Documents/adtech-hackathon", agent["policy_file"])
        
        print(f"# Register {agent['name']}")
        print(f"cursor agent register \\")
        print(f"  --name {agent['name']} \\")
        print(f"  --description \"{agent['description']}\" \\")
        print(f"  --policy \"{policy_path}\" \\")
        print(f"  --overmind-api-key {overmind_api_key} \\")
        print(f"  --function-name {agent['function_name']} \\")
        print(f"  --enable-tracing \\")
        print(f"  --enable-evaluation")
        print()
    
    print("=" * 80)
    print("REGISTRATION COMPLETE")
    print("=" * 80)
    print()
    print("After registration:")
    print("1. Verify agents are registered in Overmind dashboard")
    print("2. Check evaluation pipeline is active")
    print("3. Monitor agent performance in the dashboard")
    print("4. Review quality scores and thresholds")
    print()


def generate_evaluation_config():
    """Generate Overmind evaluation configuration for all agents."""
    
    config = {
        "evaluation_pipeline": {
            "enabled": True,
            "schedule": "daily",
            "timezone": "UTC"
        },
        "quality_thresholds": {
            "bid_strategy_agent": {
                "accuracy": 0.85,
                "roas_maintenance": 0.95,
                "confidence_calibration": 0.80
            },
            "content_brief_agent": {
                "differentiation": 0.75,
                "acceptance_rate": 0.80,
                "platform_fit": 0.85
            },
            "creative_optimization_agent": {
                "prediction_accuracy": 0.90,
                "performance_improvement": 0.20,
                "acceptance_rate": 0.70
            },
            "market_analysis_agent": {
                "insight_accuracy": 0.85,
                "false_positive_rate": 0.15,
                "source_quality": 2.0
            },
            "orchestration_agent": {
                "completion_rate": 0.95,
                "execution_time": 900.0,
                "agent_success_rate": 0.90,
                "fallback_usage": 0.10
            }
        },
        "retrain_triggers": {
            "consecutive_failures": 3,
            "accuracy_drop_threshold": 0.10,
            "confidence_drop_threshold": 0.15
        },
        "monitoring": {
            "dashboard_enabled": True,
            "alerts_enabled": True,
            "alert_channels": ["email", "slack"]
        }
    }
    
    import json
    config_path = "/Users/molyleelatham/Documents/adtech-hackathon/.overmind/evaluation_config.json"
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Evaluation configuration saved to: {config_path}")
    print()
    print("Configuration includes:")
    print("  - Daily evaluation schedule")
    print("  - Quality thresholds for each agent")
    print("  - Automatic retrain triggers")
    print("  - Monitoring and alerting")
    print()


def main():
    """Main registration function."""
    
    print("=" * 80)
    print("OPTIMIZED AGENT REGISTRATION")
    print("=" * 80)
    print()
    print("This script generates registration commands for optimized agents")
    print("with Overmind evaluation framework.")
    print()
    
    # Generate registration commands
    commands = generate_registration_commands()
    
    if commands is None:
        return
    
    # Generate evaluation configuration
    generate_evaluation_config()
    
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Copy the registration commands above")
    print("2. Paste them into Cursor IDE")
    print("3. Verify registration in Overmind dashboard")
    print("4. Check evaluation_config.json for thresholds")
    print("5. Monitor agent performance")
    print()
    print("For more information, see:")
    print("  - OPTIMIZED_AGENT_STRATEGY_BRIEFS.md")
    print("  - policies/*_optimized.md")
    print()


if __name__ == "__main__":
    main()