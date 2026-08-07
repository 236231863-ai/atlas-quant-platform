"""user_experiment.funnel - 用户实验漏斗（v4.9 P1）。

安装 → 首次打开 → 保存彩票 → 开奖提醒 → 兑奖查看 → 周报查看
每阶段：用户数 / 转化率（相对安装）/ 流失率（相对上一阶段）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from engine.user_experiment.events import (
    ExperimentTracker,
    normalize_source,
    SOURCE_REAL,
)

# 漏斗阶段（事件名, 中文标签）
FUNNEL_STAGES = (
    ("app_install", "安装"),
    ("app_open", "首次打开"),
    ("ticket_saved", "保存彩票"),
    ("draw_reminder_clicked", "开奖提醒"),
    ("claim_checked", "兑奖查看"),
    ("report_viewed", "周报查看"),
)


@dataclass
class FunnelStage:
    """漏斗一阶段。"""

    event: str
    label: str
    users: int = 0
    conversion: float = 0.0     # 相对安装
    drop_rate: float = 0.0      # 相对上一阶段流失率

    def to_dict(self) -> dict:
        return {"event": self.event, "label": self.label, "users": self.users,
                "conversion": round(self.conversion, 4),
                "drop_rate": round(self.drop_rate, 4)}


@dataclass
class ExperimentFunnelReport:
    """完整实验漏斗。"""

    stages: List[FunnelStage] = field(default_factory=list)
    total_installs: int = 0

    def to_dict(self) -> dict:
        return {"total_installs": self.total_installs,
                "stages": [s.to_dict() for s in self.stages]}

    def to_text(self) -> str:
        lines = ["🔻 用户漏斗（v4.9 P1）"]
        lines.append(f"  总安装: {self.total_installs}")
        for s in self.stages:
            lines.append(f"  {s.label}: {s.users} 人"
                         f"（转化 {s.conversion * 100:.1f}% · 流失 {s.drop_rate * 100:.1f}%）")
        return "\n".join(lines)


class ExperimentFunnel:
    """从实验事件构建漏斗。"""

    @classmethod
    def build(cls, events: Optional[list] = None,
              experiment_id: Optional[str] = None,
              source: Optional[str] = SOURCE_REAL) -> ExperimentFunnelReport:
        """构建漏斗。默认只统计真实用户（REAL）；source=None 统计全部（不推荐混用）。"""
        if events is None:
            events = ExperimentTracker().all()
        if experiment_id:
            events = [e for e in events if e.experiment_id == experiment_id]
        if source is not None:
            events = [e for e in events
                      if normalize_source(e.source) == source]

        # 每阶段触达用户
        reached: dict = {}
        for e in events:
            reached.setdefault(e.event_name, set()).add(e.user_id)

        total = len(reached.get("app_install", set()))
        report = ExperimentFunnelReport(total_installs=total)
        prev = None
        for event, label in FUNNEL_STAGES:
            users = len(reached.get(event, set()))
            conv = users / total if total else 0.0
            drop = ((prev - users) / prev) if (prev is not None and prev > 0) else 0.0
            report.stages.append(FunnelStage(event=event, label=label, users=users,
                                             conversion=conv,
                                             drop_rate=max(0.0, drop)))
            prev = users
        return report


def build_funnel(events: Optional[list] = None) -> ExperimentFunnelReport:
    """便捷函数。"""
    return ExperimentFunnel.build(events)
