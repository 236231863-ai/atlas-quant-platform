"""product_analytics_v2 - 产品使用分析。

标准事件：app_open / analysis_start / analysis_complete / report_export /
          backtest_run / strategy_view / app_close

输出：ProductUsageReport（会话数/分析完成率/导出/回测/策略/活跃天数）。
"""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# 标准事件
EVENTS = {
    "app_open", "analysis_start", "analysis_complete", "report_export",
    "backtest_run", "strategy_view", "app_close",
}


class ProductAnalytics:
    """产品使用事件记录器（本地 JSONL）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "analytics.jsonl")

    def _ensure(self) -> None:
        os.makedirs(self._dir, exist_ok=True)

    def track(self, event: str, **data) -> bool:
        if event not in EVENTS:
            return False
        self._ensure()
        entry = {
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event,
            **data,
        }
        try:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except OSError:
            return False

    def app_open(self) -> bool:
        return self.track("app_open")

    def app_close(self) -> bool:
        return self.track("app_close")

    def analysis_start(self) -> bool:
        return self.track("analysis_start")

    def analysis_complete(self) -> bool:
        return self.track("analysis_complete")

    def report_export(self, fmt: str = "") -> bool:
        return self.track("report_export", fmt=fmt)

    def backtest_run(self, method: str = "") -> bool:
        return self.track("backtest_run", method=method)

    def strategy_view(self, strategy: str = "") -> bool:
        return self.track("strategy_view", strategy=strategy)

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
        if limit:
            events = events[-limit:]
        return events

    def clear(self) -> None:
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass


@dataclass
class ProductUsageReport:
    """产品使用报告。"""

    total_sessions: int = 0
    app_open: int = 0
    app_close: int = 0
    analysis_start: int = 0
    analysis_complete: int = 0
    report_exports: int = 0
    backtest_runs: int = 0
    strategy_views: int = 0
    active_days: int = 0
    export_formats: Dict[str, int] = field(default_factory=dict)
    backtest_methods: Dict[str, int] = field(default_factory=dict)
    top_strategies: List[tuple] = field(default_factory=list)

    @property
    def analysis_completion_rate(self) -> float:
        """分析完成率（complete/start）。"""
        if self.analysis_start == 0:
            return 0.0
        return round(self.analysis_complete / self.analysis_start, 3)

    @property
    def crash_rate(self) -> float:
        """粗略崩溃率：open 后无 close 的会话比例（近似）。"""
        if self.app_open == 0:
            return 0.0
        return round(max(0, self.app_open - self.app_close) / self.app_open, 3)

    def to_text(self) -> str:
        lines = ["📊 Atlas 产品使用报告"]
        lines.append(f"· 会话：{self.total_sessions} 次，活跃天数 {self.active_days}")
        lines.append(f"· 分析：启动 {self.analysis_start} / 完成 {self.analysis_complete}（完成率 {self.analysis_completion_rate * 100:.0f}%）")
        lines.append(f"· 导出 {self.report_exports} 次 · 回测 {self.backtest_runs} 次 · 策略查看 {self.strategy_views} 次")
        lines.append(f"· 崩溃率（open 无 close）：{self.crash_rate * 100:.0f}%")
        if self.export_formats:
            lines.append("· 导出格式：" + ", ".join(f"{k}:{v}" for k, v in sorted(self.export_formats.items())))
        if self.top_strategies:
            lines.append("· 热门策略：" + "、".join(f"{s}({c})" for s, c in self.top_strategies[:3]))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total_sessions": self.total_sessions,
            "app_open": self.app_open,
            "app_close": self.app_close,
            "analysis_start": self.analysis_start,
            "analysis_complete": self.analysis_complete,
            "analysis_completion_rate": self.analysis_completion_rate,
            "crash_rate": self.crash_rate,
            "report_exports": self.report_exports,
            "backtest_runs": self.backtest_runs,
            "strategy_views": self.strategy_views,
            "active_days": self.active_days,
            "export_formats": self.export_formats,
            "top_strategies": self.top_strategies,
        }


def build_usage_report(analytics: Optional[ProductAnalytics] = None, events: Optional[List[dict]] = None) -> ProductUsageReport:
    """从事件构建使用报告。"""
    if events is None:
        analytics = analytics or ProductAnalytics()
        events = analytics.load()

    r = ProductUsageReport()
    fmt_counter: Counter = Counter()
    bt_counter: Counter = Counter()
    strat_counter: Counter = Counter()
    days = set()

    for e in events:
        ev = e.get("event", "")
        ts = e.get("ts", "")
        if ts:
            days.add(ts[:10])
        if ev == "app_open":
            r.app_open += 1
        elif ev == "app_close":
            r.app_close += 1
        elif ev == "analysis_start":
            r.analysis_start += 1
        elif ev == "analysis_complete":
            r.analysis_complete += 1
        elif ev == "report_export":
            r.report_exports += 1
            fmt_counter[e.get("fmt", "")] += 1
        elif ev == "backtest_run":
            r.backtest_runs += 1
            bt_counter[e.get("method", "")] += 1
        elif ev == "strategy_view":
            r.strategy_views += 1
            strat_counter[e.get("strategy", "")] += 1

    r.total_sessions = max(r.app_open, r.app_close)
    r.active_days = len(days)
    r.export_formats = dict(fmt_counter)
    r.backtest_methods = dict(bt_counter)
    r.top_strategies = strat_counter.most_common(5)
    return r
