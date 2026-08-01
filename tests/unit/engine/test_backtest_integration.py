"""Integration tests for the full backtest pipeline."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from core.types.models import DrawRecordData
from engine.backtest.models import BacktestConfig, BacktestMetrics, TradeRecord
from engine.backtest.simulator import TradeSimulator
from engine.backtest.analyzers import ResultAggregator
from engine.strategy.registry import StrategyRegistry, StrategyDefinition
from engine.strategy.evaluator import StrategyEvaluator
from engine.report import ReportGenerator


def _make_draws(count: int = 20) -> List[DrawRecordData]:
    return [
        DrawRecordData(lottery_code="dlt", draw_number=str(i + 1),
                       draw_date=date(2024, 1, i + 1),
                       main_numbers=[(i % 35) + 1 for _ in range(5)])
        for i in range(count)
    ]


class TestFullPipeline:
    def setup_method(self):
        self.sim = TradeSimulator()
        self.agg = ResultAggregator()
        self.report = ReportGenerator()

    def test_random_strategy_pipeline(self):
        draws = _make_draws(10)
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        trades = self.sim.run(draws, config)
        metrics = self.agg.analyze(trades)
        assert len(trades) == 10
        assert metrics.total_bets == 10

    def test_cold_strategy_pipeline(self):
        draws = _make_draws(15)
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="cold",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        trades = self.sim.run(draws, config)
        assert len(trades) > 0

    def test_metrics_computed(self):
        draws = _make_draws(10)
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        trades = self.sim.run(draws, config)
        metrics = self.agg.analyze(trades)
        assert metrics.roi is not None
        assert metrics.win_rate is not None
        assert metrics.sharpe_ratio is not None
        assert metrics.max_drawdown_pct is not None

    def test_report_generation_from_pipeline(self):
        draws = _make_draws(10)
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        trades = self.sim.run(draws, config)
        metrics = self.agg.analyze(trades)
        self.report.set_title("Test Backtest")
        md = self.report.generate_backtest_report(metrics, trades, config)
        assert "Backtest Report" in md
        assert "ROI" in md
        assert "Sharpe" in md
        assert "WIN" in md or "LOSS" in md

    def test_disclaimer_in_backtest_report(self):
        draws = _make_draws(5)
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="random",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        trades = self.sim.run(draws, config)
        metrics = self.agg.analyze(trades)
        md = self.report.generate_backtest_report(metrics, trades)
        assert "academic research" in md.lower()
        assert "Does not predict" in md

    def test_strategy_builtin_pipeline(self):
        reg = StrategyRegistry()
        reg.register_builtin()
        cold = reg.get("cold_number_tracker")
        assert cold is not None
        assert cold.strategy_type == "gap_based"

    def test_fixed_strategy_consistent(self):
        draws = _make_draws(5)
        config = BacktestConfig(
            lottery_code="dlt", strategy_id="fixed",
            start_date="", end_date="",
            main_range=(1, 35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42,
        )
        t1 = self.sim.run(draws, config)
        t2 = self.sim.run(draws, config)
        for a, b in zip(t1, t2):
            assert a.bet_main_numbers == b.bet_main_numbers


class TestBacktestReport:
    def setup_method(self):
        self.gen = ReportGenerator()
        self.metrics = BacktestMetrics(
            total_investment=100.0, total_return=50.0, roi=-50.0,
            win_count=3, total_bets=10, win_rate=30.0,
            max_drawdown_amount=30.0, max_drawdown_pct=30.0,
            volatility=0.5, sharpe_ratio=-0.5, avg_return_per_bet=-5.0,
            final_capital=950.0, prize_levels={"1": 1, "5": 2},
            best_single_return=50.0, worst_single_return=-10.0,
            consecutive_losses=4, max_consecutive_losses=5,
        )
        self.trades = [
            TradeRecord(draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
                        bet_main_numbers=[1, 2, 3, 4, 5], actual_main_numbers=[6, 7, 8, 9, 10],
                        bet_amount=10.0, win_amount=0.0, is_win=False, prize_level=0,
                        matched_main=0, matched_bonus=0, cumulative_pnl=-10.0, cumulative_roi=-1.0,
                        bet_bonus_numbers=None, actual_bonus_numbers=None,
                        )
        ]

    def test_backtest_report_contains_metrics(self):
        md = self.gen.generate_backtest_report(self.metrics, self.trades)
        assert "Win Rate" in md
        assert "ROI" in md
        assert "Sharpe" in md

    def test_backtest_report_prize_levels(self):
        md = self.gen.generate_backtest_report(self.metrics, self.trades)
        assert "Prize Level" in md
        assert "1" in md

    def test_backtest_report_trades_table(self):
        md = self.gen.generate_backtest_report(self.metrics, self.trades)
        assert "Recent Trades" in md
        assert "LOSS" in md

    def test_backtest_report_empty_trades(self):
        md = self.gen.generate_backtest_report(self.metrics, [])
        assert "Recent Trades" in md

    def test_all_strategies_produce_trades(self):
        draws = _make_draws(10)
        for strategy in ["random", "gap_based", "hot", "cold"]:
            config = BacktestConfig(lottery_code="dlt", strategy_id=strategy,
                start_date="", end_date="", main_range=(1,35), main_count=5,
                initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
            trades = self.sim.run(draws, config)
            assert len(trades) == 10, f"Strategy {strategy} failed"

    def test_metrics_roi_consistent_with_trades(self):
        draws = _make_draws(10)
        config = BacktestConfig(lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1,35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = self.sim.run(draws, config)
        metrics = self.agg.analyze(trades)
        total_cost = sum(t.bet_amount for t in trades)
        total_won = sum(t.win_amount for t in trades)
        expected_roi = (total_won - total_cost) / total_cost * 100
        assert abs(metrics.roi - expected_roi) < 0.01

    def test_custom_prize_table(self):
        custom = {"5:2": 100.0, "4:1": 10.0}
        sim = TradeSimulator(prize_table=custom)
        amount, level = sim._calculate_prize(5, 2)
        assert amount == 100.0

    def test_strategy_registry_integration(self):
        reg = StrategyRegistry()
        reg.register_builtin()
        strategies = reg.list()
        draws = _make_draws(5)
        for strategy in strategies:
            config = BacktestConfig(lottery_code="dlt", strategy_id=strategy.strategy_id,
                start_date="", end_date="", main_range=(1,35), main_count=5,
                initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
            trades = self.sim.run(draws, config)
            assert len(trades) > 0

    def test_report_without_config(self):
        draws = _make_draws(5)
        config = BacktestConfig(lottery_code="dlt", strategy_id="random",
            start_date="", end_date="", main_range=(1,35), main_count=5,
            initial_capital=1000.0, bet_per_draw=10.0, random_seed=42)
        trades = self.sim.run(draws, config)
        metrics = self.agg.analyze(trades)
        md = self.report.generate_backtest_report(metrics, trades)
        assert "ROI" in md
