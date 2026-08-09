"""user_experiment.reminder_value - 提醒价值统计（v4.9.1 P1）。

重点验证：开奖提醒是否是最大留存钩子（任务书 P1 ④）。

统计：
  reminder_sent                发送提醒次数
  reminder_clicked             点击提醒次数
  draw_checked_after_reminder  收到提醒后查看开奖次数

指标：
  提醒点击率 = reminder_clicked / reminder_sent（目标 ≥30%）
  提醒→查看开奖率 = draw_checked_after_reminder / reminder_sent

存储：~/.atlas/reminder_value_v491.jsonl
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ReminderEvent:
    """一条提醒相关记录。"""

    user_id: str
    kind: str  # sent / clicked / checked_after
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "kind": self.kind,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }


class ReminderValueTracker:
    """提醒价值追踪与统计。"""

    KINDS = ("sent", "clicked", "checked_after")

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "reminder_value_v491.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def _append(self, user_id: str, kind: str,
                metadata: Optional[dict]) -> Optional[ReminderEvent]:
        if kind not in self.KINDS:
            return None
        ev = ReminderEvent(user_id=user_id, kind=kind, metadata=metadata or {})
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return ev

    def sent(self, user_id: str, metadata: Optional[dict] = None) -> Optional[ReminderEvent]:
        return self._append(user_id, "sent", metadata)

    def clicked(self, user_id: str, metadata: Optional[dict] = None) -> Optional[ReminderEvent]:
        return self._append(user_id, "clicked", metadata)

    def checked_after(self, user_id: str, metadata: Optional[dict] = None) -> Optional[ReminderEvent]:
        return self._append(user_id, "checked_after", metadata)

    def all(self) -> List[ReminderEvent]:
        if not os.path.exists(self._path):
            return []
        out: List[ReminderEvent] = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(ReminderEvent(**json.loads(line)))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def counts(self) -> Dict[str, int]:
        c = {k: 0 for k in self.KINDS}
        for e in self.all():
            c[e.kind] = c.get(e.kind, 0) + 1
        return c

    def click_rate(self) -> float:
        """提醒点击率 = clicked / sent（0 分母返回 0.0）。"""
        c = self.counts()
        if c["sent"] == 0:
            return 0.0
        return c["clicked"] / c["sent"]

    def checked_after_rate(self) -> float:
        """提醒→查看开奖率 = checked_after / sent。"""
        c = self.counts()
        if c["sent"] == 0:
            return 0.0
        return c["checked_after"] / c["sent"]

    def per_user(self) -> Dict[str, Dict[str, int]]:
        out: Dict[str, Dict[str, int]] = {}
        for e in self.all():
            row = out.setdefault(e.user_id, {k: 0 for k in self.KINDS})
            row[e.kind] += 1
        return out

    def summary(self) -> dict:
        c = self.counts()
        return {
            "counts": c,
            "click_rate": round(self.click_rate(), 4),
            "checked_after_rate": round(self.checked_after_rate(), 4),
            "users": len(self.per_user()),
            "goal_click_rate": 0.30,
            "click_rate_met": self.click_rate() >= 0.30,
        }

    def export_csv(self, path: Optional[str] = None) -> str:
        out_path = path or os.path.join(self._dir, "reminder_value_v491_export.csv")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "kind", "timestamp", "metadata"])
            writer.writeheader()
            for e in self.all():
                writer.writerow({
                    "user_id": e.user_id, "kind": e.kind,
                    "timestamp": e.timestamp,
                    "metadata": json.dumps(e.metadata, ensure_ascii=False),
                })
        return out_path

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass
