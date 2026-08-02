"""backtest - 彩票策略回测（v3.9.0 Phase 6）。

复用 engine/evaluation_v2 回测框架，支持热号/冷号/均衡/随机策略。
输出 StrategyReport：各策略 ROI + 随机基准比较。
禁止盈利保证。
"""
from .strategy import (
    STRATEGY_METHODS,
    STRATEGY_NAMES,
    StrategyBacktester,
    StrategyReport,
    run_strategy_backtest,
)

__all__ = ["STRATEGY_METHODS", "STRATEGY_NAMES", "StrategyBacktester",
           "StrategyReport", "run_strategy_backtest"]
