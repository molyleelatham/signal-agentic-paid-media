"""
Agent Registration Test Script

This script verifies that all agents are properly configured for Overmind registration
and provides detailed instructions for registration in Cursor IDE.

Usage:
    python scripts/test_agent_registration.py
"""

import os
import sys
from pathlib import Path
import importlib.util


def test_agent_file(agent_path: str) -> dict:
    """Test if an agent file is properly structured."""
    result = {
        "file_exists": False,
        "has_base_agent": False,
        "has_overmind_tracer": False,
        "has_cursor_composer": False,
        "has_main_methods": False,
        "errors": []
    }
    
    agent_file = Path(agent_path)
    if not agent_file.exists():
        result["errors"].append(f"File not found: {agent_path}")
        return result
    
    result["file_exists"] = True
    
    try:
        with open(agent_file) as f:
            content = f.read()
        
        # Check for BaseAgent import
        if "BaseAgent" in content:
            result["has_base_agent"] = True
        else:
            result["errors"].append("Missing BaseAgent import")
        
        # Check for OvermindTracer
        if "OvermindTracer" in content:
            result["has_overmind_tracer"] = True
        else:
            result["errors"].append("Missing OvermindTracer")
        
        # Check for CursorComposerService
        if "CursorComposerService" in content:
            result["has_cursor_composer"] = True
        else:
            result["errors"].append("Missing CursorComposerService")
        
        # Check for main methods (execute, analyze, generate, etc.)
        main_methods = ["execute", "analyze", "generate", "coordinate", "make_decision"]
        if any(method in content for method in main_methods):
            result["has_main_methods"] = True
        else:
            result["errors"].append("No main execution method found")
        
    except Exception as e:
        result["errors"].append(f"Error reading file: {e}")
    
    return result


def test_policy_file(policy_path: str) -> dict:
    """Test if a policy file is properly structured."""
    result = {
        "file_exists": False,
        "has_overview": False,
        "has_capabilities": False,
        "has_input_schema": False,
        "has_output_schema": False,
        "has_constraints": False,
        "errors": []
    }
    
    policy_file = Path(policy_path)
    if not policy_file.exists():
        result["errors"].append(f"File not found: {policy_path}")
        return result
    
    result["file_exists"] = True
    
    try:
        with open(policy_file) as f:
            content = f.read()
        
        # Check for required sections
        sections = [
            ("Agent Overview", "has_overview"),
            ("Capabilities", "has_capabilities"),
            ("Input Schema", "has_input_schema"),
            ("Output Schema", "has_output_schema"),
            ("Constraints", "has_constraints")
        ]
        
        for section_name, result_key in sections:
            if section_name in content:
                result[result_key] = True
            else:
                result["errors"].append(f"Missing section: {section_name}")
        
    except Exception as e:
        result["errors"].append(f"Error reading file: {e}")
    
    return result


def test_overmind_config() -> dict:
    """Test if Overmind is properly configured."""
    result = {
        "has_api_key": False,
        "has_project_id": False,
        "has_openai_key": False,
        "overmind_installed": False,
        "errors": []
    }
    
    # Check environment variables
    if os.getenv("OVERMIND_API_KEY"):
        result["has_api_key"] = True
    else:
        result["errors"].append("OVERMIND_API_KEY not set in environment")
    
    if os.getenv("OVERMIND_PROJECT_ID"):
        result["has_project_id"] = True
    else:
        result["errors"].append("OVERMIND_PROJECT_ID not set in environment")
    
    if os.getenv("OPENAI_API_KEY"):
        result["has_openai_key"] = True
    else:
        result["errors"].append("OPENAI_API_KEY not set in environment")
    
    # Check if Overmind is installed
    try:
        import overmind
        result["overmind_installed"] = True
    except ImportError:
        result["errors"].append("Overmind SDK not installed")
    
    return result


