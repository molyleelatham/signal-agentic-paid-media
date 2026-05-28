"""
Reset database - drop all tables and recreate schema.
WARNING: This will delete all data!
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

from shared.utils.settings import settings
from shared.database import Base


async def reset_database():
    """Reset database by dropping all tables and recreating schema."""
    print("=" * 50)
    print("⚠️  DATABASE RESET - ALL DATA WILL BE LOST")
    print("=" * 50)
    print()
    
    engine = create_async_engine(
        settings.database_url,
        echo=True
    )
    
    print("Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Recreating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database reset complete")
    await engine.dispose()


async def main():
    """Main reset function."""
    response = input("Are you sure you want to reset the database? [y/N]: ")
    if response.lower() == 'y':
        await reset_database()
        print()
        print("Next steps:")
        print("  make demo-data    - Populate Gymshark demo data")
    else:
        print("❌ Cancelled")


if __name__ == "__main__":
    asyncio.run(main())