"""user_feedback_v2 - 用户行为报告（UserBehaviorReport）。

汇总行为事件，输出：
  - 事件统计（按类型）
  - 热门页面 TOP
  - 高频功能 TOP
  - 导出偏好（格式分布）
  - 常用策略
  - 用户偏好快照
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .tracker import UserFeedbackTracker


@dataclass
class UserBehaviorReport:
    """用户行为报告。"""

    total_events: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    top_pages: List[tuple] = field(default_factory=list)
    top_features: List[tuple] = field(default_factory=list)
    export_formats: Dict[str, int] = field(default_factory=dict)
    top_strategies: List[tuple] = field(default_factory=list)
    preferences: Dict[str, object] = field(default_factory=dict)
    active_days: int = 0

    def to_text(self) -> str:
        lines = ["📊 Atlas 用户行为报告"]
        lines.append(f"· 总事件：{self.total_events}，活跃天数：{self.active_days}")
        lines.append(f"· 事件分布：{', '.join(f'{k}={v}' for k, v in sorted(self.by_type.items()))}")
        if self.top_pages:
            lines.append("· 热门页面：" + " → ".join(f"{p}({c})" for p, c in self.top_pages[:5]))
        if self.top_features:
            lines.append("· 高频功能：" + "、".join(f"{f}({c})" for f, c in self.top_features[:5]))
        if self.export_formats:
            lines.append("· 导出格式：" + ", ".join(f"{k}:{v}" for k, v in sorted(self.export_formats.items())))
        if self.top_strategies:
            lines.append("· 常用策略：" + "、".join(f"{s}({c})" for s, c in self.top_strategies[:3]))
        if self.preferences:
            lines.append("· 用户偏好：" + ", ".join(f"{k}={v}" for k, v in self.preferences.items()))
        lines.append("· 本数据仅存本机，用于改进产品体验。")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total_events": self.total_events,
            "by_type": self.by_type,
            "top_pages": self.top_pages,
            "top_features": self.top_features,
            "export_formats": self.export_formats,
            "top_strategies": self.top_strategies,
            "preferences": self.preferences,
            "active_days": self.active_days,
        }


def build_behavior_report(tracker: Optional[UserFeedbackTracker] = None, events: Optional[List[dict]] = None) -> UserBehaviorReport:
    """从 tracker（或给定事件）构建行为报告。"""
    if events is None:
        tracker = tracker or UserFeedbackTracker()
        events = tracker.load()

    report = UserBehaviorReport(total_events=len(events))
    type_counter: Counter = Counter()
    page_counter: Counter = Counter()
    feature_counter: Counter = Counter()
    fmt_counter: Counter = Counter()
    strategy_counter: Counter = Counter()
    prefs: Dict[str, object] = {}
    days = set()

    for e in events:
        t = e.get("type", "unknown")
        type_counter[t] += 1
        ts = e.get("ts", "")
        if ts:
            days.add(ts[:10])
        if t == "page_view":
            page_counter[e.get("page", "")] += 1
        elif t == "feature_use":
            feature_counter[e.get("feature", "")] += 1
        elif t == "report_export":
            fmt_counter[e.get("fmt", "")] += 1
        elif t == "strategy_view":
            strategy_counter[e.get("strategy", "")] += 1
        elif t == "preference":
            prefs[e.get("key", "")] = e.get("value")

    report.by_type = dict(type_counter)
    report.top_pages = page_counter.most_common(8)
    report.top_features = feature_counter.most_common(8)
    report.export_formats = dict(fmt_counter)
    report.top_strategies = strategy_counter.most_common(5)
    report.preferences = prefs
    report.active_days = len(days)
    return report
