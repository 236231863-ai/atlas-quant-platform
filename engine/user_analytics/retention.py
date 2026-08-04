"""user_analytics.retention - Retention Dashboard（v4.6 P1）。

日/周留存：
  D0/D1/D3/D7 留存率
  周留存
  活跃天数分布
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class RetentionMetrics:
    """留存指标。"""

    active_days: int = 0
    daily: Dict[str, int] = field(default_factory=dict)     # 日期 -> 活跃用户数
    d1: float = 0.0
    d3: float = 0.0
    d7: float = 0.0

    def to_dict(self) -> dict:
        return {"active_days": self.active_days,
                "daily": {d: int(v) for d, v in self.daily.items()},
                "d1": round(self.d1, 4), "d3": round(self.d3, 4),
                "d7": round(self.d7, 4)}


class RetentionBuilder:
    """构建 Retention Dashboard。"""

    @classmethod
    def build(cls, events: Optional[list] = None,
              now: Optional[date] = None) -> RetentionMetrics:
        """基于 app_opened 事件计算留存。"""
        if events is None:
            from engine.user_analytics.analytics import AnalyticsTracker
            events = AnalyticsTracker().all()
        now = now or date.today()

        # 用户首次出现日期 & 活跃日期
        first_seen = {}
        active_by_day = {}
        for e in events:
            if e.event_name != "app_opened":
                continue
            day = (e.timestamp or "")[:10]
            if not day:
                continue
            active_by_day.setdefault(day, set()).add(e.user_id)
            if e.user_id not in first_seen or day < first_seen[e.user_id]:
                first_seen[e.user_id] = day

        metrics = RetentionMetrics()
        metrics.active_days = len(active_by_day)
        metrics.daily = {d: len(u) for d, u in sorted(active_by_day.items())}

        # 留存率：以首见日为 D0
        cohorts = {}
        for uid, day0 in first_seen.items():
            cohorts.setdefault(day0, set()).add(uid)

        def _retention(offset: int) -> float:
            total = 0
            retained = 0
            for day0, users in cohorts.items():
                target = (datetime.strptime(day0, "%Y-%m-%d").date()
                          + timedelta(days=offset)).isoformat()
                active = active_by_day.get(target, set())
                total += len(users)
                retained += len(users & active)
            return retained / total if total else 0.0

        metrics.d1 = _retention(1)
        metrics.d3 = _retention(3)
        metrics.d7 = _retention(7)
        return metrics


def build_retention(events: Optional[list] = None) -> RetentionMetrics:
    """便捷函数。"""
    return RetentionBuilder.build(events)
