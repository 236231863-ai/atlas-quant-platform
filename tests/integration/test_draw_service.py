"""Integration tests for DrawService."""
from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from backend.service.draw_service import DrawService
from core.types.models import LotteryGameData, DrawRecordData


pytestmark = pytest.mark.integration


class TestDrawService:
    async def test_create_and_get_game(self, db_session: AsyncSession):
        service = DrawService(db_session)
        game_data = LotteryGameData(code="dlt", name="大乐透", region="CN",
                                    main_range={"min": 1, "max": 35, "count": 5})
        created = await service.create_game(game_data)
        assert created.id is not None
        found = await service.get_game("dlt")
        assert found is not None
        assert found.name == "大乐透"

    async def test_list_games(self, db_session: AsyncSession):
        service = DrawService(db_session)
        await service.create_game(LotteryGameData(code="dlt", name="大乐透"))
        await service.create_game(LotteryGameData(code="ssq", name="双色球"))
        games = await service.list_games()
        assert len(games) >= 2

    async def test_save_and_get_draws(self, db_session: AsyncSession):
        service = DrawService(db_session)
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5],
            bonus_numbers=[6, 7],
        )
        saved = await service.save_draw(draw)
        assert saved.id is not None
        draws = await service.get_draws("dlt")
        assert len(draws) >= 1
        assert draws[0].draw_number == "24001"

    async def test_get_latest_draw(self, db_session: AsyncSession):
        service = DrawService(db_session)
        draws = [
            DrawRecordData(lottery_code="dlt", draw_number=f"2400{i}",
                           draw_date=date(2024, 1, i), main_numbers=[1, 2, 3, 4, 5])
            for i in range(1, 4)
        ]
        await service.save_draws_batch(draws)
        latest = await service.get_latest_draw("dlt")
        assert latest is not None
        assert latest.draw_number == "24003"

    async def test_get_statistics(self, db_session: AsyncSession):
        service = DrawService(db_session)
        await service.save_draw(
            DrawRecordData(lottery_code="dlt", draw_number="24001",
                           draw_date=date(2024, 1, 1), main_numbers=[1, 2, 3, 4, 5])
        )
        stats = await service.get_statistics("dlt")
        assert stats.lottery_code == "dlt"
        assert stats.total_draws >= 1

    async def test_get_nonexistent_game(self, db_session: AsyncSession):
        service = DrawService(db_session)
        result = await service.get_game("nonexistent")
        assert result is None

    async def test_get_latest_nonexistent(self, db_session: AsyncSession):
        service = DrawService(db_session)
        result = await service.get_latest_draw("nonexistent")
        assert result is None

    async def test_save_draws_batch(self, db_session: AsyncSession):
        service = DrawService(db_session)
        records = [
            DrawRecordData(lottery_code="dlt", draw_number=f"2400{i}",
                           draw_date=date(2024, 1, i), main_numbers=[1, 2, 3, 4, 5])
            for i in range(1, 6)
        ]
        saved = await service.save_draws_batch(records)
        assert len(saved) == 5
        count = len(await service.get_draws("dlt"))
        assert count == 5
