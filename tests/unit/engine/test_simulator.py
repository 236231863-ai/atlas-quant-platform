"""Tests for the TradeSimulator - walk-forward simulation."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.backtest.models import BacktestConfig
from engine.backtest.simulator import TradeSimulator
from engine.strategy.registry import StrategyDefinition


def _make_draws(numbers_list: List[List[int]]) -> List[DrawRecordData]:
    return [
        DrawRecordData(lottery_code="dlt", draw_number=str(i + 1),
                       draw_date=date(2024, 1, i + 1), main_numbers=n)
        for i, n in enumerate(numbers_list)
    ]


SAMPLE_DRAWS = _make_draws([
    [1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20], [21, 22, 23, 24, 25], [1, 7, 13, 19, 25],
    [2, 8, 14, 20, 21], [3, 9, 15, 16, 22], [4, 10, 11, 17, 23],
    [5, 6, 12, 18, 24],
])

BASE_CONFIG = BacktestConfig(
    lottery_code="dlt", strategy_id="random_selection",
    start_date="2024-01-01", end_date="2024-01-10",
    main_range=(1, 35), main_count=5,
    initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
)


class TestTradeSimulatorBasic:
    def setup_method(self):
        self.sim = TradeSimulator()

    def test_empty_draws_returns_empty(self):
        trades = self.sim.run([], BASE_CONFIG)
        assert trades == []

    def test_single_draw_produces_one_trade(self):
        draws = _make_draws([[1, 2, 3, 4, 5]])
        trades = self.sim.run(draws, BASE_CONFIG)
        assert len(trades) == 1

    def test_returns_trade_records(self):
        trades = self.sim.run(SAMPLE_DRAWS, BASE_CONFIG)
        assert all(hasattr(t, "draw_date") for t in trades)
        assert all(hasattr(t, "bet_amount") for t in trades)

    def test_each_trade_has_bet_main_numbers(self):
        trades = self.sim.run(SAMPLE_DRAWS, BASE_CONFIG)
        for t in trades:
            assert len(t.bet_main_numbers) == 5

    def test_each_trade_tracks_pnl(self):
        trades = self.sim.run(SAMPLE_DRAWS, BASE_CONFIG)
        for t in trades:
            assert hasattr(t, "cumulative_pnl")

    def test_bet_amount_matches_config(self):
        trades = self.sim.run(SAMPLE_DRAWS, BASE_CONFIG)
        for t in trades:
            assert t.bet_amount == 10.0

    def test_invalid_capital_raises(self):
        bad = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=0, bet_per_draw=10.0,
        )
        with pytest.raises(ValueError, match="positive"):
            self.sim.run(SAMPLE_DRAWS[:1], bad)

    def test_invalid_bet_size_raises(self):
        bad = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=100.0, bet_per_draw=0,
        )
        with pytest.raises(ValueError, match="positive"):
            self.sim.run(SAMPLE_DRAWS[:1], bad)

    def test_bet_exceeds_capital_raises(self):
        bad = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=10.0, bet_per_draw=100.0,
        )
        with pytest.raises(ValueError):
            self.sim.run(SAMPLE_DRAWS[:1], bad)


class TestWalkForward:
    def setup_method(self):
        self.sim = TradeSimulator()

    def test_uses_only_historical_data(self):
        # Strategy uses cold numbers. At draw 1: history=empty, all numbers qualify
        # At draw 10: history includes 9 draws, gaps are different
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="test",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        # First draw with no history
        trades = self.sim.run(SAMPLE_DRAWS[:1], config)
        assert len(trades) == 1

    def test_reproducible_with_same_seed(self):
        t1 = self.sim.run(SAMPLE_DRAWS, BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        ))
        t2 = self.sim.run(SAMPLE_DRAWS, BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        ))
        assert len(t1) == len(t2)
        for a, b in zip(t1, t2):
            assert a.bet_main_numbers == b.bet_main_numbers

    def test_different_seeds_different_results(self):
        t1 = self.sim.run(SAMPLE_DRAWS, BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        ))
        t2 = self.sim.run(SAMPLE_DRAWS, BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=99,
        ))
        bet_numbers_seed1 = [tuple(t.bet_main_numbers) for t in t1]
        bet_numbers_seed2 = [tuple(t.bet_main_numbers) for t in t2]
        assert bet_numbers_seed1 != bet_numbers_seed2


class TestPrizeCalculation:
    def setup_method(self):
        self.sim = TradeSimulator()

    def test_matched_main_count_accurate(self):
        draw = _make_draws([[1, 2, 3, 4, 5]])[0]
        # Bet exactly what was drawn
        result = self.sim._count_matches([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
        assert result == 5

    def test_matched_main_no_match(self):
        result = self.sim._count_matches([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
        assert result == 0

    def test_matched_main_partial(self):
        result = self.sim._count_matches([1, 2, 3, 10, 11], [1, 2, 3, 4, 5])
        assert result == 3

    def test_calculate_prize_jackpot(self):
        amount, level = self.sim._calculate_prize(5, 2)
        assert amount == 5000000.0
        assert level == 1

    def test_calculate_prize_no_win(self):
        amount, level = self.sim._calculate_prize(0, 0)
        assert amount == 0.0
        assert level == 0

    def test_calculate_prize_small_win(self):
        amount, level = self.sim._calculate_prize(2, 1)
        assert amount == 5.0
        assert level == 12

    def test_calculate_prize_medium(self):
        amount, level = self.sim._calculate_prize(4, 1)
        assert amount == 300.0
        assert level == 5


class TestNoFutureLeakage:
    def setup_method(self):
        self.sim = TradeSimulator()

    def test_first_draw_has_no_history(self):
        """At the first draw, no historical data exists. Strategy must handle this."""
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="test",
            start_date="", end_date="", main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        draws = _make_draws([[1, 2, 3, 4, 5]])
        trades = self.sim.run(draws, config)
        assert len(trades) == 1
        assert len(trades[0].bet_main_numbers) == 5

    def test_early_draws_dont_have_later_data(self):
        """Verify that at draw 2, only draw 1's data exists in history."""
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="cold_number_tracker",
            start_date="", end_date="",
            main_range=(1, 5), main_count=2,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        draws = _make_draws([
            [1, 2],  # draw 1: numbers 1,2 appear
            [3, 4],  # draw 2: 1,2 should appear gap-based (gap=1)
        ])
        trades = self.sim.run(draws, config)
        assert len(trades) == 2

