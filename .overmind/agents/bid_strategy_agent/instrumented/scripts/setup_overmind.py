"""
Overmind Setup Helper Script
Helps configure Overmind for SIGNAL Platform
"""

import os
from pathlib import Path


def setup_overmind():
    """Setup Overmind configuration files."""
    
    print("=" * 60)
    print("SIGNAL Platform - Overmind Setup")
    print("=" * 60)
    print()
    
    # Create .overmind directory
    overmind_dir = Path(".overmind")
    overmind_dir.mkdir(exist_ok=True)
    print(f"✅ Created .overmind directory")
    
    # Check if .env exists
    env_file = overmind_dir / ".env"
    if env_file.exists():
        print(f"✅ Overmind .env already exists")
        print()
        print("Current configuration:")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    # Mask API keys
                    if "=" in line and "API_KEY" in line.upper():
                        key, value = line.split("=", 1)
                        masked_value = value[:8] + "..." if len(value) > 8 else "***"
                        print(f"  {key}={masked_value}")
                    else:
                        print(f"  {line.strip()}")
    else:
        print(f"⚠️  Overmind .env not found")
        print()
        print("Creating template .env file...")
        
        template = """# Overmind Configuration for SIGNAL Platform
# Get your API key from: https://platform.overmind.ai/

# OpenAI API Key (required for OpenAI models)
OPENAI_API_KEY=your_openai_api_key_here

# Overmind API Key (required for Overmind platform)
OVERMIND_API_KEY=your_overmind_api_key_here

# Overmind Project ID
OVERMIND_PROJECT_ID=your_project_id_here

# Environment
OVERMIND_ENVIRONMENT=development

# Service Name
OVERMIND_SERVICE_NAME=signal-platform

# LLM Provider (openai, anthropic, google-genai)
DEFAULT_LLM_PROVIDER=openai

# Model Settings
DEFAULT_MODEL=gpt-4-turbo
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
"""
        
        with open(env_file, "w") as f:
            f.write(template)
        
        print(f"✅ Created .overmind/.env template")
    
    print()
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Edit .overmind/.env")
    print("  2. Add your OPENAI_API_KEY (from https://platform.openai.com/api-keys)")
    print("  3. Add your OVERMIND_API_KEY (from https://platform.overmind.ai)")
    print("  4. Add your OVERMIND_PROJECT_ID")
    print()
    print("Get Overmind credentials:")
    print("  - Go to: https://platform.overmind.ai")
    print("  - Sign up or login")
    print("  - Create a new project")
    print("  - Copy API key and project ID")
    print()
    print("Optional: Install Cursor IDE skills")
    print("  - Overmind installs skills automatically for Cursor")
    print("  - Skills are in: .cursor/skills/")
    print()


if __name__ == "__main__":
    setup_overmind()