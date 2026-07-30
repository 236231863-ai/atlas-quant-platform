"""Tests for engine/analysis/__init__.py integration."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.analysis import calculate_frequency, calculate_gap, calculate_distribution


def _make_draws(data: List[Dict[str, Any]]) -> List[DrawRecordData]:
    return [
        DrawRecordData(lottery_code="test", draw_number=str(i),
                       draw_date=date(2024, 1, i + 1), main_numbers=d["main"],
                       bonus_numbers=d.get("bonus"))
        for i, d in enumerate(data)
    ]


class TestAnalysisModule:
    def test_calculate_frequency_basic(self):
        draws = _make_draws([{"main": [1, 2, 3, 4, 5, 6]}])
        result = calculate_frequency(draws, (1, 33))
        assert result["analysis_type"] == "frequency"
        assert result["total_draws"] == 1

    def test_calculate_frequency_with_bonus(self):
        draws = _make_draws([{"main": [1, 2, 3, 4, 5], "bonus": [1, 2]}])
        result = calculate_frequency(draws, (1, 35), (1, 12))
        assert result["bonus_numbers"] is not None

    def test_calculate_gap_basic(self):
        draws = _make_draws([{"main": [1, 2, 3, 4, 5, 6]}])
        result = calculate_gap(draws, (1, 33))
        assert result["analysis_type"] == "gap"
        assert result["total_draws"] == 1

    def test_calculate_distribution_basic(self):
        draws = _make_draws([{"main": [1, 3, 5, 7, 9, 11]}])
        result = calculate_distribution(draws, (1, 33))
        assert result["analysis_type"] == "distribution"
        assert result["total_draws"] == 1

    def test_all_engines_handle_empty(self):
        result_f = calculate_frequency([], (1, 33))
        result_g = calculate_gap([], (1, 33))
        result_d = calculate_distribution([], (1, 33))
        assert result_f["total_draws"] == 0
        assert result_g["total_draws"] == 0
        assert result_d["total_draws"] == 0
