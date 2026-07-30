"""
Atlas Quant Platform - Database Session Management.

SQLAlchemy 2.x async session configuration.
SQLite for development, PostgreSQL for production.
"""
from __future__ import annotations

import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""
    pass


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_db_url() -> str:
    """Get database URL from environment or use default SQLite."""
    return os.getenv("ATLAS_DB_URL", "sqlite+aiosqlite:///data/atlas.db")


def create_engine(db_url: Optional[str] = None) -> AsyncEngine:
    """Create database engine."""
    global _engine
    url = db_url or get_db_url()
    _engine = create_async_engine(
        url,
        echo=os.getenv("ATLAS_DB_ECHO", "false").lower() == "true",
        pool_size=5,
        max_overflow=10,
    )
    return _engine


def get_engine() -> AsyncEngine:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        return create_engine()
    return _engine


def create_session_factory(engine: Optional[AsyncEngine] = None) -> async_sessionmaker[AsyncSession]:
    """Create async session factory."""
    global _session_factory
    eng = engine or get_engine()
    _session_factory = async_sessionmaker(eng, class_=AsyncSession, expire_on_commit=False)
    return _session_factory


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create session factory."""
    global _session_factory
    if _session_factory is None:
        return create_session_factory()
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield a database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db(engine: Optional[AsyncEngine] = None) -> None:
    """Create all tables. For development/testing use."""
    eng = engine or get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """Dispose the database engine."""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
