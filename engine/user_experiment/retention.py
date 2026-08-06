"""user_experiment.retention - 用户实验留存曲线（v4.9 P1）。

基于 app_open / weekly_return 事件计算 D1 / D3 / D7 留存与留存曲线。
以用户首次出现日为 D0，按日统计活跃用户。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from engine.user_experiment.events import ExperimentTracker


@dataclass
class RetentionPoint:
    """留存曲线一点。"""

    day_offset: int
    rate: float
    users: int

    def to_dict(self) -> dict:
        return {"day_offset": self.day_offset, "rate": round(self.rate, 4),
                "users": self.users}


@dataclass
class ExperimentRetention:
    """实验留存指标。"""

    d1: float = 0.0
    d3: float = 0.0
    d7: float = 0.0
    curve: List[RetentionPoint] = field(default_factory=list)
    cohort_users: int = 0

    def to_dict(self) -> dict:
        return {"d1": round(self.d1, 4), "d3": round(self.d3, 4),
                "d7": round(self.d7, 4),
                "curve": [p.to_dict() for p in self.curve],
                "cohort_users": self.cohort_users}

    def to_text(self) -> str:
        return (f"📈 留存: D1 {self.d1 * 100:.1f}% · D3 {self.d3 * 100:.1f}% · "
                f"D7 {self.d7 * 100:.1f}%")


class ExperimentRetentionBuilder:
    """基于事件计算留存。"""

    @classmethod
    def build(cls, events: Optional[list] = None,
              experiment_id: Optional[str] = None,
              use_weekly_return: bool = False,
              max_day: int = 7) -> ExperimentRetention:
        """从事件构建留存。

        use_weekly_return=True 时，活跃判定同时计入 weekly_return 事件
        （周回访也算活跃）；否则仅统计 app_open。
        """
        if events is None:
            events = ExperimentTracker().all()
        if experiment_id:
            events = [e for e in events if e.experiment_id == experiment_id]

        active_events = [e for e in events
                         if e.event_name == "app_open"
                         or (use_weekly_return and e.event_name == "weekly_return")]

        # 用户首次出现日 & 活跃日
        first_seen: Dict[str, str] = {}
        active_by_day: Dict[str, set] = {}
        for e in active_events:
            day = (e.timestamp or "")[:10]
            if not day:
                continue
            active_by_day.setdefault(day, set()).add(e.user_id)
            if e.user_id not in first_seen or day < first_seen[e.user_id]:
                first_seen[e.user_id] = day

        cohorts: Dict[str, set] = {}
        for uid, day0 in first_seen.items():
            cohorts.setdefault(day0, set()).add(uid)

        def _rate(offset: int) -> float:
            total = 0
            retained = 0
            for day0, users in cohorts.items():
                try:
                    target = (datetime.strptime(day0, "%Y-%m-%d").date()
                              + timedelta(days=offset)).isoformat()
                except ValueError:
                    continue
                active = active_by_day.get(target, set())
                total += len(users)
                retained += len(users & active)
            return retained / total if total else 0.0

        curve = [RetentionPoint(day_offset=0, rate=1.0,
                                users=len(cohorts))]
        for offset in range(1, max_day + 1):
            curve.append(RetentionPoint(day_offset=offset, rate=_rate(offset),
                                        users=0))
        cohort_users = sum(len(u) for u in cohorts.values())

        return ExperimentRetention(
            d1=_rate(1), d3=_rate(3), d7=_rate(7),
            curve=curve, cohort_users=cohort_users,
        )


def build_retention(events: Optional[list] = None) -> ExperimentRetention:
    """便捷函数。"""
    return ExperimentRetentionBuilder.build(events)
