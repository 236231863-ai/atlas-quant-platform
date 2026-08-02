"""product_director_v2 - 产品总监引擎。

职责：
  1. 分析用户（价值分 + 行为）
  2. 检测问题（崩溃率/分析完成率/反馈热点）
  3. 生成路线图建议

输入：行为事件 + 反馈 + 使用指标。
输出：ProductAssessment（产品健康评估 + 建议路线图）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from engine.value_score import compute_value_score, UserValueScore
from engine.feedback_intelligence import FeedbackIntelligence, FeedbackInsight


@dataclass
class ProductAssessment:
    """产品评估。"""

    health_score: float = 0.0       # 0-100
    user_value: UserValueScore = field(default_factory=UserValueScore)
    feedback_insight: FeedbackInsight = field(default_factory=FeedbackInsight)
    issues: List[str] = field(default_factory=list)
    roadmap: List[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines = ["🎯 Atlas 产品评估"]
        lines.append(f"· 健康分：{self.health_score:.0f}/100")
        lines.append(f"· 用户价值：{self.user_value.total:.0f}（{self.user_value.level}）")
        if self.issues:
            lines.append("· 发现问题：")
            for i in self.issues:
                lines.append(f"  - {i}")
        if self.roadmap:
            lines.append("· 建议路线图：")
            for r in self.roadmap:
                lines.append(f"  - {r}")
        return "\n".join(lines)


class ProductDirectorV2:
    """产品总监引擎。"""

    @staticmethod
    def assess(
        total_events: int = 0, active_days: int = 0,
        analysis_runs: int = 0, backtest_runs: int = 0,
        exports: int = 0, feedback_count: int = 0,
        strategy_saves: int = 0,
        crash_rate: float = 0.0,
        analysis_completion: float = 0.0,
        feedback_items: List[dict] = None,
    ) -> ProductAssessment:
        """综合评估产品。"""
        feedback_items = feedback_items or []
        value = compute_value_score(
            total_events=total_events, active_days=active_days,
            analysis_runs=analysis_runs, backtest_runs=backtest_runs,
            exports=exports, feedback_count=feedback_count, strategy_saves=strategy_saves,
        )
        insight = FeedbackIntelligence.analyze(feedback_items)

        # 健康分：基础 60，减去问题分
        health = 60.0
        issues: List[str] = []
        if crash_rate > 0.05:
            health -= 20
            issues.append(f"崩溃率 {crash_rate * 100:.0f}% 超阈值（5%）")
        if analysis_completion < 0.6 and analysis_runs > 0:
            health -= 15
            issues.append(f"分析完成率 {analysis_completion * 100:.0f}% 偏低")
        if insight.by_category.get("bug", 0) >= 3:
            health -= 10
            issues.append("Bug 反馈较多，建议优先修复")
        if active_days < 3:
            health -= 10
            issues.append("用户活跃度偏低")
        health = max(0, min(100, health))

        # 路线图
        roadmap = []
        if insight.by_category.get("bug", 0) > 0:
            roadmap.append("P0：修复反馈中的 Bug")
        if analysis_completion < 0.7:
            roadmap.append("P1：优化分析流程引导，提升完成率")
        if exports == 0:
            roadmap.append("P1：引导用户导出报告（价值感知）")
        if backtest_runs == 0:
            roadmap.append("P2：引导用户尝试回测（核心功能）")
        if not roadmap:
            roadmap.append("P3：扩大用户规模，验证付费转化")

        return ProductAssessment(
            health_score=health, user_value=value, feedback_insight=insight,
            issues=issues, roadmap=roadmap,
        )
