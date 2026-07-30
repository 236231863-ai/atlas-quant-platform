"""Tests for Frequency Analysis Engine."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.analysis.calculators.frequency import frequency_analysis


def _make_draws(data: List[Dict[str, Any]]) -> List[DrawRecordData]:
    """Helper to create test draws."""
    return [
        DrawRecordData(
            lottery_code=d.get("code", "test"),
            draw_number=d.get("number", str(i)),
            draw_date=d.get("date", date(2024, 1, i + 1)),
            main_numbers=d["main"],
            bonus_numbers=d.get("bonus"),
        )
        for i, d in enumerate(data)
    ]


DRAWS_6_33 = _make_draws([
    {"main": [1, 2, 3, 4, 5, 6]},
    {"main": [1, 2, 3, 7, 8, 9]},
    {"main": [1, 2, 10, 11, 12, 13]},
    {"main": [14, 15, 16, 17, 18, 19]},
    {"main": [20, 21, 22, 23, 24, 25]},
])

DRAWS_WITH_BONUS = _make_draws([
    {"main": [1, 2, 3, 4, 5], "bonus": [1, 2]},
    {"main": [1, 2, 3, 4, 6], "bonus": [3, 4]},
    {"main": [7, 8, 9, 10, 11], "bonus": [1, 5]},
])


class TestFrequencyAnalysis:
    def test_empty_draws(self):
        result = frequency_analysis([], (1, 33))
        assert result["total_draws"] == 0
        assert result["main_numbers"]["frequencies"] == {}

    def test_single_draw(self):
        draws = _make_draws([{"main": [1, 2, 3, 4, 5, 6]}])
        result = frequency_analysis(draws, (1, 33))
        assert result["total_draws"] == 1
        assert result["main_numbers"]["frequencies"]["1"] == 1
        assert result["main_numbers"]["frequencies"]["7"] == 0

    def test_counts_occurrences_correctly(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        assert result["main_numbers"]["frequencies"]["1"] == 3
        assert result["main_numbers"]["frequencies"]["2"] == 3
        assert result["main_numbers"]["frequencies"]["14"] == 1

    def test_range_bounds(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        r = result["main_numbers"]["range"]
        assert r["min"] == 1
        assert r["max"] == 33
        assert r["size"] == 33

    def test_total_occurrences(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        assert result["main_numbers"]["total_occurrences"] == 30  # 5 draws * 6 numbers

    def test_hot_numbers_found(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        hot = result["main_numbers"]["hot_numbers"]
        assert len(hot) == 5
        assert hot[0]["number"] in [1, 2]  # 1 and 2 appear 3 times each

    def test_cold_numbers_found(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        cold = result["main_numbers"]["cold_numbers"]
        assert len(cold) == 5

    def test_chi_square_computed(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        cs = result["main_numbers"]["chi_square"]
        assert cs is not None
        assert "statistic" in cs
        assert "p_value" in cs
        assert "significant" in cs

    def test_analysis_type(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        assert result["analysis_type"] == "frequency"

    def test_with_bonus_numbers(self):
        result = frequency_analysis(DRAWS_WITH_BONUS, (1, 11), (1, 5))
        assert result["bonus_numbers"] is not None
        assert result["bonus_numbers"]["frequencies"]["1"] == 2

    def test_bonus_range_none_when_not_provided(self):
        result = frequency_analysis(DRAWS_WITH_BONUS, (1, 11))
        assert result["bonus_numbers"] is None

    def test_expected_per_number(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        epn = result["main_numbers"]["expected_per_number"]
        assert epn > 0

    def test_sorted_by_frequency(self):
        result = frequency_analysis(DRAWS_6_33, (1, 33))
        sf = result["main_numbers"]["sorted_by_frequency"]
        assert sf[0][1] >= sf[1][1]  # descending order

    def test_large_range_boundary(self):
        draws = _make_draws([{"main": [50, 60, 70, 80, 90, 99]}])
        result = frequency_analysis(draws, (1, 99))
        assert result["main_numbers"]["frequencies"]["50"] == 1
        assert result["main_numbers"]["frequencies"]["1"] == 0
