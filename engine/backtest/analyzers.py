"""
Atlas Quant Platform - Result Aggregator.

Calculates performance metrics from backtest trade records.
Pure computation: no IO, no database.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from engine.backtest.models import TradeRecord, BacktestMetrics


class ResultAggregator:
    """Calculates performance metrics from a list of trade records."""

    def analyze(self, trades: List[TradeRecord]) -> BacktestMetrics:
        """Compute all performance metrics from trade records.

        Args:
            trades: List of trade records from a backtest simulation.

        Returns:
            BacktestMetrics with all calculated performance metrics.
        """
        if not trades:
            return BacktestMetrics()

        total_investment = sum(t.bet_amount for t in trades)
        total_return = sum(t.win_amount for t in trades)
        roi = ((total_return - total_investment) / total_investment * 100) if total_investment > 0 else 0.0
        win_count = sum(1 for t in trades if t.is_win)
        total_bets = len(trades)
        win_rate = (win_count / total_bets * 100) if total_bets > 0 else 0.0

        # Net PnL per trade
        net_pnls = [t.win_amount - t.bet_amount for t in trades]
        avg_return = sum(net_pnls) / len(net_pnls) if net_pnls else 0.0

        # Drawdown calculation
        max_dd_amount, max_dd_pct = self._calculate_max_drawdown(net_pnls)

        # Volatility (std of returns)
        returns = [(t.win_amount / t.bet_amount) - 1 if t.bet_amount > 0 else 0 for t in trades]
        volatility = self._calculate_volatility(returns)

        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe = self._calculate_sharpe(returns, volatility)

        # Prize level distribution
        prize_levels: Dict[str, int] = {}
        for t in trades:
            if t.prize_level > 0:
                key = str(t.prize_level)
                prize_levels[key] = prize_levels.get(key, 0) + 1

        # Best/worst single return
        pnls_sorted = sorted([t.win_amount - t.bet_amount for t in trades])
        best_single = pnls_sorted[-1] if pnls_sorted else 0.0
        worst_single = pnls_sorted[0] if pnls_sorted else 0.0

        # Consecutive losses
        max_consec_losses = 0
        current_consec = 0
        for t in trades:
            if not t.is_win:
                current_consec += 1
                max_consec_losses = max(max_consec_losses, current_consec)
            else:
                current_consec = 0

        final_capital = total_investment + sum(net_pnls)

        return BacktestMetrics(
            total_investment=round(total_investment, 2),
            total_return=round(total_return, 2),
            roi=round(roi, 4),
            win_count=win_count,
            total_bets=total_bets,
            win_rate=round(win_rate, 2),
            max_drawdown_amount=round(max_dd_amount, 2),
            max_drawdown_pct=round(max_dd_pct, 2),
            volatility=round(volatility, 6),
            sharpe_ratio=round(sharpe, 4),
            avg_return_per_bet=round(avg_return, 2),
            final_capital=round(final_capital, 2),
            prize_levels=prize_levels,
            best_single_return=round(best_single, 2),
            worst_single_return=round(worst_single, 2),
            consecutive_losses=current_consec,
            max_consecutive_losses=max_consec_losses,
        )

    def _calculate_max_drawdown(
        self, net_pnls: List[float]
    ) -> tuple:
        """Calculate maximum drawdown from net PnL series.

        Drawdown is the peak-to-trough decline in cumulative PnL.
        Returns (max_drawdown_amount, max_drawdown_pct).
        """
        if not net_pnls:
            return 0.0, 0.0

        cumulative = 0.0
        peak = 0.0
        max_dd_amount = 0.0
        max_dd_pct = 0.0

        for pnl in net_pnls:
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            dd_amount = peak - cumulative
            dd_pct = (dd_amount / peak * 100) if peak > 0 else 0.0
            if dd_amount > max_dd_amount:
                max_dd_amount = dd_amount
                max_dd_pct = dd_pct

        return max_dd_amount, max_dd_pct

    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility (standard deviation of returns)."""
        if len(returns) < 2:
            return 0.0
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        return math.sqrt(variance) if variance > 0 else 0.0

    def _calculate_sharpe(self, returns: List[float], volatility: float) -> float:
        """Calculate Sharpe ratio (risk-free rate = 0)."""
        if not returns or volatility == 0:
            return 0.0
        mean_return = sum(returns) / len(returns)
        return mean_return / volatility if volatility > 0 else 0.0
