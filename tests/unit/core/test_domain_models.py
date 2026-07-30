"""Tests for domain data models."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import pytest

from core.types.models import (
    LotteryGameData,
    DrawRecordData,
    DrawStatistics,
)


class TestLotteryGameData:
    def test_create_valid_game(self) -> None:
        game = LotteryGameData(code="dlt", name="大乐透", region="CN")
        assert game.code == "dlt"
        assert game.name == "大乐透"

    def test_game_to_dict(self) -> None:
        game = LotteryGameData(code="ssq", name="双色球")
        d = game.to_dict()
        assert d["code"] == "ssq"
        assert d["name"] == "双色球"
        assert "id" in d

    def test_game_default_region(self) -> None:
        game = LotteryGameData(code="test", name="Test")
        assert game.region == "CN"

    def test_game_with_full_data(self) -> None:
        game = LotteryGameData(
            code="dlt", name="大乐透", region="CN",
            main_range={"min": 1, "max": 35, "count": 5},
            bonus_range={"min": 1, "max": 12, "count": 2},
            draw_schedule="Mon,Wed,Sat",
        )
        assert game.main_range["max"] == 35


class TestDrawRecordData:
    def test_create_valid_draw(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt",
            draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5],
            bonus_numbers=[6, 7],
        )
        assert draw.lottery_code == "dlt"
        assert draw.draw_number == "24001"

    def test_validate_main_numbers_valid(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[5, 12, 18, 25, 30],
        )
        assert draw.validate_main_numbers(1, 35, 5) is True

    def test_validate_main_numbers_wrong_count(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[5, 12, 18, 25],
        )
        assert draw.validate_main_numbers(1, 35, 5) is False

    def test_validate_main_numbers_out_of_range(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[5, 12, 18, 25, 99],
        )
        assert draw.validate_main_numbers(1, 35, 5) is False

    def test_validate_bonus_numbers_valid(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5],
            bonus_numbers=[6, 7],
        )
        assert draw.validate_bonus_numbers(1, 12, 2) is True

    def test_validate_bonus_numbers_none(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5],
        )
        assert draw.validate_bonus_numbers(1, 12, 2) is True

    def test_draw_with_no_bonus(self) -> None:
        draw = DrawRecordData(
            lottery_code="ssq", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5, 6],
        )
        assert draw.bonus_numbers is None

    def test_draw_to_dict(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5],
        )
        d = draw.to_dict()
        assert isinstance(d["draw_date"], str)
        assert d["draw_date"] == "2024-01-01"

    def test_draw_with_pool_amount(self) -> None:
        draw = DrawRecordData(
            lottery_code="dlt", draw_number="24001",
            draw_date=date(2024, 1, 1),
            main_numbers=[1, 2, 3, 4, 5],
            pool_amount=Decimal("1000000.00"),
        )
        assert draw.pool_amount == Decimal("1000000.00")


class TestDrawStatistics:
    def test_create_statistics(self) -> None:
        stats = DrawStatistics(
            lottery_code="dlt",
            total_draws=100,
            earliest_date="2024-01-01",
            latest_date="2024-07-28",
        )
        assert stats.lottery_code == "dlt"
        assert stats.total_draws == 100

    def test_statistics_to_dict(self) -> None:
        stats = DrawStatistics(
            lottery_code="dlt", total_draws=50,
        )
        d = stats.to_dict()
        assert d["lottery_code"] == "dlt"
        assert d["total_draws"] == 50
