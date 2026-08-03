"""growth_health - 购彩健康指数（v4.2 Phase 3 用户成长体系）。

不是积分商城、不是中奖能力。衡量四个健康维度：
  预算控制 / 连续记录 / 复盘习惯 / 风险意识

输出理性等级 A/B/C：反映「购彩行为是否健康」，与中奖能力无关。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

DISCLAIMER = "健康指数反映购彩行为习惯，不代表中奖能力，也不构成购彩建议。"

DIMENSIONS = ("预算控制", "连续记录", "复盘习惯", "风险意识")


@dataclass
class HealthDimension:
    """单维度健康评分。"""

    name: str
    score: int            # 0-100
    weight: float
    comment: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "score": self.score,
                "weight": self.weight, "comment": self.comment}


@dataclass
class GrowthHealthReport:
    """购彩健康指数报告。"""

    overall_score: int = 0
    rational_level: str = "C"              # A/B/C
    dimensions: List[HealthDimension] = field(default_factory=list)
    ticket_count: int = 0
    suggestions: List[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    @property
    def level_text(self) -> str:
        return {"A": "理性 A 级", "B": "理性 B 级", "C": "理性 C 级"}.get(self.rational_level, "理性 C 级")

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "rational_level": self.rational_level,
            "level_text": self.level_text,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "ticket_count": self.ticket_count,
            "suggestions": list(self.suggestions),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = ["🌱 购彩健康指数"]
        lines.append(f"· 理性等级：{self.level_text}（总分 {self.overall_score}/100）")
        for d in self.dimensions:
            lines.append(f"· {d.name}：{d.score}/100" + (f"（{d.comment}）" if d.comment else ""))
        if self.suggestions:
            lines.append("· 建议：")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class GrowthHealthEngine:
    """购彩健康指数引擎。"""

    @classmethod
    def _budget_score(cls, budget) -> int:
        """预算控制：复用预算健康度。"""
        if budget is None:
            return 50
        return max(0, min(100, budget.health_score))

    @classmethod
    def _record_score(cls, tickets: List[dict]) -> tuple:
        """连续记录：按连续周数与记录分布评分。

        返回 (score, comment)。
        """
        if not tickets:
            return 0, "尚未保存任何购彩记录"
        try:
            from engine.budget_manager import BudgetPlanner
            weeks = BudgetPlanner.consecutive_weeks(tickets)
        except Exception:
            weeks = 0
        if weeks >= 4:
            return 100, f"连续记录 {weeks} 周"
        if weeks >= 2:
            return 70, f"连续记录 {weeks} 周"
        if weeks >= 1:
            return 45, "开始记录但尚未形成连续"
        return 30, "记录中断"

    @classmethod
    def _review_score(cls, tickets: List[dict]) -> tuple:
        """复盘习惯：已开奖票据的确认比例。"""
        claimed = sum(1 for t in tickets if t.get("claimed"))
        try:
            from engine.reminder_center import ReminderEngine
            status = ReminderEngine.ticket_status(tickets)
            settled = status["ready_claim"] + status["claimed"]
        except Exception:
            settled = claimed
        if settled == 0:
            return 50, "暂无已开奖票据可确认"
        ratio = claimed / settled
        if ratio >= 0.8:
            return 100, f"已确认 {claimed}/{settled} 张已开奖票据"
        if ratio >= 0.5:
            return 70, f"确认率 {ratio * 100:.0f}%"
        if ratio > 0:
            return 40, f"确认率 {ratio * 100:.0f}%，建议开奖后查看结果"
        return 10, "开奖后未确认结果，复盘习惯待建立"

    @classmethod
    def _risk_score(cls, budget) -> tuple:
        """风险意识：亏损率与超支惩罚。"""
        if budget is None:
            return 50, ""
        score = 100
        loss = budget.loss_rate
        if loss < -0.5:
            score -= 45
        elif loss < -0.3:
            score -= 20
        elif loss < -0.1:
            score -= 8
        if budget.month_over:
            score -= 25
        if budget.week_over:
            score -= 10
        score = max(0, min(100, score))
        parts = []
        if loss < -0.3:
            parts.append(f"累计亏损率 {loss * 100:.0f}%")
        if budget.month_over:
            parts.append("本月超预算")
        return score, "；".join(parts)

    @classmethod
    def evaluate(cls, tickets: List[dict], budget=None) -> GrowthHealthReport:
        """计算购彩健康指数。"""
        if budget is None:
            try:
                from engine.budget_manager import BudgetPlanner
                budget = BudgetPlanner().evaluate_tickets(tickets)
            except Exception:
                budget = None

        dims = []
        dims.append(HealthDimension("预算控制", cls._budget_score(budget), 0.30))
        rs, rc = cls._record_score(tickets)
        dims.append(HealthDimension("连续记录", rs, 0.20, rc))
        vs, vc = cls._review_score(tickets)
        dims.append(HealthDimension("复盘习惯", vs, 0.25, vc))
        ks, kc = cls._risk_score(budget)
        dims.append(HealthDimension("风险意识", ks, 0.25, kc))

        overall = int(round(sum(d.score * d.weight for d in dims)))
        overall = max(0, min(100, overall))
        level = "A" if overall >= 80 else ("B" if overall >= 60 else "C")

        suggestions = []
        if overall >= 80:
            suggestions.append("购彩习惯健康，请继续保持记录与复盘")
        elif overall >= 60:
            suggestions.append("整体健康，注意控制单月投入节奏")
        else:
            suggestions.append("建议设置预算并坚持记录，理性看待开奖结果")
        for d in dims:
            if d.score < 50:
                suggestions.append(f"「{d.name}」得分偏低（{d.score}/100）")
        if not tickets:
            suggestions = ["保存第一张彩票后，这里才会评估你的购彩健康"]
            level = "C"
            overall = 0

        return GrowthHealthReport(
            overall_score=overall,
            rational_level=level,
            dimensions=dims,
            ticket_count=len(tickets),
            suggestions=suggestions,
        )

    @classmethod
    def evaluate_from_manager(cls, ticket_manager=None) -> GrowthHealthReport:
        """从 TicketManager 读取票据评估。"""
        if ticket_manager is None:
            from engine.ticket_system import TicketManager
            ticket_manager = TicketManager()
        tickets = [t.__dict__ for t in ticket_manager.list_all()]
        return cls.evaluate(tickets)


def growth_health(tickets: List[dict], budget=None) -> GrowthHealthReport:
    """便捷函数：购彩健康指数。"""
    return GrowthHealthEngine.evaluate(tickets, budget)
