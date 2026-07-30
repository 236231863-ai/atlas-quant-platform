"""
Atlas Quant Platform - Draw Service.

Service layer orchestrates:
1. Receives requests from API
2. Uses repositories to access data
3. Calls engine for computation (future)
4. Returns results
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import LotteryGame, DrawRecord, StrategyRun
from backend.database.repositories import (
    LotteryGameRepository,
    DrawRecordRepository,
    StrategyRunRepository,
)
from core.types.models import LotteryGameData, DrawRecordData, DrawStatistics


class DrawService:
    """Service for draw data operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._game_repo = LotteryGameRepository(session)
        self._draw_repo = DrawRecordRepository(session)

    async def create_game(self, data: LotteryGameData) -> LotteryGameData:
        game = LotteryGame(
            code=data.code,
            name=data.name,
            region=data.region,
            main_range=data.main_range or {},
            bonus_range=data.bonus_range,
            draw_schedule=data.draw_schedule,
        )
        saved = await self._game_repo.save(game)
        data.id = saved.id
        return data

    async def get_game(self, code: str) -> Optional[LotteryGameData]:
        game = await self._game_repo.find_by_code(code)
        if not game:
            return None
        return LotteryGameData(
            code=game.code, name=game.name, region=game.region,
            main_range=game.main_range, bonus_range=game.bonus_range,
            draw_schedule=game.draw_schedule, id=game.id,
        )

    async def list_games(self) -> List[LotteryGameData]:
        games = await self._game_repo.list_all()
        return [
            LotteryGameData(
                code=g.code, name=g.name, region=g.region,
                main_range=g.main_range, bonus_range=g.bonus_range,
                draw_schedule=g.draw_schedule, id=g.id,
            )
            for g in games
        ]

    async def save_draw(self, data: DrawRecordData) -> DrawRecordData:
        record = DrawRecord(
            lottery_code=data.lottery_code,
            draw_number=data.draw_number,
            draw_date=data.draw_date,
            main_numbers=data.main_numbers,
            bonus_numbers=data.bonus_numbers,
            pool_amount=data.pool_amount,
        )
        saved = await self._draw_repo.save(record)
        data.id = saved.id
        return data

    async def save_draws_batch(self, records: List[DrawRecordData]) -> List[DrawRecordData]:
        orm_records = [
            DrawRecord(
                lottery_code=r.lottery_code,
                draw_number=r.draw_number,
                draw_date=r.draw_date,
                main_numbers=r.main_numbers,
                bonus_numbers=r.bonus_numbers,
                pool_amount=r.pool_amount,
            )
            for r in records
        ]
        saved = await self._draw_repo.save_many(orm_records)
        for r, s in zip(records, saved):
            r.id = s.id
        return records

    async def get_draws(
        self,
        lottery_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DrawRecordData]:
        sd = date.fromisoformat(start_date) if start_date else None
        ed = date.fromisoformat(end_date) if end_date else None
        records = await self._draw_repo.find_by_lottery_and_date_range(
            lottery_code, sd, ed, limit, offset
        )
        return [
            DrawRecordData(
                id=r.id, lottery_code=r.lottery_code,
                draw_number=r.draw_number, draw_date=r.draw_date,
                main_numbers=r.main_numbers, bonus_numbers=r.bonus_numbers,
                pool_amount=r.pool_amount,
            )
            for r in records
        ]

    async def get_latest_draw(self, lottery_code: str) -> Optional[DrawRecordData]:
        records = await self._draw_repo.find_latest(lottery_code, 1)
        if not records:
            return None
        r = records[0]
        return DrawRecordData(
            id=r.id, lottery_code=r.lottery_code,
            draw_number=r.draw_number, draw_date=r.draw_date,
            main_numbers=r.main_numbers, bonus_numbers=r.bonus_numbers,
            pool_amount=r.pool_amount,
        )

    async def get_statistics(self, lottery_code: str) -> DrawStatistics:
        stats = await self._draw_repo.get_statistics(lottery_code)
        return DrawStatistics(**stats)
