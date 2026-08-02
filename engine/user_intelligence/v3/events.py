"""user_intelligence/v3 - 行为事件与汇总。"""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

EVENTS = {
    "APP_START", "ANALYSIS_RUN", "REPORT_EXPORT", "BACKTEST_RUN",
    "STRATEGY_SAVE", "FEEDBACK_SEND",
}


class UserIntelligenceV3:
    """行为事件记录器（本地 JSONL，v3）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "user_intel_v3.jsonl")

    def _ensure(self) -> None:
        os.makedirs(self._dir, exist_ok=True)

    def track(self, event: str, **data) -> bool:
        if event not in EVENTS:
            return False
        self._ensure()
        entry = {"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "event": event, **data}
        try:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except OSError:
            return False

    def app_start(self) -> bool:
        return self.track("APP_START")

    def analysis_run(self, method: str = "") -> bool:
        return self.track("ANALYSIS_RUN", method=method)

    def report_export(self, fmt: str = "") -> bool:
        return self.track("REPORT_EXPORT", fmt=fmt)

    def backtest_run(self, method: str = "") -> bool:
        return self.track("BACKTEST_RUN", method=method)

    def strategy_save(self, name: str = "") -> bool:
        return self.track("STRATEGY_SAVE", name=name)

    def feedback_send(self, ftype: str = "") -> bool:
        return self.track("FEEDBACK_SEND", type=ftype)

    def load(self, limit: Optional[int] = None) -> List[dict]:
        if not os.path.exists(self._path):
            return []
        events = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except OSError:
            return []
        return events[-limit:] if limit else events

    def clear(self) -> None:
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass


@dataclass
class BehaviorSummary:
    """行为汇总。"""

    total_events: int = 0
    by_event: Dict[str, int] = field(default_factory=dict)
    active_days: int = 0
    top_methods: List[tuple] = field(default_factory=list)
    top_export_formats: List[tuple] = field(default_factory=list)

    def to_text(self) -> str:
        lines = ["🧠 Atlas 用户行为智能"]
        lines.append(f"· 总事件：{self.total_events}，活跃天数 {self.active_days}")
        lines.append("· " + ", ".join(f"{k}={v}" for k, v in sorted(self.by_event.items())))
        if self.top_methods:
            lines.append("· 常用策略：" + "、".join(f"{m}({c})" for m, c in self.top_methods[:3]))
        if self.top_export_formats:
            lines.append("· 导出格式：" + "、".join(f"{f}({c})" for f, c in self.top_export_formats[:4]))
        return "\n".join(lines)


def build_behavior_summary(tracker: Optional[UserIntelligenceV3] = None, events: Optional[List[dict]] = None) -> BehaviorSummary:
    if events is None:
        tracker = tracker or UserIntelligenceV3()
        events = tracker.load()
    s = BehaviorSummary(total_events=len(events))
    ev_counter: Counter = Counter()
    method_counter: Counter = Counter()
    fmt_counter: Counter = Counter()
    days = set()
    for e in events:
        ev_counter[e.get("event", "?")] += 1
        ts = e.get("ts", "")
        if ts:
            days.add(ts[:10])
        if e.get("event") == "BACKTEST_RUN":
            method_counter[e.get("method", "")] += 1
        elif e.get("event") == "REPORT_EXPORT":
            fmt_counter[e.get("fmt", "")] += 1
    s.by_event = dict(ev_counter)
    s.active_days = len(days)
    s.top_methods = method_counter.most_common(5)
    s.top_export_formats = fmt_counter.most_common(5)
    return s
