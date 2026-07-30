"""Test configuration and shared fixtures."""
from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

from backend.database.session import Base, init_db, dispose_engine
from backend.database.models import LotteryGame, DrawRecord
from backend.database.repositories import (
    LotteryGameRepository,
    DrawRecordRepository,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create in-memory SQLite engine for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def game_repo(db_session: AsyncSession) -> LotteryGameRepository:
    return LotteryGameRepository(db_session)


@pytest_asyncio.fixture
async def draw_repo(db_session: AsyncSession) -> DrawRecordRepository:
    return DrawRecordRepository(db_session)


@pytest.fixture
def sample_game() -> LotteryGame:
    return LotteryGame(
        code="dlt",
        name="大乐透",
        region="CN",
        main_range={"min": 1, "max": 35, "count": 5},
        bonus_range={"min": 1, "max": 12, "count": 2},
    )


@pytest.fixture
def sample_draw() -> DrawRecord:
    return DrawRecord(
        lottery_code="dlt",
        draw_number="24001",
        draw_date=date(2024, 1, 1),
        main_numbers=[5, 12, 18, 25, 30],
        bonus_numbers=[2, 7],
        pool_amount=Decimal("850000000.00"),
    )


@pytest.fixture
def sample_draws() -> list:
    """Sample draws for batch testing."""
    return [
        DrawRecord(
            lottery_code="dlt",
            draw_number=f"240{str(i).zfill(2)}",
            draw_date=date(2024, 1, i),
            main_numbers=[1, 2, 3, 4, 5],
            bonus_numbers=[1, 2],
        )
        for i in range(1, 11)
    ]
