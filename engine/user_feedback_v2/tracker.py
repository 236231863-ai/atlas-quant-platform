"""user_feedback_v2 - 用户行为追踪。

记录（本地，隐私友好）：
  - page_view     : 页面访问
  - feature_use   : 功能使用
  - report_export : 报告导出
  - strategy_view : 策略查看
  - preference    : 用户偏好

存储：~/.atlas/behavior.jsonl（追加式 JSON Lines）。
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# 合法事件类型
EVENT_TYPES = {"page_view", "feature_use", "report_export", "strategy_view", "preference"}


class UserFeedbackTracker:
    """本地用户行为追踪器。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "behavior.jsonl")

    def _ensure_dir(self) -> None:
        os.makedirs(self._dir, exist_ok=True)

    def record(self, event_type: str, **data) -> bool:
        """记录一条事件。返回是否成功。"""
        if event_type not in EVENT_TYPES:
            return False
        self._ensure_dir()
        entry = {
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            **data,
        }
        try:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return True
        except OSError:
            return False

    def page_view(self, page: str) -> bool:
        return self.record("page_view", page=page)

    def feature_use(self, feature: str, **extra) -> bool:
        return self.record("feature_use", feature=feature, **extra)

    def report_export(self, fmt: str, kind: str = "report") -> bool:
        return self.record("report_export", fmt=fmt, kind=kind)

    def strategy_view(self, strategy: str) -> bool:
        return self.record("strategy_view", strategy=strategy)

    def set_preference(self, key: str, value) -> bool:
        return self.record("preference", key=key, value=value)

    def load(self, limit: Optional[int] = None) -> List[dict]:
        """读取全部事件（按时间升序）。"""
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
        """清空事件（测试/重置用）。"""
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass
