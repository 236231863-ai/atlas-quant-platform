"""Tests for DLT data source adapter."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from plugins.dlt.data_source import DltDataSource, DLT_GAME_DEF


SAMPLE_CSV = """draw_number,draw_date,front_1,front_2,front_3,front_4,front_5,back_1,back_2,pool_amount
24001,2024-01-01,5,12,18,25,30,2,7,850000000.00
24002,2024-01-03,3,8,15,22,28,1,9,876000000.00"""


class TestDltGameDefinition:
    def test_game_code_is_dlt(self) -> None:
        assert DLT_GAME_DEF.code == "dlt"

    def test_game_name_is_dlt(self) -> None:
        assert DLT_GAME_DEF.name == "大乐透"

    def test_main_range_config(self) -> None:
        assert DLT_GAME_DEF.main_range == {"min": 1, "max": 35, "count": 5}

    def test_bonus_range_config(self) -> None:
        assert DLT_GAME_DEF.bonus_range == {"min": 1, "max": 12, "count": 2}

    def test_draw_schedule(self) -> None:
        assert DLT_GAME_DEF.draw_schedule == "Mon,Wed,Sat"


class TestDltDataSource:
    def setup_method(self) -> None:
        self.ds = DltDataSource()

    def test_get_game_definition(self) -> None:
        game = self.ds.get_game_definition()
        assert game.code == "dlt"

    def test_parse_single_csv_line(self) -> None:
        row = {
            "draw_number": "24001",
            "draw_date": "2024-01-01",
            "front_1": "5", "front_2": "12", "front_3": "18",
            "front_4": "25", "front_5": "30",
            "back_1": "2", "back_2": "7",
            "pool_amount": "850000000.00",
        }
        record = self.ds.parse_csv_line(row)
        assert record.draw_number == "24001"
        assert record.main_numbers == [5, 12, 18, 25, 30]
        assert record.bonus_numbers == [2, 7]
        assert record.pool_amount == Decimal("850000000.00")

    def test_parse_csv_full(self) -> None:
        records = self.ds.parse_csv(SAMPLE_CSV)
        assert len(records) == 2
        assert records[0].draw_number == "24001"
        assert records[1].draw_number == "24002"

    def test_parse_csv_without_pool(self) -> None:
        csv_data = """draw_number,draw_date,front_1,front_2,front_3,front_4,front_5,back_1,back_2
99999,2024-12-31,1,2,3,4,5,6,7"""
        records = self.ds.parse_csv(csv_data)
        assert len(records) == 1
        assert records[0].pool_amount is None

    def test_parse_csv_line_invalid_numbers_raises(self) -> None:
        row = {
            "draw_number": "99999",
            "draw_date": "2024-01-01",
            "front_1": "1", "front_2": "2", "front_3": "3",
            "front_4": "4", "front_5": "99",
            "back_1": "6", "back_2": "7",
        }
        with pytest.raises(ValueError, match="Invalid numbers"):
            self.ds.parse_csv_line(row)

    def test_validate_numbers_valid(self) -> None:
        assert self.ds.validate_numbers([5, 12, 18, 25, 30], [2, 7]) is True

    def test_validate_numbers_wrong_count(self) -> None:
        assert self.ds.validate_numbers([1, 2, 3, 4], [1, 2]) is False

    def test_validate_numbers_out_of_range(self) -> None:
        assert self.ds.validate_numbers([1, 2, 3, 4, 99], [1, 2]) is False

    def test_validate_numbers_duplicate_main(self) -> None:
        assert self.ds.validate_numbers([1, 1, 2, 3, 4], [1, 2]) is False

    def test_validate_numbers_duplicate_bonus(self) -> None:
        assert self.ds.validate_numbers([1, 2, 3, 4, 5], [1, 1]) is False

    def test_validate_numbers_bonus_out_of_range(self) -> None:
        assert self.ds.validate_numbers([1, 2, 3, 4, 5], [1, 99]) is False

    def test_validate_numbers_no_bonus(self) -> None:
        assert self.ds.validate_numbers([1, 2, 3, 4, 5]) is True
