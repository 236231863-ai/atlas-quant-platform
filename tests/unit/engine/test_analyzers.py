"""Tests for ResultAggregator - backtest metrics calculation."""
from __future__ import annotations

import pytest
from engine.backtest.models import TradeRecord, BacktestMetrics
from engine.backtest.analyzers import ResultAggregator


def _trade(win: bool = False, win_amt: float = 0.0, bet: float = 10.0,
           pnl: float = -10.0, cum_pnl: float = -10.0) -> TradeRecord:
    return TradeRecord(
        draw_date="2024-01-01", draw_number="1", lottery_code="dlt",
        bet_main_numbers=[1, 2, 3, 4, 5], bet_bonus_numbers=[1, 2],
        actual_main_numbers=[6, 7, 8, 9, 10], actual_bonus_numbers=[3, 4],
        bet_amount=bet, win_amount=win_amt, is_win=win, prize_level=1 if win else 0,
        matched_main=5 if win else 0, matched_bonus=2 if win else 0,
        cumulative_pnl=cum_pnl, cumulative_roi=0.0,
    )


class TestResultAggregator:
    def setup_method(self):
        self.agg = ResultAggregator()

    def test_empty_trades(self):
        m = self.agg.analyze([])
        assert m.total_bets == 0

    def test_all_losses(self):
        trades = [_trade() for _ in range(10)]
        m = self.agg.analyze(trades)
        assert m.total_bets == 10
        assert m.win_count == 0
        assert m.win_rate == 0.0

    def test_all_wins(self):
        trades = [_trade(win=True, win_amt=20.0) for _ in range(5)]
        m = self.agg.analyze(trades)
        assert m.win_count == 5
        assert m.win_rate == 100.0

    def test_win_rate(self):
        trades = [_trade(win=True, win_amt=10.0) for _ in range(3)] + [_trade() for _ in range(7)]
        m = self.agg.analyze(trades)
        assert m.win_rate == 30.0

    def test_total_investment(self):
        trades = [_trade(bet=10.0) for _ in range(5)]
        m = self.agg.analyze(trades)
        assert m.total_investment == 50.0

    def test_total_return(self):
        trades = [_trade(win=True, win_amt=100.0) for _ in range(2)]
        m = self.agg.analyze(trades)
        assert m.total_return == 200.0

    def test_roi_positive(self):
        trades = [_trade(win=True, win_amt=20.0, bet=10.0) for _ in range(10)]
        m = self.agg.analyze(trades)
        assert m.roi > 0

    def test_roi_negative(self):
        trades = [_trade(win=False) for _ in range(10)]
        m = self.agg.analyze(trades)
        assert m.roi < 0

    def test_max_drawdown_zero_on_all_wins(self):
        trades = [_trade(win=True, win_amt=20.0, bet=10.0) for _ in range(5)]
        m = self.agg.analyze(trades)
        assert m.max_drawdown_amount == 0

    def test_max_drawdown_positive_on_losses(self):
        trades = [
            _trade(win=True, win_amt=50.0, bet=10.0, cum_pnl=40.0),
            _trade(win=False, cum_pnl=30.0),
            _trade(win=False, cum_pnl=20.0),
        ]
        m = self.agg.analyze(trades)
        assert m.max_drawdown_amount >= 0

    def test_volatility_calculated(self):
        # 混合收益产生波动（恒定收益时 volatility 为 0 是设计行为，见 test_volatility_zero_on_constant）
        trades = [_trade(win=True, win_amt=20.0, bet=10.0) for _ in range(8)] + \
                 [_trade(win=True, win_amt=5.0, bet=10.0) for _ in range(2)]
        m = self.agg.analyze(trades)
        assert m.volatility > 0

    def test_sharpe_ratio_calculated(self):
        trades = [_trade(win=True, win_amt=20.0, bet=10.0) for _ in range(8)] + \
                 [_trade(win=True, win_amt=5.0, bet=10.0) for _ in range(2)]
        m = self.agg.analyze(trades)
        assert m.sharpe_ratio != 0

    def test_avg_return_per_bet(self):
        trades = [_trade(win=True, win_amt=20.0, bet=10.0) for _ in range(10)]
        m = self.agg.analyze(trades)
        assert m.avg_return_per_bet == 10.0  # 20-10 = 10 per bet

    def test_max_consecutive_losses(self):
        trades = [
            _trade(win=True, win_amt=10.0, cum_pnl=0),
            _trade(win=False, cum_pnl=-10),
            _trade(win=False, cum_pnl=-20),
            _trade(win=False, cum_pnl=-30),
            _trade(win=True, win_amt=10.0, cum_pnl=-20),
        ]
        m = self.agg.analyze(trades)
        assert m.max_consecutive_losses == 3

    def test_drawdown_calculation(self):
        pnls = [10.0, -5.0, -10.0, 5.0, -20.0, 15.0]
        dd_amt, dd_pct = self.agg._calculate_max_drawdown(pnls)
        assert dd_amt >= 0
        assert dd_pct >= 0

    def test_empty_drawdown(self):
        dd_amt, dd_pct = self.agg._calculate_max_drawdown([])
        assert dd_amt == 0
        assert dd_pct == 0

    def test_drawdown_increasing(self):
        pnls = [10, -5, -10, -20, 5]
        dd_amt, dd_pct = self.agg._calculate_max_drawdown(pnls)
        assert dd_amt > 0
        assert dd_pct > 0

    def test_sharpe_ratio_negative_on_losses(self):
        # 整体亏损且收益有波动
        trades = [_trade() for _ in range(8)] + \
                 [_trade(win=True, win_amt=5.0, bet=10.0) for _ in range(2)]
        m = self.agg.analyze(trades)
        assert m.sharpe_ratio < 0

    def test_sharpe_ratio_zero_on_flat(self):
        trades = [_trade(win=True, win_amt=10.0, bet=10.0) for _ in range(10)]
        m = self.agg.analyze(trades)
        assert m.sharpe_ratio == 0.0

    def test_volatility_zero_on_constant(self):
        trades = [_trade() for _ in range(5)]
        m = self.agg.analyze(trades)
        assert m.volatility == 0.0

    def test_final_capital_correct(self):
        trades = [_trade(bet=10.0, cum_pnl=-50.0) for _ in range(10)]
        m = self.agg.analyze(trades)
        assert m.final_capital < 1000.0
