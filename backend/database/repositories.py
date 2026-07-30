"""
Atlas Quant Platform - Repository Pattern.

Data access layer using the repository pattern.
Repositories abstract database operations behind interfaces.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Protocol, TypeVar

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import LotteryGame, DrawRecord, StrategyRun


# ---- Generic Repository Protocol ----
T = TypeVar("T")


class RepositoryProtocol(Protocol[T]):
    """Generic repository protocol."""

    async def save(self, entity: T) -> T:
        ...

    async def find_by_id(self, id: str) -> Optional[T]:
        ...

    async def delete(self, entity: T) -> None:
        ...

    async def count(self) -> int:
        ...


# ---- Base Repository Implementation ----
class BaseRepository:
    """Base repository with common methods."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, instance: Any) -> Any:
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def delete(self, instance: Any) -> None:
        await self._session.delete(instance)

    async def flush(self) -> None:
        await self._session.flush()


# ---- LotteryGame Repository ----
class LotteryGameRepository(BaseRepository):
    """Repository for LotteryGame entities."""

    async def find_by_id(self, id: str) -> Optional[LotteryGame]:
        result = await self._session.get(LotteryGame, id)
        return result

    async def find_by_code(self, code: str) -> Optional[LotteryGame]:
        stmt = select(LotteryGame).where(LotteryGame.code == code)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> List[LotteryGame]:
        stmt = select(LotteryGame).order_by(LotteryGame.code)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count(LotteryGame.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def upsert_by_code(self, game: LotteryGame) -> LotteryGame:
        existing = await self.find_by_code(game.code)
        if existing:
            existing.name = game.name
            existing.region = game.region
            existing.main_range = game.main_range
            existing.bonus_range = game.bonus_range
            existing.draw_schedule = game.draw_schedule
            existing.metadata_json = game.metadata_json
            return existing
        self._session.add(game)
        return game


# ---- DrawRecord Repository ----
class DrawRecordRepository(BaseRepository):
    """Repository for DrawRecord entities."""

    async def find_by_id(self, id: str) -> Optional[DrawRecord]:
        result = await self._session.get(DrawRecord, id)
        return result

    async def find_by_lottery_and_number(
        self, lottery_code: str, draw_number: str
    ) -> Optional[DrawRecord]:
        stmt = select(DrawRecord).where(
            and_(
                DrawRecord.lottery_code == lottery_code,
                DrawRecord.draw_number == draw_number,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_lottery_and_date_range(
        self,
        lottery_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DrawRecord]:
        conditions = [DrawRecord.lottery_code == lottery_code]
        if start_date:
            conditions.append(DrawRecord.draw_date >= start_date)
        if end_date:
            conditions.append(DrawRecord.draw_date <= end_date)
        stmt = (
            select(DrawRecord)
            .where(and_(*conditions))
            .order_by(desc(DrawRecord.draw_date))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_latest(self, lottery_code: str, n: int = 1) -> List[DrawRecord]:
        stmt = (
            select(DrawRecord)
            .where(DrawRecord.lottery_code == lottery_code)
            .order_by(desc(DrawRecord.draw_date))
            .limit(n)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_lottery(self, lottery_code: str) -> int:
        stmt = select(func.count(DrawRecord.id)).where(
            DrawRecord.lottery_code == lottery_code
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def save_many(self, records: List[DrawRecord]) -> List[DrawRecord]:
        self._session.add_all(records)
        await self._session.flush()
        return records

    async def exists_by_lottery_and_number(
        self, lottery_code: str, draw_number: str
    ) -> bool:
        stmt = select(DrawRecord.id).where(
            and_(
                DrawRecord.lottery_code == lottery_code,
                DrawRecord.draw_number == draw_number,
            )
        ).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_statistics(self, lottery_code: str) -> Dict[str, Any]:
        """获取彩种的基本统计信息。"""
        total = await self.count_by_lottery(lottery_code)
        latest_records = await self.find_latest(lottery_code, 1)
        earliest_stmt = (
            select(DrawRecord)
            .where(DrawRecord.lottery_code == lottery_code)
            .order_by(DrawRecord.draw_date)
            .limit(1)
        )
        result = await self._session.execute(earliest_stmt)
        earliest = result.scalar_one_or_none()
        return {
            "lottery_code": lottery_code,
            "total_draws": total,
            "earliest_date": str(earliest.draw_date) if earliest else None,
            "latest_date": str(latest_records[0].draw_date) if latest_records else None,
            "latest_draw_number": latest_records[0].draw_number if latest_records else None,
        }


# ---- StrategyRun Repository ----
class StrategyRunRepository(BaseRepository):
    """Repository for StrategyRun entities."""

    async def find_by_id(self, id: str) -> Optional[StrategyRun]:
        result = await self._session.get(StrategyRun, id)
        return result

    async def find_by_lottery(self, lottery_code: str, limit: int = 20) -> List[StrategyRun]:
        stmt = (
            select(StrategyRun)
            .where(StrategyRun.lottery_code == lottery_code)
            .order_by(desc(StrategyRun.created_at))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        stmt = select(func.count(StrategyRun.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0
