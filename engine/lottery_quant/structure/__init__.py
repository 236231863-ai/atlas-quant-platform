"""structure - 号码结构分析（v3.9.0 Phase 2）。

分析号码组合结构：奇偶/大小/三区/和值/跨度/连号/重复/历史偏离度。
输出 CombinationScore（结构评分，不是中奖概率）。
"""
from .analyzer import (
    StructureAnalyzer,
    StructureMetrics,
    CombinationScore,
    analyze_combination,
)

__all__ = ["StructureAnalyzer", "StructureMetrics", "CombinationScore", "analyze_combination"]
