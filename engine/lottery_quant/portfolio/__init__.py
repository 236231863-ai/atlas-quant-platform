"""portfolio - 投注组合分析（v3.9.0 Phase 5）。

分析多注组合：号码重复率 / 组合相关性 / 覆盖范围 / 集中风险。
提供结构优化建议（只能优化结构，不能保证中奖）。
"""
from .analyzer import PortfolioAnalyzer, PortfolioReport, analyze_portfolio

__all__ = ["PortfolioAnalyzer", "PortfolioReport", "analyze_portfolio"]
