"""evaluation_v2 - 回测可信化（v3.6.1 Phase 2）。

实现：
  - Sample Split   : 时序划分，训练 70% / 验证 30%（split.py）
  - Random Baseline: 随机选号基准对照（baseline.py）
  - Performance    : ROI/命中/回撤 + 样本内外对比（metrics.py）
  - Disclaimer     : 免责声明模块，禁止诱导中奖表达（disclaimer.py）

用法:
    from engine.evaluation_v2 import run_backtest_with_evaluation
    report = run_backtest_with_evaluation(draws, method="hot")
    print(report.conclusion())
"""
from .split import temporal_split, walk_forward_indexes
from .baseline import RandomBaseline, PrizeRule, DLT_PRIZES
from .metrics import PerformanceReport, BacktestRecord, run_backtest_with_evaluation
from .disclaimer import (
    DISCLAIMER,
    SHORT_DISCLAIMER,
    FORBIDDEN_EXPRESSIONS,
    get_disclaimer,
    get_short_disclaimer,
    validate_copy,
)

__all__ = [
    "temporal_split",
    "walk_forward_indexes",
    "RandomBaseline",
    "PrizeRule",
    "DLT_PRIZES",
    "PerformanceReport",
    "BacktestRecord",
    "run_backtest_with_evaluation",
    "DISCLAIMER",
    "SHORT_DISCLAIMER",
    "FORBIDDEN_EXPRESSIONS",
    "get_disclaimer",
    "get_short_disclaimer",
    "validate_copy",
]
