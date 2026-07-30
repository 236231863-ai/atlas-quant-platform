"""Tests for Distribution Analysis Engine."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.analysis.calculators.distribution import distribution_analysis


def _make_draws(data: List[Dict[str, Any]]) -> List[DrawRecordData]:
    return [
        DrawRecordData(lottery_code="test", draw_number=str(i),
                       draw_date=date(2024, 1, i + 1), main_numbers=d)
        for i, d in enumerate(data)
    ]


DRAWS_ODD_EVEN = _make_draws([
    [1, 3, 5, 7, 9, 11],     # 6:0 odd:even
    [2, 4, 6, 8, 10, 12],    # 0:6 odd:even
    [1, 2, 3, 4, 5, 6],      # 3:3 odd:even
    [1, 3, 5, 2, 4, 7],      # 4:2 odd:even
    [2, 4, 6, 1, 3, 8],      # 3:3 odd:even
])


class TestDistributionAnalysis:
    def test_empty_draws(self):
        result = distribution_analysis([], (1, 33))
        assert result["total_draws"] == 0

    def test_odd_even_distribution(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        oe = result["odd_even"]["distribution"]
        assert "6:0" in oe
        assert "0:6" in oe
        assert "3:3" in oe

    def test_odd_even_percentages(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        pct = result["odd_even"]["percentages"]
        assert pct["3:3"] == 40.0  # 2 out of 5

    def test_odd_even_current(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        assert result["odd_even"]["current"] == "3:3"

    def test_odd_even_most_common(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        assert result["odd_even"]["most_common"] == "3:3"

    def test_high_low_distribution(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        assert "distribution" in result["high_low"]

    def test_high_low_midpoint(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        assert result["high_low"]["midpoint"] == 17.0

    def test_zone_distribution_has_zones(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        zones = result["zone_distribution"]
        assert "low" in zones
        assert "medium" in zones
        assert "high" in zones

    def test_zone_ranges_correct(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        low = result["zone_distribution"]["low"]
        assert low["range"]["min"] == 1
        assert low["range"]["max"] == 10

    def test_sum_values_has_stats(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        sv = result["sum_values"]
        assert "mean" in sv
        assert "median" in sv
        assert "min" in sv
        assert "max" in sv

    def test_sum_values_correct(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        # Draw sums: 36, 42, 21, 22, 24
        assert result["sum_values"]["min"] == 21
        assert result["sum_values"]["max"] == 42

    def test_span_values_has_stats(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        sp = result["span_values"]
        assert "mean" in sp
        assert "current" in sp

    def test_span_values_correct(self):
        draws = _make_draws([[1, 2, 3, 4, 5, 33]])
        result = distribution_analysis(draws, (1, 33))
        assert result["span_values"]["current"] == 32

    def test_recent_10_in_sum(self):
        result = distribution_analysis(DRAWS_ODD_EVEN, (1, 33))
        assert len(result["sum_values"]["recent_10"]) <= 10

    def test_single_draw(self):
        draws = _make_draws([[5, 10, 15, 20, 25, 30]])
        result = distribution_analysis(draws, (1, 33))
        assert result["total_draws"] == 1
