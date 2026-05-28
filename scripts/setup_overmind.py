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
# See docs/LLM_ARCHITECTURE.md — agents use Cursor; Overmind analyzer uses OpenAI.

# Overmind platform
OVERMIND_API_KEY=your_overmind_api_key_here
OVERMIND_PROJECT_ID=your_project_id_here
OVERMIND_ENVIRONMENT=development
OVERMIND_SERVICE_NAME=signal-platform

# OpenAI — Overmind setup, optimize, analyzer, synthetic datagen
OPENAI_API_KEY=your_openai_api_key_here
ANALYZER_MODEL=gpt-4o-mini
SYNTHETIC_DATAGEN_MODEL=gpt-4o-mini
DEFAULT_LLM_PROVIDER=openai

# Cursor — agent harness evals (Composer 2.5)
CURSOR_API_KEY=
CURSOR_MODEL=composer-2.5
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