def main():
    """Main test function."""
    
    print("=" * 80)
    print("SIGNAL Platform - Agent Registration Test")
    print("=" * 80)
    print()
    
    agents = [
        {
            "name": "bid_strategy_agent",
            "path": "services/agents/bid_strategy_agent.py",
            "policy": "policies/bid_strategy_agent.md"
        },
        {
            "name": "content_brief_agent",
            "path": "services/agents/content_brief_agent.py",
            "policy": "policies/content_brief_agent.md"
        },
        {
            "name": "creative_optimization_agent",
            "path": "services/agents/creative_optimization_agent.py",
            "policy": "policies/creative_optimization_agent.md"
        },
        {
            "name": "market_analysis_agent",
            "path": "services/agents/market_analysis_agent.py",
            "policy": "policies/market_analysis_agent.md"
        },
        {
            "name": "orchestration_agent",
            "path": "services/agents/orchestration_agent.py",
            "policy": "policies/orchestration_agent.md"
        }
    ]
    
    # Test Overmind configuration
    print("Testing Overmind Configuration...")
    print("-" * 80)
    overmind_config = test_overmind_config()
    
    if overmind_config["overmind_installed"]:
        print("✅ Overmind SDK installed")
    else:
        print("❌ Overmind SDK not installed")
    
    if overmind_config["has_api_key"]:
        print("✅ OVERMIND_API_KEY set")
    else:
        print("❌ OVERMIND_API_KEY not set")
    
    if overmind_config["has_project_id"]:
        print("✅ OVERMIND_PROJECT_ID set")
    else:
        print("❌ OVERMIND_PROJECT_ID not set")
    
    if overmind_config["has_openai_key"]:
        print("✅ OPENAI_API_KEY set")
    else:
        print("❌ OPENAI_API_KEY not set")
    
    if overmind_config["errors"]:
        print()
        print("Configuration Errors:")
        for error in overmind_config["errors"]:
            print(f"  ⚠️  {error}")
    print()
    
    # Test each agent
    all_passed = True
    for agent in agents:
        print(f"Testing {agent['name']}...")
        print("-" * 80)
        
        # Test agent file
        agent_test = test_agent_file(agent['path'])
        
        if agent_test["file_exists"]:
            print(f"✅ Agent file exists: {agent['path']}")
        else:
            print(f"❌ Agent file missing: {agent['path']}")
            all_passed = False
        
        if agent_test["has_base_agent"]:
            print("✅ Has BaseAgent import")
        else:
            print("❌ Missing BaseAgent import")
            all_passed = False
        
        if agent_test["has_overmind_tracer"]:
            print("✅ Has OvermindTracer")
        else:
            print("❌ Missing OvermindTracer")
            all_passed = False
        
        if agent_test["has_cursor_composer"]:
            print("✅ Has CursorComposerService")
        else:
            print("❌ Missing CursorComposerService")
            all_passed = False
        
        if agent_test["has_main_methods"]:
            print("✅ Has main execution methods")
        else:
            print("❌ Missing main execution methods")
            all_passed = False
        
        # Test policy file
        policy_test = test_policy_file(agent['policy'])
        
        if policy_test["file_exists"]:
            print(f"✅ Policy file exists: {agent['policy']}")
        else:
            print(f"❌ Policy file missing: {agent['policy']}")
            all_passed = False
        
        if policy_test["has_overview"]:
            print("✅ Policy has Agent Overview section")
        else:
            print("❌ Policy missing Agent Overview")
            all_passed = False
        
        if policy_test["has_capabilities"]:
            print("✅ Policy has Capabilities section")
        else:
            print("❌ Policy missing Capabilities")
            all_passed = False
        
        if policy_test["has_input_schema"]:
            print("✅ Policy has Input Schema section")
        else:
            print("❌ Policy missing Input Schema")
            all_passed = False
        
        if policy_test["has_output_schema"]:
            print("✅ Policy has Output Schema section")
        else:
            print("❌ Policy missing Output Schema")
            all_passed = False
        
        if policy_test["has_constraints"]:
            print("✅ Policy has Constraints section")
        else:
            print("❌ Policy missing Constraints")
            all_passed = False
        
        if agent_test["errors"] or policy_test["errors"]:
            print()
            print("Errors:")
            for error in agent_test["errors"] + policy_test["errors"]:
                print(f"  ⚠️  {error}")
        
        print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    if all_passed and not overmind_config["errors"]:
        print("✅ All agents are ready for Overmind registration!")
        print()
        print("Next Steps:")
        print("1. Open Cursor IDE")
        print("2. Open the command palette (Cmd+K)")
        print("3. Run the following commands:")
        print()
        for agent in agents:
            print(f"   /overmind-register-agent {agent['path']}")
            print(f"   /overmind-optimize-agent {agent['name']}")
            print()
        print("4. Verify registration at https://platform.overmind.ai")
    else:
        print("❌ Some agents are not ready for registration")
        print()
        print("Please fix the errors above before registering agents.")
        if overmind_config["errors"]:
            print()
            print("To fix configuration errors:")
            print("1. Set OVERMIND_API_KEY in .env")
            print("2. Set OVERMIND_PROJECT_ID in .env")
            print("3. Set OPENAI_API_KEY in .env")
            print("4. Install Overmind: pip install overmind")


if __name__ == "__main__":
    main()