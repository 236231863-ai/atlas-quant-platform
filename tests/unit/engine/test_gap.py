"""Tests for Gap Analysis Engine."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.analysis.calculators.gap import gap_analysis


def _make_draws(data: List[Dict[str, Any]]) -> List[DrawRecordData]:
    return [
        DrawRecordData(
            lottery_code="test",
            draw_number=str(i),
            draw_date=date(2024, 1, i + 1),
            main_numbers=d["main"],
            bonus_numbers=d.get("bonus"),
        )
        for i, d in enumerate(data)
    ]


DRAWS_ORDERED = _make_draws([
    {"main": [1, 2, 3, 10, 20, 30]},
    {"main": [4, 5, 6, 10, 21, 31]},
    {"main": [7, 8, 9, 10, 22, 32]},
    {"main": [1, 11, 12, 20, 23, 33]},
    {"main": [2, 13, 14, 10, 24, 34]},
])

BONUS_DRAWS = _make_draws([
    {"main": [1, 2, 3, 4, 5], "bonus": [1, 7]},
    {"main": [6, 7, 8, 9, 10], "bonus": [2, 8]},
    {"main": [11, 12, 13, 14, 15], "bonus": [1, 9]},
])


class TestGapAnalysis:
    def test_empty_draws(self):
        result = gap_analysis([], (1, 10))
        assert result["total_draws"] == 0

    def test_current_gap_for_appearing_number(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        # Number 10 appears in draws 0, 1, 2, 4 -> last at index 4, total draws = 5
        # Current gap = 5 - 1 - 4 = 0 (appeared in last draw)
        assert result["main_numbers"]["numbers"]["10"]["current_gap"] == 0

    def test_current_gap_for_missing_number(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        # Number 33 appears only at index 3, last at index 3, total draws = 5
        # Current gap = 5 - 1 - 3 = 1
        assert result["main_numbers"]["numbers"]["33"]["current_gap"] == 1

    def test_gap_for_never_appeared_number(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        assert result["main_numbers"]["numbers"]["35"]["current_gap"] == 5

    def test_average_gap(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        avg = result["main_numbers"]["numbers"]["10"]["average_gap"]
        assert avg > 0

    def test_appearances_count(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        assert result["main_numbers"]["numbers"]["1"]["appearances"] == 2
        assert result["main_numbers"]["numbers"]["35"]["appearances"] == 0

    def test_current_max_gap(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        assert result["main_numbers"]["current_max_gap"] > 0

    def test_current_avg_gap(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        assert result["main_numbers"]["current_avg_gap"] > 0

    def test_top_missing_returned(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        assert len(result["main_numbers"]["top_missing"]) == 10

    def test_top_missing_sorted_by_gap(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        tm = result["main_numbers"]["top_missing"]
        for i in range(len(tm) - 1):
            assert tm[i]["current_gap"] >= tm[i + 1]["current_gap"]

    def test_with_bonus_numbers(self):
        result = gap_analysis(BONUS_DRAWS, (1, 15), (1, 10))
        assert result["bonus_numbers"] is not None
        assert "numbers" in result["bonus_numbers"]

    def test_no_bonus_when_not_provided(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 35))
        assert result["bonus_numbers"] is None

    def test_single_draw(self):
        draws = _make_draws([{"main": [1, 2, 3, 4, 5]}])
        result = gap_analysis(draws, (1, 10))
        assert result["total_draws"] == 1

    def test_range_size(self):
        result = gap_analysis(DRAWS_ORDERED, (1, 33))
        assert result["main_numbers"]["range"]["size"] == 33