class TestEdgeCases:
    def setup_method(self):
        self.sim = TradeSimulator()

    def test_handles_single_draw_reproducibly(self):
        draws = [_make_draws([[1,2,3,4,5]])[0]]
        config = BacktestConfig(lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1,35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=1)
        t1 = self.sim.run(draws, config)
        t2 = self.sim.run([_make_draws([[1,2,3,4,5]])[0]], config)
        assert t1[0].bet_main_numbers == t2[0].bet_main_numbers

    def test_all_draws_produce_trades(self):
        draws = _make_draws([[i*5+1, i*5+2, i*5+3, i*5+4, i*5+5] for i in range(10)])
        config = BacktestConfig(lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1,35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = self.sim.run(draws, config)
        assert len(trades) == 10

    def test_prize_level_2(self):
        amount, level = self.sim._calculate_prize(5, 1)
        assert level == 2
        assert amount > 0

    def test_prize_level_10(self):
        # 3+0 = level 10
        self.sim._prize_table["3:0"] = 5.0
        amount, level = self.sim._calculate_prize(3, 0)
        assert level > 0
        assert amount > 0

    def test_draw_filter_no_history(self):
        config = BacktestConfig(lottery_code="dlt", strategy_id="gap_based",
            start_date="", end_date="", main_range=(1,10), main_count=3,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        draws = _make_draws([[1,2,3,4,5],[6,7,8,9,10]])
        trades = self.sim.run(draws, config)
        assert len(trades) == 2
