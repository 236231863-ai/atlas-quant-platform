"""risk - 资金风险分析（v3.9.0 Phase 4）。

彩票资金风险分析：
  输入：每期投入金额 / 周期 / 投注次数
  输出：年度投入 / 最大损失 / 预计回报 / 亏损概率 / 风险等级 A-D

声明：彩票为负期望游戏，长期亏损是大概率事件。
"""
from .engine import RiskEngine, RiskReport, analyze_risk

__all__ = ["RiskEngine", "RiskReport", "analyze_risk"]
