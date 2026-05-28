"""
Database configuration and session management.
Optimized for localhost development.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from shared.utils.settings import settings


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Database connection pool settings (optimized for localhost)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create async engine with localhost-optimized settings
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=DB_POOL_SIZE,  # Connection pool size (lower for localhost)
    max_overflow=DB_MAX_OVERFLOW,  # Max overflow connections
    pool_timeout=DB_POOL_TIMEOUT,  # Timeout for getting connection from pool
    pool_recycle=DB_POOL_RECYCLE,  # Recycle connections after N seconds
    connect_args={
        "command_timeout": 60,  # Command timeout in seconds
        "server_settings": {
            "application_name": "signal-platform-dev",  # Identify connection
            "jit": "off",  # Disable JIT for development (faster for small queries)
        }
    }
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    
    Usage:
        async with get_db_session() as session:
            # Use session here
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for FastAPI.
    
    Usage in FastAPI:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()