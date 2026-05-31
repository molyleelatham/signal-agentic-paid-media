"""
Master Demo Setup Script

Runs all demo data setup scripts in the correct order:
1. Initialize database
2. Create base client data (demo_data.py)
3. Create comprehensive demo data (comprehensive_demo_data.py)
"""

import asyncio
import subprocess
import sys


def run_command(cmd: str, description: str):
    """Run a command and print the result."""
    print("=" * 80)
    print(f"STEP: {description}")
    print("=" * 80)
    print(f"Running: {cmd}")
    print()
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        return False
    
    print(f"✅ {description} completed successfully")
    print()
    return True


async def main():
    """Main setup function."""
    
    print("=" * 80)
    print("MASTER DEMO SETUP")
    print("=" * 80)
    print()
    print("This script will:")
    print("1. Initialize/reset the database")
    print("2. Create base client and campaign data")
    print("3. Create comprehensive historical data")
    print("4. Create model performance tracking")
    print("5. Create keyword performance data")
    print("6. Create agent execution history")
    print("7. Create A/B test data")
    print("8. Create content performance data")
    print()
    
    # Step 1: Initialize database
    if not run_command(
        "python3 scripts/init_db.py",
        "Initialize Database"
    ):
        print("❌ Database initialization failed. Exiting.")
        return
    
    # Step 2: Create base demo data
    if not run_command(
        "python3 scripts/demo_data.py",
        "Create Base Demo Data (Client, Campaigns, etc.)"
    ):
        print("❌ Base demo data creation failed. Exiting.")
        return
    
    # Step 3: Create comprehensive demo data
    if not run_command(
        "python3 scripts/comprehensive_demo_data.py",
        "Create Comprehensive Demo Data (Historical, Performance, etc.)"
    ):
        print("❌ Comprehensive demo data creation failed. Exiting.")
        return
    
    print("=" * 80)
    print("MASTER DEMO SETUP COMPLETE")
    print("=" * 80)
    print()
    print("All demo data has been successfully created!")
    print()
    print("You can now:")
    print("  - Start the API server: python3 -m api.main")
    print("  - Run the frontend: cd frontend adtech && npm run dev")
    print("  - Access the Bloomberg Terminal: http://localhost:8000/terminal")
    print("  - Test the API endpoints")
    print()


if __name__ == "__main__":
    asyncio.run(main())