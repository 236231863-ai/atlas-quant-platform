"""user_experiment.feedback - 真实用户反馈问卷（v4.9 P3）。

两问问卷（最小采集，非功能扩展）：
  Q1 你为什么使用 Atlas？    （自动提醒/自动兑奖/管理投入/查看历史/其他）
  Q2 你为什么可能卸载？      （没必要/操作复杂/没中奖/提醒无用/数据问题）

数据标记 REAL_USER（真实用户），禁止与模拟混用。
存储：~/.atlas/feedback_v49.jsonl
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

USE_REASONS = ("自动提醒", "自动兑奖", "管理投入", "查看历史", "其他")
UNINSTALL_REASONS = ("没必要", "操作复杂", "没中奖", "提醒无用", "数据问题", "其他")


@dataclass
class UserFeedback:
    """一条真实用户反馈。"""

    user_id: str
    use_reason: str
    uninstall_reason: str = ""
    experiment_id: str = "real_users"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class UserFeedbackSurvey:
    """真实用户反馈问卷采集与统计。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "feedback_v49.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def submit(self, user_id: str, use_reason: str,
               uninstall_reason: str = "",
               experiment_id: str = "real_users") -> Optional[UserFeedback]:
        """提交一条真实用户反馈（真实用户专用）。"""
        if use_reason not in USE_REASONS and use_reason != "其他":
            return None
        if uninstall_reason and uninstall_reason not in UNINSTALL_REASONS:
            return None
        fb = UserFeedback(user_id=user_id, use_reason=use_reason,
                          uninstall_reason=uninstall_reason,
                          experiment_id=experiment_id)
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(fb.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return fb

    def all(self) -> List[UserFeedback]:
        if not os.path.exists(self._path):
            return []
        out = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(UserFeedback(**json.loads(line)))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def count(self) -> int:
        return len(self.all())

    def distribution(self, field: str) -> Dict[str, int]:
        """统计某字段分布（use_reason / uninstall_reason）。"""
        out: Dict[str, int] = {}
        for fb in self.all():
            val = getattr(fb, field, "")
            if val:
                out[val] = out.get(val, 0) + 1
        return out

    def top_use_reason(self) -> str:
        d = self.distribution("use_reason")
        return max(d, key=d.get) if d else "（暂无反馈）"

    def top_uninstall_reason(self) -> str:
        d = self.distribution("uninstall_reason")
        return max(d, key=d.get) if d else "（暂无反馈）"

    def summary(self) -> dict:
        return {
            "total": self.count(),
            "use_reasons": self.distribution("use_reason"),
            "uninstall_reasons": self.distribution("uninstall_reason"),
            "top_use": self.top_use_reason(),
            "top_uninstall": self.top_uninstall_reason(),
        }

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass
