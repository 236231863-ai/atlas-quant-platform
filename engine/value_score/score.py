"""value_score - 用户价值分计算。"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UserValueScore:
    """用户价值分。"""

    usage_score: float = 0.0      # 0-20 使用活跃度
    retention_score: float = 0.0  # 0-20 留存
    research_score: float = 0.0   # 0-20 研究深度（回测/分析）
    export_score: float = 0.0     # 0-20 产出（导出）
    feedback_score: float = 0.0   # 0-20 反馈参与
    total: float = 0.0            # 0-100

    @property
    def level(self) -> str:
        """研究等级：入门/进阶/资深/专家。"""
        if self.total >= 80:
            return "专家"
        if self.total >= 60:
            return "资深"
        if self.total >= 35:
            return "进阶"
        return "入门"

    def to_dict(self) -> dict:
        return {
            "usage": round(self.usage_score, 1),
            "retention": round(self.retention_score, 1),
            "research": round(self.research_score, 1),
            "export": round(self.export_score, 1),
            "feedback": round(self.feedback_score, 1),
            "total": round(self.total, 1),
            "level": self.level,
        }

    def to_text(self) -> str:
        return (f"🏆 用户价值分 {self.total:.0f}/100（{self.level}）\n"
                f"· 使用 {self.usage_score:.0f} · 留存 {self.retention_score:.0f} · "
                f"研究 {self.research_score:.0f} · 产出 {self.export_score:.0f} · 反馈 {self.feedback_score:.0f}")


def _clamp(x: float, lo: float = 0.0, hi: float = 20.0) -> float:
    return max(lo, min(hi, x))


def compute_value_score(
    total_events: int = 0,
    active_days: int = 0,
    analysis_runs: int = 0,
    backtest_runs: int = 0,
    exports: int = 0,
    feedback_count: int = 0,
    strategy_saves: int = 0,
) -> UserValueScore:
    """计算用户价值分。

    Args:
        total_events: 总事件数
        active_days: 活跃天数
        analysis_runs: 分析次数
        backtest_runs: 回测次数
        exports: 导出次数
        feedback_count: 反馈次数
        strategy_saves: 策略保存次数
    """
    # Usage（20）：基于事件量与活跃天数
    usage = _clamp(total_events * 0.15 + active_days * 1.5)
    # Retention（20）：基于活跃天数（目标 7 天）
    retention = _clamp(active_days * 20 / 7)
    # Research（20）：分析 + 回测 + 策略保存
    research = _clamp(analysis_runs * 1.0 + backtest_runs * 1.5 + strategy_saves * 1.2)
    # Export（20）
    export = _clamp(exports * 2.5)
    # Feedback（20）
    feedback = _clamp(feedback_count * 6.0)
    total = usage + retention + research + export + feedback
    return UserValueScore(
        usage_score=usage, retention_score=retention, research_score=research,
        export_score=export, feedback_score=feedback, total=total,
    )
