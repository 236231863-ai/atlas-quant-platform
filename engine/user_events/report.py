"""user_events.report - User Behavior Report（v4.5 P5）。

基于真实用户行为事件，回答「用户为什么打开 Atlas」：
  ticket_saved / draw_reminder_received / draw_opened /
  claim_completed / report_viewed / app_opened
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

KEY_EVENTS = (
    "app_opened", "ticket_saved", "draw_reminder_received", "draw_opened",
    "claim_completed", "report_viewed",
)


@dataclass
class BehaviorSummary:
    """行为统计摘要。"""

    total_events: int = 0
    by_event: dict = field(default_factory=dict)
    active_days: int = 0
    last_seen: str = ""

    def top_events(self, n: int = 3) -> List[tuple]:
        """使用最多的前 n 个事件。"""
        items = [(k, v) for k, v in self.by_event.items() if v > 0]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:n]


@dataclass
class UserBehaviorReport:
    """用户行为报告。"""

    summary: BehaviorSummary = field(default_factory=BehaviorSummary)
    daily: dict = field(default_factory=dict)   # 日期 -> {event: count}
    insights: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"total_events": self.summary.total_events,
                "by_event": dict(self.summary.by_event),
                "active_days": self.summary.active_days,
                "last_seen": self.summary.last_seen,
                "daily": {d: dict(v) for d, v in self.daily.items()},
                "insights": list(self.insights)}

    def to_text(self) -> str:
        lines = ["📊 User Behavior Report"]
        lines.append(f"· 总事件：{self.summary.total_events} · 活跃天数：{self.summary.active_days}")
        top = self.summary.top_events(5)
        if top:
            lines.append("· 主要行为：")
            for k, v in top:
                lines.append(f"  - {k}: {v}")
        if self.insights:
            lines.append("· 洞察：")
            for i in self.insights:
                lines.append(f"  💡 {i}")
        return "\n".join(lines)


class BehaviorReporter:
    """构建 User Behavior Report。"""

    @classmethod
    def build(cls, events: Optional[List] = None) -> UserBehaviorReport:
        """从事件列表构建报告。"""
        if events is None:
            from engine.user_events import EventTracker
            events = EventTracker().all()

        rep = UserBehaviorReport()
        rep.summary.total_events = len(events)
        by_event = {k: 0 for k in KEY_EVENTS}
        days = {}
        for e in events:
            if e.event_type in by_event:
                by_event[e.event_type] += 1
            day = (e.created_at or "")[:10]
            if day:
                days.setdefault(day, {}).setdefault(e.event_type, 0)
                days[day][e.event_type] = days[day].get(e.event_type, 0) + 1
        rep.summary.by_event = by_event
        rep.daily = days
        rep.summary.active_days = len(days)
        if events:
            dates = sorted(d for d in days)
            rep.summary.last_seen = dates[-1] if dates else ""
        rep.insights = cls._insights(by_event, rep.summary.active_days)
        return rep

    @classmethod
    def _insights(cls, by_event: dict, active_days: int) -> List[str]:
        """行为洞察（为什么打开）。"""
        insights = []
        opened = by_event.get("app_opened", 0)
        saved = by_event.get("ticket_saved", 0)
        claimed = by_event.get("claim_completed", 0)
        reminded = by_event.get("draw_reminder_received", 0)
        draw_opened = by_event.get("draw_opened", 0)

        if opened == 0:
            insights.append("尚无使用记录")
            return insights
        if saved == 0:
            insights.append("用户未保存票据——需降低录入门槛")
        else:
            save_rate = saved / opened
            if save_rate < 0.3:
                insights.append("票据保存率偏低，建议优化录入体验")
            else:
                insights.append("票据保存活跃，数据飞轮在积累")
        if draw_opened == 0 and reminded > 0:
            insights.append("收到提醒但未打开查看——提醒内容需更吸引")
        if claimed == 0 and saved > 0:
            insights.append("保存票据但未完成兑奖——兑奖闭环待强化")
        if active_days >= 3:
            insights.append("多日活跃，用户养成使用习惯")
        if saved > 0 and claimed > 0 and draw_opened > 0:
            insights.append("核心行为链路通畅（保存→兑奖→查看）")
        if not insights:
            insights.append("核心行为链路通畅（保存→提醒→兑奖→报告）")
        return insights


def build_behavior_report(events: Optional[List] = None) -> UserBehaviorReport:
    """便捷函数。"""
    return BehaviorReporter.build(events)
