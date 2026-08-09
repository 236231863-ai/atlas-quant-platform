"""user_experiment.daily_log - 每日实验记录（v4.9.1 P1）。

产品负责人每天记录实验进展（任务书 P1 ③）：
  日期 / 新增用户 / 首次打开 / 保存彩票 / 提醒开启
  / 开奖查看 / 兑奖完成 / 资产查看 / 周报查看 / 反馈数量

存储：~/.atlas/daily_log_v491.jsonl
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# 每日记录字段（任务书固定顺序）
DAILY_LOG_FIELDS = (
    "date", "new_users", "first_open", "ticket_saved", "reminder_enabled",
    "draw_checked", "claim_completed", "asset_viewed",
    "weekly_report_viewed", "feedback_count",
)


@dataclass
class DailyLogEntry:
    """一天的实验记录。"""

    date: str  # YYYY-MM-DD
    new_users: int = 0
    first_open: int = 0
    ticket_saved: int = 0
    reminder_enabled: int = 0
    draw_checked: int = 0
    claim_completed: int = 0
    asset_viewed: int = 0
    weekly_report_viewed: int = 0
    feedback_count: int = 0

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in DAILY_LOG_FIELDS}

    def total_actions(self) -> int:
        return (self.new_users + self.first_open + self.ticket_saved
                + self.reminder_enabled + self.draw_checked
                + self.claim_completed + self.asset_viewed
                + self.weekly_report_viewed + self.feedback_count)


class DailyExperimentLog:
    """每日实验记录（追加写 + 按日累加 + CSV 导出）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "daily_log_v491.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def today(self) -> str:
        return datetime.now().strftime("%Y-%m-%d")

    def record(self, date: Optional[str] = None, **counts) -> DailyLogEntry:
        """记录/累加某天的计数（同名 key 累加）。"""
        date = date or self.today()
        entries = self.all()
        entry = next((e for e in entries if e.date == date),
                     DailyLogEntry(date=date))
        for k, v in counts.items():
            if k in DAILY_LOG_FIELDS and k != "date" and isinstance(v, int):
                setattr(entry, k, getattr(entry, k) + v)
        # 移除旧条目，追加更新后的条目
        entries = [e for e in entries if e.date != date]
        entries.append(entry)
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                for e in sorted(entries, key=lambda x: x.date):
                    f.write(json.dumps(e.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return entry

    def all(self) -> List[DailyLogEntry]:
        if not os.path.exists(self._path):
            return []
        out: List[DailyLogEntry] = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(DailyLogEntry(**json.loads(line)))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return sorted(out, key=lambda x: x.date)

    def get(self, date: str) -> Optional[DailyLogEntry]:
        for e in self.all():
            if e.date == date:
                return e
        return None

    def summary(self) -> dict:
        """14 天实验汇总（用于报告）。"""
        entries = self.all()
        total: Dict[str, int] = {k: 0 for k in DAILY_LOG_FIELDS if k != "date"}
        active_days = 0
        for e in entries:
            active_days += 1
            for k in total:
                total[k] += getattr(e, k)
        return {
            "days": active_days,
            "date_range": (entries[0].date, entries[-1].date) if entries else ("", ""),
            "totals": total,
        }

    def export_csv(self, path: Optional[str] = None) -> str:
        out_path = path or os.path.join(self._dir, "daily_log_v491_export.csv")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=DAILY_LOG_FIELDS)
            writer.writeheader()
            for e in self.all():
                writer.writerow(e.to_dict())
        return out_path

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass
