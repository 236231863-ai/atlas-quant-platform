"""Atlas Quant Platform - Backtest Engine.

回测引擎: walk-forward simulation, result analysis, performance metrics.
Pure computation: no IO, no database, no side effects.
"""
from __future__ import annotations

from engine.backtest.models import TradeRecord, BacktestConfig, BacktestMetrics
from engine.backtest.simulator import TradeSimulator
from engine.backtest.analyzers import ResultAggregator

__all__ = [
    "TradeRecord", "BacktestConfig", "BacktestMetrics",
    "TradeSimulator", "ResultAggregator",
]
