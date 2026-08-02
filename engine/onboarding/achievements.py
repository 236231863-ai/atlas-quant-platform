"""onboarding - 用户成就系统（UserAchievement）。

记录用户里程碑，增强首次成功体验的成就感：
  first_analysis / first_report / first_export / data_500 / backtest_first
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# 成就定义
ACHIEVEMENTS: Dict[str, dict] = {
    "first_analysis": {
        "id": "first_analysis",
        "name": "🎯 第一次分析",
        "desc": "完成第一次数据分析",
        "icon": "🎯",
    },
    "first_report": {
        "id": "first_report",
        "name": "📄 第一份报告",
        "desc": "生成第一份研究报告",
        "icon": "📄",
    },
    "first_export": {
        "id": "first_export",
        "name": "⬇ 第一次导出",
        "desc": "导出任意分析结果",
        "icon": "⬇",
    },
    "data_500": {
        "id": "data_500",
        "name": "📊 数据达人",
        "desc": "数据量达到 500 期",
        "icon": "📊",
    },
    "backtest_first": {
        "id": "backtest_first",
        "name": "📉 第一次回测",
        "desc": "运行第一次策略回测",
        "icon": "📉",
    },
    "daily_7": {
        "id": "daily_7",
        "name": "📅 连续使用 7 天",
        "desc": "连续 7 天使用 Atlas",
        "icon": "📅",
    },
}


@dataclass
class UserAchievement:
    """用户成就记录器。"""

    storage_dir: Optional[str] = None
    unlocked: Dict[str, str] = field(default_factory=dict)  # id -> 解锁时间

    def _path(self) -> str:
        base = self.storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        return os.path.join(base, "achievements.json")

    def load(self) -> "UserAchievement":
        p = self._path()
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    self.unlocked = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.unlocked = {}
        return self

    def save(self) -> None:
        os.makedirs(os.path.dirname(self._path()), exist_ok=True)
        with open(self._path(), "w", encoding="utf-8") as f:
            json.dump(self.unlocked, f, ensure_ascii=False, indent=2)

    def unlock(self, aid: str) -> bool:
        """解锁成就，返回是否新解锁。"""
        if aid not in ACHIEVEMENTS:
            return False
        if aid in self.unlocked:
            return False
        self.unlocked[aid] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save()
        return True

    def is_unlocked(self, aid: str) -> bool:
        return aid in self.unlocked

    def locked_ids(self) -> List[str]:
        return [aid for aid in ACHIEVEMENTS if aid not in self.unlocked]

    def unlocked_count(self) -> int:
        return len(self.unlocked)

    def total_count(self) -> int:
        return len(ACHIEVEMENTS)

    def newest(self, k: int = 3) -> List[dict]:
        """最近解锁的 k 个成就。"""
        items = sorted(
            ({"id": aid, "time": t, **ACHIEVEMENTS[aid]} for aid, t in self.unlocked.items() if aid in ACHIEVEMENTS),
            key=lambda x: x["time"],
            reverse=True,
        )
        return items[:k]

    def report(self) -> dict:
        return {
            "unlocked": self.unlocked,
            "unlocked_count": self.unlocked_count(),
            "total": self.total_count(),
            "locked": self.locked_ids(),
        }
