"""user_experiment.metrics - 用户验证指标（v4.9 P1 Q1-Q4）。

Q1 安装完成率：install 事件用户 / 进入实验用户
Q2 首次建档率：first ticket_saved / installed（护栏 ≥50%）
Q3 D1 ≥40% / D7 ≥30%（由 retention 计算）
Q4 Premium 兴趣：premium_view / premium_click（付费意愿点击率）
北极星 WALU：每周有彩票行为（ticket_saved / claim_checked / reminder_clicked）的用户
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from engine.user_experiment.events import ExperimentTracker, SOURCE_REAL
from engine.user_experiment.funnel import ExperimentFunnel, ExperimentFunnelReport
from engine.user_experiment.retention import (
    ExperimentRetention,
    ExperimentRetentionBuilder,
)

# 目标护栏
TARGETS = {
    "first_save_rate": 0.50,   # Q2 首次建档率 ≥50%
    "d1": 0.40,                # Q3 D1 ≥40%
    "d7": 0.30,                # Q3 D7 ≥30%
    "reminder_click_rate": 0.30,
}


@dataclass
class ValidationMetric:
    """一项验证指标。"""

    key: str
    label: str
    value: float
    target: float
    passed: bool

    def to_dict(self) -> dict:
        return {"key": self.key, "label": self.label,
                "value": round(self.value, 4), "target": round(self.target, 4),
                "passed": self.passed}


@dataclass
class ValidationMetrics:
    """完整验证指标集。"""

    metrics: List[ValidationMetric] = field(default_factory=list)
    walu: int = 0
    installs: int = 0

    def to_dict(self) -> dict:
        return {"metrics": [m.to_dict() for m in self.metrics],
                "walu": self.walu, "installs": self.installs}

    def to_text(self) -> str:
        lines = ["🎯 用户验证指标（v4.9 P1）"]
        for m in self.metrics:
            flag = "✅" if m.passed else "❌"
            lines.append(f"  {flag} {m.label}: {m.value * 100:.1f}%"
                         f"（目标 {m.target * 100:.1f}%）")
        lines.append(f"  北极星 WALU: {self.walu} · 安装: {self.installs}")
        return "\n".join(lines)


class ValidationMetricsBuilder:
    """从事件构建 Q1-Q4 指标。"""

    @classmethod
    def build(cls, events: Optional[list] = None,
              experiment_id: Optional[str] = None,
              retention: Optional[ExperimentRetention] = None,
              funnel: Optional[ExperimentFunnelReport] = None,
              source: Optional[str] = SOURCE_REAL) -> ValidationMetrics:
        if events is None:
            events = ExperimentTracker().all()
        if experiment_id:
            events = [e for e in events if e.experiment_id == experiment_id]
        if source is not None:
            from engine.user_experiment.events import is_real_source, normalize_source
            if source == SOURCE_REAL:
                # REAL 口径 = REAL + MOBILE（移动端真实用户计入真实统计）
                events = [e for e in events
                          if is_real_source(normalize_source(e.source))]
            else:
                events = [e for e in events
                          if normalize_source(e.source) == source]
        if funnel is None:
            funnel = ExperimentFunnel.build(events, source=None)
        if retention is None:
            retention = ExperimentRetentionBuilder.build(events, source=None)

        # 触达用户
        reached: dict = {}
        for e in events:
            reached.setdefault(e.event_name, set()).add(e.user_id)
        installed = reached.get("app_install", set())
        opened = reached.get("app_open", set())
        saved = reached.get("ticket_saved", set())
        reminded = reached.get("draw_reminder_clicked", set())
        premium_view = reached.get("premium_view", set())
        premium_click = reached.get("premium_click", set())

        installs = len(installed)
        # Q1 安装完成率：打开 / 安装（安装后至少打开一次）
        install_complete = len(opened & installed) / installs if installs else 0.0
        # Q2 首次建档率：保存 / 安装
        first_save = len(saved & installed) / installs if installs else 0.0
        # 提醒点击率：提醒点击 / 安装
        reminder_rate = len(reminded & installed) / installs if installs else 0.0
        # Q4 付费意愿：premium_click / premium_view
        pay_willing = len(premium_click) / len(premium_view) if premium_view else 0.0

        metrics = [
            ValidationMetric("install_complete", "安装完成率(Q1)",
                             install_complete, 1.0, install_complete >= 0.5),
            ValidationMetric("first_save_rate", "首次建档率(Q2)",
                             first_save, TARGETS["first_save_rate"],
                             first_save >= TARGETS["first_save_rate"]),
            ValidationMetric("d1", "D1 留存(Q3)",
                             retention.d1, TARGETS["d1"],
                             retention.d1 >= TARGETS["d1"]),
            ValidationMetric("d7", "D7 留存(Q3)",
                             retention.d7, TARGETS["d7"],
                             retention.d7 >= TARGETS["d7"]),
            ValidationMetric("reminder_click_rate", "提醒点击率",
                             reminder_rate, TARGETS["reminder_click_rate"],
                             reminder_rate >= TARGETS["reminder_click_rate"]),
            ValidationMetric("pay_willing", "付费意愿点击率(Q4)",
                             pay_willing, 0.05,
                             pay_willing >= 0.05),
        ]

        # 北极星 WALU：本周有彩票行为的用户
        walu_users = set(saved) | set(reached.get("claim_checked", set())) | reminded
        walu = len(walu_users)

        return ValidationMetrics(metrics=metrics, walu=walu, installs=installs)


def build_metrics(events: Optional[list] = None) -> ValidationMetrics:
    """便捷函数。"""
    return ValidationMetricsBuilder.build(events)
