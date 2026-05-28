"""Database configuration and session management."""

from shared.database.config import Base, async_session_factory, engine, get_db, get_db_session

# Alias for compatibility
get_async_session = get_db_session

__all__ = ["Base", "async_session_factory", "engine", "get_db", "get_db_session", "get_async_session"]