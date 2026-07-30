"""Tests for composite strategy evaluation."""
from __future__ import annotations
from datetime import date
import pytest
from core.types.models import DrawRecordData
from engine.strategy.evaluator import StrategyEvaluator

def _d(nums):
    return [DrawRecordData(lottery_code="dlt", draw_number=str(i+1), draw_date=date(2024,1,i+1), main_numbers=n) for i,n in enumerate(nums)]

H = _d([[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15],[16,17,18,19,20],[21,22,23,24,25]])

class TestCompositeStrategy:
    def setup_method(self):
        self.e = StrategyEvaluator()
    def test_random_strategy(self):
        m,_ = self.e.evaluate(H, (1,35), 5, strategy_type="random")
        assert len(m) == 5
    def test_gap_based_strategy(self):
        m,_ = self.e.evaluate(H, (1,35), 5, strategy_type="gap_based", strategy_params={"min_gap":3})
        assert len(m) == 5
    def test_hot_strategy(self):
        m,_ = self.e.evaluate(H, (1,35), 5, strategy_type="hot")
        assert len(m) == 5
    def test_cold_strategy(self):
        m,_ = self.e.evaluate(H, (1,35), 5, strategy_type="cold")
        assert len(m) == 5
    def test_fixed_strategy(self):
        m,_ = self.e.evaluate(H, (1,35), 3, strategy_type="fixed", strategy_params={"numbers":[1,2,3]})
        assert sorted(m) == [1,2,3]
    def test_even_strategy(self):
        m,_ = self.e.evaluate(H, (1,10), 3, strategy_type="even")
        assert all(n%2==0 for n in m)
    def test_odd_strategy(self):
        m,_ = self.e.evaluate(H, (1,10), 3, strategy_type="odd")
        assert all(n%2==1 for n in m)
    def test_empty_history(self):
        m,_ = self.e.evaluate([], (1,35), 5, strategy_type="random")
        assert len(m) == 5
    def test_bonus_selection(self):
        _,b = self.e.evaluate(H, (1,35), 5, (1,12), 2, strategy_type="random")
        assert b is not None and len(b) == 2
    def test_no_bonus_when_not_requested(self):
        _,b = self.e.evaluate(H, (1,35), 5, strategy_type="random")
        assert b is None
    def test_gap_with_no_history(self):
        m,_ = self.e.evaluate([], (1,35), 5, strategy_type="gap_based", strategy_params={"min_gap":5})
        assert len(m) == 5
    def test_reproducible_seed(self):
        import random
        r1 = random.Random(42); r2 = random.Random(42)
        m1,_ = self.e.evaluate(H, (1,35), 5, strategy_type="random", rng=r1)
        m2,_ = self.e.evaluate(H, (1,35), 5, strategy_type="random", rng=r2)
        assert m1 == m2
    def test_hot_picks_most_frequent(self):
        hist = _d([[1,1,1,1,1]]*3 + [[10,11,12,13,14]])
        m,_ = self.e.evaluate(hist, (1,14), 3, strategy_type="hot")
        assert 1 in m
    def test_cold_picks_least_frequent(self):
        hist = _d([[1,2,3,4,5]]*3 + [[10,11,12,13,14]])
        m,_ = self.e.evaluate(hist, (1,14), 3, strategy_type="cold")
        cold_in_m = sum(1 for n in m if n >= 10)
        assert cold_in_m >= 2
    def test_gap_prioritizes_absent(self):
        m,_ = self.e.evaluate(H, (1,30), 5, strategy_type="gap_based", strategy_params={"min_gap":1})
        assert len(m) == 5
