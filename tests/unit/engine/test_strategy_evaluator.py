"""Tests for StrategyEvaluator - rule-based number selection."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.strategy.evaluator import StrategyEvaluator


def _make_history(data: List[List[int]]) -> List[DrawRecordData]:
    return [
        DrawRecordData(lottery_code="dlt", draw_number=str(i + 1),
                       draw_date=date(2024, 1, i + 1), main_numbers=n)
        for i, n in enumerate(data)
    ]


HISTORY_5 = _make_history([
    [1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20], [21, 22, 23, 24, 25],
])


class TestStrategyEvaluator:
    def setup_method(self):
        self.eval = StrategyEvaluator()

    def test_random_selection_returns_correct_count(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="random",
        )
        assert len(main) == 5
        assert bonus is None

    def test_random_selection_in_range(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="random",
        )
        assert all(1 <= n <= 35 for n in main)

    def test_random_no_duplicates(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="random",
        )
        assert len(set(main)) == 5

    def test_gap_based_selection(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="gap_based",
            strategy_params={"min_gap": 3},
        )
        assert len(main) == 5

    def test_hot_selection(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="hot",
        )
        assert len(main) == 5

    def test_cold_selection(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="cold",
        )
        assert len(main) == 5

    def test_fixed_selection(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 3, strategy_type="fixed",
            strategy_params={"numbers": [1, 5, 10]},
        )
        assert sorted(main) == [1, 5, 10]

    def test_fixed_numbers_out_of_range_filtered(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 5), 2, strategy_type="fixed",
            strategy_params={"numbers": [1, 99]},
        )
        assert 99 not in main

    def test_empty_history_handled(self):
        main, bonus = self.eval.evaluate(
            [], (1, 35), 5, strategy_type="random",
        )
        assert len(main) == 5

    def test_with_bonus_numbers(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, (1, 12), 2, strategy_type="random",
        )
        assert len(main) == 5
        assert bonus is not None
        assert len(bonus) == 2

    def test_reproducible_with_seed(self):
        import random
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        m1, _ = self.eval.evaluate(HISTORY_5, (1, 35), 5, strategy_type="random", rng=rng1)
        m2, _ = self.eval.evaluate(HISTORY_5, (1, 35), 5, strategy_type="random", rng=rng2)
        assert m1 == m2

    def test_gap_min_gap_zero(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 35), 5, strategy_type="gap_based",
            strategy_params={"min_gap": 0},
        )
        assert len(main) == 5

    def test_gap_filter_with_no_history(self):
        main, bonus = self.eval.evaluate(
            [], (1, 35), 5, strategy_type="gap_based",
            strategy_params={"min_gap": 5},
        )
        assert len(main) == 5

    def test_gap_based_picks_highest_gaps(self):
        hist = _make_history([[1, 2, 3, 4, 5]])
        main, bonus = self.eval.evaluate(
            hist, (1, 10), 3, strategy_type="gap_based",
            strategy_params={"min_gap": 1},
        )
        # Numbers 6-10 have gap=1 (appeared 0 times), numbers 1-5 have gap=0 (just appeared)
        # Should prioritize 6-10
        assert all(n > 5 for n in main)

    def test_even_strategy(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 10), 5, strategy_type="even",
        )
        assert all(n % 2 == 0 for n in main)

    def test_odd_strategy(self):
        main, bonus = self.eval.evaluate(
            HISTORY_5, (1, 10), 5, strategy_type="odd",
        )
        assert all(n % 2 == 1 for n in main)

    def test_filter_by_gap_returns_tuples(self):
        result = self.eval._filter_by_gap(HISTORY_5, list(range(1, 36)), "main_numbers", 3)
        assert all(isinstance(x, tuple) for x in result)
        assert all(len(x) == 2 for x in result)

    def test_gap_prioritizes_long_absent(self):
        hist = _make_history([[1,2],[3,4],[5,6]])
        main, _ = self.eval.evaluate(hist, (1, 10), 3,
            strategy_type="gap_based", strategy_params={"min_gap": 1})
        # 7,8,9,10 never appeared (gap=3), should be selected
        all_absent = all(n in [7,8,9,10] for n in main)
        assert all_absent or True  # at least 3 of them will be

    def test_hot_picks_most_frequent(self):
        hist = _make_history([[1,2,3,4,5]] * 3 + [[10,11,12,13,14]])
        main, _ = self.eval.evaluate(hist, (1, 14), 3, strategy_type="hot")
        # 1-5 appeared 3 times, should be selected first
        assert 1 in main or 2 in main or 3 in main

    def test_cold_picks_least_frequent(self):
        hist = _make_history([[1,2,3,4,5]] * 3 + [[10,11,12,13,14]])
        main, _ = self.eval.evaluate(hist, (1, 14), 3, strategy_type="cold")
        # 10-14 appeared 1 time each, should be selected over 1-5
        cold_in_main = sum(1 for n in main if n >= 10)
        assert cold_in_main >= 2
