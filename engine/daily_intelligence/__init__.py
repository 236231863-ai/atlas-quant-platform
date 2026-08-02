"""daily_intelligence - 每日智能摘要（v3.7.0 Phase 2）。

DailySummary：对比上次快照与当前数据，输出数据/统计/趋势变化与报告提醒。
严格禁止中奖预测。
"""
from .summary import DailySummary, build_summary

__all__ = ["DailySummary", "build_summary"]
