"""user_analytics.funnel - 用户漏斗（v4.6 P1）。

打开APP → 保存彩票 → 查看结果 → 查看资产 → 再次打开
每阶段：人数 / 转化率 / 流失率
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

FUNNEL_STAGES = (
    ("app_opened", "打开APP"),
    ("ticket_saved", "保存彩票"),
    ("ticket_checked", "查看结果"),
    ("claim_completed", "完成兑奖"),
    ("report_viewed", "查看资产/报告"),
)


@dataclass
class FunnelStage:
    """漏斗一阶段。"""

    event: str
    label: str
    users: int = 0
    conversion: float = 0.0      # 相对首阶段
    drop_rate: float = 0.0       # 相对上一阶段流失

    def to_dict(self) -> dict:
        return {"event": self.event, "label": self.label, "users": self.users,
                "conversion": round(self.conversion, 4),
                "drop_rate": round(self.drop_rate, 4)}


@dataclass
class FunnelReport:
    """完整漏斗报告。"""

    stages: List[FunnelStage] = field(default_factory=list)
    total_users: int = 0

    def to_dict(self) -> dict:
        return {"total_users": self.total_users,
                "stages": [s.to_dict() for s in self.stages]}

    def to_text(self) -> str:
        lines = ["🔻 用户漏斗"]
        for s in self.stages:
            lines.append(f"  {s.label}: {s.users} 人"
                         f"（转化 {s.conversion * 100:.1f}% · 流失 {s.drop_rate * 100:.1f}%）")
        return "\n".join(lines)


class FunnelBuilder:
    """构建用户漏斗。"""

    @classmethod
    def build(cls, events: Optional[list] = None) -> FunnelReport:
        """从事件列表构建漏斗（按 user_id 去重）。"""
        if events is None:
            from engine.user_analytics.analytics import AnalyticsTracker
            events = AnalyticsTracker().all()

        # 每阶段触达的用户集合
        reached = {}
        for e in events:
            reached.setdefault(e.event_name, set()).add(e.user_id)

        total_users = len(reached.get("app_opened", set()))
        report = FunnelReport(total_users=total_users)
        prev_users = None
        for event, label in FUNNEL_STAGES:
            users = len(reached.get(event, set()))
            conversion = users / total_users if total_users else 0.0
            drop = ((prev_users - users) / prev_users) if (prev_users and prev_users > 0) else 0.0
            report.stages.append(FunnelStage(event=event, label=label,
                                             users=users, conversion=conversion,
                                             drop_rate=max(0.0, drop)))
            prev_users = users
        return report


def build_funnel(events: Optional[list] = None) -> FunnelReport:
    """便捷函数。"""
    return FunnelBuilder.build(events)
