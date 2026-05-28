"""
Overmind Agent Registration Script

This script provides the commands to register SIGNAL platform agents with Overmind
using the Cursor IDE skills.

Usage:
    python scripts/register_overmind_agents.py

This will output the commands to run in Cursor IDE to register each agent.
"""

import os
from pathlib import Path


# Agent definitions with their file paths and policies
AGENTS = [
    {
        "name": "bid_strategy_agent",
        "path": "services/agents/bid_strategy_agent.py",
        "policy": "policies/bid_strategy_agent.md",
        "description": "Makes strategic bidding decisions for media buying"
    },
    {
        "name": "content_brief_agent",
        "path": "services/agents/content_brief_agent.py",
        "policy": "policies/content_brief_agent.md",
        "description": "Generates creative briefs based on gap analysis"
    },
    {
        "name": "creative_optimization_agent",
        "path": "services/agents/creative_optimization_agent.py",
        "policy": "policies/creative_optimization_agent.md",
        "description": "Analyzes and optimizes creative performance"
    },
    {
        "name": "market_analysis_agent",
        "path": "services/agents/market_analysis_agent.py",
        "policy": "policies/market_analysis_agent.md",
        "description": "Analyzes market intelligence and provides strategic insights"
    },
    {
        "name": "orchestration_agent",
        "path": "services/agents/orchestration_agent.py",
        "policy": "policies/orchestration_agent.md",
        "description": "Central coordinator for all AI agents"
    }
]


def print_registration_commands():
    """Print Overmind registration commands for each agent."""
    
    print("=" * 80)
    print("Overmind Agent Registration Commands")
    print("=" * 80)
    print()
    print("These commands should be run in Cursor IDE using the Overmind skills.")
    print()
    print("Prerequisites:")
    print("1. Overmind must be configured (see LOCAL_DEVELOPMENT.md)")
    print("2. Cursor IDE skills must be installed (in .cursor/skills/)")
    print("3. OPENAI_API_KEY and OVERMIND_API_KEY must be set in .env")
    print()
    print("=" * 80)
    print()
    
    for agent in AGENTS:
        print(f"# Register {agent['name']}")
        print(f"# Description: {agent['description']}")
        print(f"# Agent File: {agent['path']}")
        print(f"# Policy File: {agent['policy']}")
        print()
        print(f"/overmind-register-agent {agent['path']}")
        print()
        print(f"# After registration, optimize the agent:")
        print(f"/overmind-optimize-agent {agent['name']}")
        print()
        print("-" * 80)
        print()


def print_optimization_commands():
    """Print Overmind optimization commands for all agents."""
    
    print("=" * 80)
    print("Overmind Agent Optimization Commands")
    print("=" * 80)
    print()
    print("Run these commands after registration to optimize each agent:")
    print()
    
    for agent in AGENTS:
        print(f"/overmind-optimize-agent {agent['name']}")
    
    print()
    print("=" * 80)


def verify_files_exist():
    """Verify that all agent and policy files exist."""
    
    print("=" * 80)
    print("Verifying Agent and Policy Files")
    print("=" * 80)
    print()
    
    project_root = Path.cwd()
    missing_files = []
    
    for agent in AGENTS:
        agent_path = project_root / agent['path']
        policy_path = project_root / agent['policy']
        
        if not agent_path.exists():
            missing_files.append(f"Agent file: {agent['path']}")
            print(f"❌ Missing: {agent['path']}")
        else:
            print(f"✅ Found: {agent['path']}")
        
        if not policy_path.exists():
            missing_files.append(f"Policy file: {agent['policy']}")
            print(f"❌ Missing: {agent['policy']}")
        else:
            print(f"✅ Found: {agent['policy']}")
        
        print()
    
    if missing_files:
        print("=" * 80)
        print("ERROR: Missing files detected!")
        print("=" * 80)
        print()
        for file in missing_files:
            print(f"  - {file}")
        print()
        return False
    else:
        print("=" * 80)
        print("✅ All agent and policy files found!")
        print("=" * 80)
        return True


def main():
    """Main function."""
    
    # First verify files exist
    if not verify_files_exist():
        return
    
    print()
    
    # Print registration commands
    print_registration_commands()
    
    # Print optimization commands
    print()
    print_optimization_commands()
    
    print()
    print("=" * 80)
    print("Next Steps")
    print("=" * 80)
    print()
    print("1. Copy and paste the registration commands into Cursor IDE")
    print("2. Run each /overmind-register-agent command")
    print("3. Run each /overmind-optimize-agent command after registration")
    print("4. Verify registration at https://platform.overmind.ai")
    print()
    print("For more information, see:")
    print("  - LOCAL_DEVELOPMENT.md (Overmind setup)")
    print("  - .cursor/skills/overmind-register-agent/SKILL.md")
    print("  - .cursor/skills/overmind-optimize-agent/SKILL.md")
    print()


if __name__ == "__main__":
    main()