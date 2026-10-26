"""
Initialize database schema for local development.
Optimized for localhost hosting.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from shared.utils.settings import settings
from shared.database import Base
import shared.models  # noqa: F401  # register every table before create_all


async def init_database():
    """Initialize database schema."""
    print("Creating database engine...")
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=10,  # Optimized for localhost
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600
    )
    
    print("Creating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database schema created successfully")
    await engine.dispose()


async def create_extensions():
    """Create PostgreSQL extensions for better performance."""
    # The sync URL has no async driver. Extensions use the same async URL as the tables.
    engine = create_async_engine(settings.database_url)
    
    extensions = [
        "uuid-ossp",  # UUID generation
        "pg_trgm",    # Text similarity (for search)
        "btree_gin",  # GIN index support
        "btree_gist"   # GiST index support
    ]
    
    async with engine.begin() as conn:
        for ext in extensions:
            try:
                await conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS \"{ext}\""))
                print(f"✅ Created extension: {ext}")
            except Exception as e:
                print(f"⚠️  Could not create extension {ext}: {e}")
    
    await engine.dispose()


async def main():
    """Main initialization function."""
    print("=" * 50)
    print("SIGNAL Platform - Database Initialization")
    print("=" * 50)
    print()
    
    await create_extensions()
    await init_database()
    
    print()
    print("=" * 50)
    print("Database initialization complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  make demo-data    - Populate Gymshark demo data")
    print("  make server       - Start the server")
    print()


if __name__ == "__main__":
    asyncio.run(main())