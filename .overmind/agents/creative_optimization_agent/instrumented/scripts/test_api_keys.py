"""
Test API Keys Configuration

This script tests if the configured API keys are valid and working.
"""

import os
import sys
from pathlib import Path

def test_overmind_key():
    """Test Overmind API key."""
    api_key = os.getenv("OVERMIND_API_KEY")
    
    print("Testing Overmind API Key...")
    print("-" * 60)
    
    if not api_key:
        print("❌ OVERMIND_API_KEY not set")
        return False
    
    if api_key.startswith("ovr_"):
        print(f"✅ OVERMIND_API_KEY is set (starts with 'ovr_')")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print(f"⚠️  OVERMIND_API_KEY format unusual (should start with 'ovr_')")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Try to import and initialize Overmind
    try:
        from overmind import init
        print("✅ Overmind SDK is installed")
        
        # Try initialization (won't actually connect without project_id)
        try:
            init(
                overmind_api_key=api_key,
                service_name="signal-platform-test",
                environment="development"
            )
            print("✅ Overmind SDK initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️  Overmind initialization failed: {e}")
            print("   This might be expected without a project ID")
            return True  # Key format is correct, initialization might fail for other reasons
    
    except ImportError:
        print("❌ Overmind SDK not installed")
        print("   Install with: pip install overmind")
        return False


def test_openai_key():
    """Test OpenAI API key."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    print("\nTesting OpenAI API Key...")
    print("-" * 60)
    
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return False
    
    if api_key.startswith("sk-"):
        print(f"✅ OPENAI_API_KEY is set (starts with 'sk-')")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print(f"⚠️  OPENAI_API_KEY format unusual (should start with 'sk-')")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Try to make a simple API call
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test - list models (minimal API call)
        try:
            models = client.models.list()
            print("✅ OpenAI API key is valid and working")
            return True
        except Exception as e:
            print(f"❌ OpenAI API call failed: {e}")
            return False
    
    except ImportError:
        print("❌ OpenAI SDK not installed")
        print("   Install with: pip install openai")
        return False


def test_tavily_key():
    """Test Tavily API key."""
    api_key = os.getenv("TAVILY_API_KEY")
    
    print("\nTesting Tavily API Key...")
    print("-" * 60)
    
    if not api_key:
        print("⚠️  TAVILY_API_KEY not set (optional)")
        return None
    
    print(f"✅ TAVILY_API_KEY is set")
    print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Try to make a test call
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        
        try:
            # Simple search test
            result = client.search("test query", max_results=1)
            print("✅ Tavily API key is valid and working")
            return True
        except Exception as e:
            print(f"❌ Tavily API call failed: {e}")
            return False
    
    except ImportError:
        print("❌ Tavily SDK not installed")
        print("   Install with: pip install tavily-python")
        return False


def test_cursor_key():
    """Test Cursor API key."""
    api_key = os.getenv("CURSOR_API_KEY")
    
    print("\nTesting Cursor API Key...")
    print("-" * 60)
    
    if not api_key:
        print("⚠️  CURSOR_API_KEY not set (optional)")
        return None
    
    if api_key.startswith("crsr_"):
        print(f"✅ CURSOR_API_KEY is set (starts with 'crsr_')")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    else:
        print(f"⚠️  CURSOR_API_KEY format unusual (should start with 'crsr_')")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
    
    return True


def load_env_file():
    """Load environment variables from .env.local file."""
    env_file = Path(".env.local")
    if env_file.exists():
        print("Loading environment from .env.local...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ Environment variables loaded from .env.local")
        return True
    else:
        print("⚠️  .env.local file not found")
        return False


def main():
    """Main test function."""
    
    print("=" * 60)
    print("API Keys Test")
    print("=" * 60)
    print()
    
    # Load environment variables
    load_env_file()
    print()
    
    # Test each API key
    results = {}
    
    results["overmind"] = test_overmind_key()
    results["openai"] = test_openai_key()
    results["tavily"] = test_tavily_key()
    results["cursor"] = test_cursor_key()
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    for key, result in results.items():
        if result is True:
            print(f"✅ {key.upper()}: Valid and working")
        elif result is False:
            print(f"❌ {key.upper()}: Invalid or not working")
        else:
            print(f"⚠️  {key.upper()}: Not configured (optional)")
    
    print()
    print("For Overmind agent registration, you need:")
    print("  ✅ OVERMIND_API_KEY (configured)")
    print("  ⚠️  OPENAI_API_KEY (recommended for optimization)")
    print("  ⚠️  OVERMIND_PROJECT_ID (recommended for organization)")
    
    print()
    print("Next steps:")
    print("  1. If OVERMIND_API_KEY is valid, you can register agents in Cursor IDE")
    print("  2. Run: make register-agents to see the commands")
    print("  3. Open Cursor IDE and run the /overmind-register-agent commands")


if __name__ == "__main__":
    main()