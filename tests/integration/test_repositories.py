"""Integration tests for database repositories."""
from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from backend.database.models import LotteryGame, DrawRecord
from backend.database.repositories import (
    LotteryGameRepository,
    DrawRecordRepository,
)


pytestmark = pytest.mark.integration


class TestLotteryGameRepository:
    async def test_save_and_find_by_code(self, game_repo, sample_game):
        saved = await game_repo.save(sample_game)
        found = await game_repo.find_by_code("dlt")
        assert found is not None
        assert found.name == "大乐透"

    async def test_save_and_find_by_id(self, game_repo, sample_game):
        saved = await game_repo.save(sample_game)
        found = await game_repo.find_by_id(saved.id)
        assert found is not None
        assert found.code == "dlt"

    async def test_list_all_returns_games(self, game_repo, sample_game):
        await game_repo.save(sample_game)
        games = await game_repo.list_all()
        assert len(games) >= 1

    async def test_count_games(self, game_repo, sample_game):
        await game_repo.save(sample_game)
        count = await game_repo.count()
        assert count >= 1

    async def test_upsert_existing_game(self, game_repo, sample_game):
        saved = await game_repo.save(sample_game)
        game2 = LotteryGame(
            code="dlt", name="大乐透更新版", region="CN",
            main_range={"min": 1, "max": 35, "count": 5},
        )
        result = await game_repo.upsert_by_code(game2)
        assert result.name == "大乐透更新版"

    async def test_find_by_code_not_found(self, game_repo):
        result = await game_repo.find_by_code("nonexistent")
        assert result is None

    async def test_find_by_id_not_found(self, game_repo):
        result = await game_repo.find_by_id("nonexistent-id")
        assert result is None


class TestDrawRecordRepository:
    async def test_save_and_find_by_id(self, draw_repo, sample_draw):
        saved = await draw_repo.save(sample_draw)
        found = await draw_repo.find_by_id(saved.id)
        assert found is not None
        assert found.draw_number == "24001"

    async def test_find_by_lottery_and_number(self, draw_repo, sample_draw):
        await draw_repo.save(sample_draw)
        found = await draw_repo.find_by_lottery_and_number("dlt", "24001")
        assert found is not None
        assert found.draw_date == date(2024, 1, 1)

    async def test_find_by_lottery_and_number_not_found(self, draw_repo):
        result = await draw_repo.find_by_lottery_and_number("dlt", "99999")
        assert result is None

    async def test_find_latest(self, draw_repo, sample_draws):
        await draw_repo.save_many(sample_draws)
        latest = await draw_repo.find_latest("dlt", 1)
        assert len(latest) == 1
        assert latest[0].draw_number == "24010"

    async def test_find_latest_multiple(self, draw_repo, sample_draws):
        await draw_repo.save_many(sample_draws)
        latest = await draw_repo.find_latest("dlt", 3)
        assert len(latest) == 3

    async def test_count_by_lottery(self, draw_repo, sample_draws):
        await draw_repo.save_many(sample_draws)
        count = await draw_repo.count_by_lottery("dlt")
        assert count == 10

    async def test_save_many_records(self, draw_repo, sample_draws):
        saved = await draw_repo.save_many(sample_draws)
        assert len(saved) == 10

    async def test_exists_by_lottery_and_number(self, draw_repo, sample_draw):
        await draw_repo.save(sample_draw)
        exists = await draw_repo.exists_by_lottery_and_number("dlt", "24001")
        assert exists is True

    async def test_not_exists_by_lottery_and_number(self, draw_repo):
        exists = await draw_repo.exists_by_lottery_and_number("dlt", "99999")
        assert exists is False

    async def test_get_statistics(self, draw_repo, sample_draws):
        await draw_repo.save_many(sample_draws)
        stats = await draw_repo.get_statistics("dlt")
        assert stats["lottery_code"] == "dlt"
        assert stats["total_draws"] == 10
        assert stats["latest_draw_number"] is not None
