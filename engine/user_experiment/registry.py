"""user_experiment.registry - 种子用户编号体系（v4.9.1 P1）。

为真实用户分配稳定编号 U0001..U0050..（禁止匿名统计），
记录每位用户的基础数据与行为里程碑字段。

字段（任务书 P1 ①）：
  user_id / 注册日期 / 首次打开时间 / 首次保存时间
  / 彩票类型 / 购买频率 / 是否开启提醒 / 是否查看开奖
  / 是否兑奖 / 是否查看资产 / 是否查看周报

存储：~/.atlas/users_v491.jsonl
"""
from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

USER_ID_PREFIX = "U"
USER_ID_PATTERN = re.compile(r"^U\d{4,}$")

# 允许的彩票类型 / 购买频率（避免自由文本污染统计）
LOTTERY_TYPES = ("大乐透", "双色球", "两者都有", "其他")
PURCHASE_FREQUENCIES = ("每周", "每月", "偶尔", "首次")


@dataclass
class ExperimentUser:
    """一位种子用户（REAL）。"""

    user_id: str
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    first_open_at: str = ""
    first_ticket_saved_at: str = ""
    lottery_type: str = ""
    purchase_frequency: str = ""
    reminder_enabled: bool = False
    draw_checked: bool = False
    claim_completed: bool = False
    asset_viewed: bool = False
    weekly_report_viewed: bool = False

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "registered_at": self.registered_at,
            "first_open_at": self.first_open_at,
            "first_ticket_saved_at": self.first_ticket_saved_at,
            "lottery_type": self.lottery_type,
            "purchase_frequency": self.purchase_frequency,
            "reminder_enabled": self.reminder_enabled,
            "draw_checked": self.draw_checked,
            "claim_completed": self.claim_completed,
            "asset_viewed": self.asset_viewed,
            "weekly_report_viewed": self.weekly_report_viewed,
        }


class UserRegistry:
    """种子用户编号注册表（自动分配 U0001+，追加写，CSV 导出）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "users_v491.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def allocate_next_id(self) -> str:
        """分配下一个编号：U0001, U0002, ...（基于现有最大编号）。"""
        max_seq = 0
        for u in self.all():
            m = USER_ID_PATTERN.match(u.user_id)
            if m:
                try:
                    max_seq = max(max_seq, int(u.user_id[1:]))
                except ValueError:
                    continue
        return f"{USER_ID_PREFIX}{max_seq + 1:04d}"

    def register(self, lottery_type: str = "大乐透",
                 purchase_frequency: str = "每周",
                 first_open_at: str = "",
                 registered_at: Optional[str] = None,
                 user_id: Optional[str] = None) -> ExperimentUser:
        """注册一位新用户（未指定编号则自动分配）。"""
        if lottery_type not in LOTTERY_TYPES:
            lottery_type = "其他"
        if purchase_frequency not in PURCHASE_FREQUENCIES:
            purchase_frequency = "首次"
        uid = user_id or self.allocate_next_id()
        user = ExperimentUser(
            user_id=uid,
            registered_at=registered_at or datetime.now().isoformat(timespec="seconds"),
            first_open_at=first_open_at or datetime.now().isoformat(timespec="seconds"),
            lottery_type=lottery_type,
            purchase_frequency=purchase_frequency,
        )
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(user.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return user

    def all(self) -> List[ExperimentUser]:
        if not os.path.exists(self._path):
            return []
        out: List[ExperimentUser] = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        out.append(ExperimentUser(**json.loads(line)))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def get(self, user_id: str) -> Optional[ExperimentUser]:
        for u in self.all():
            if u.user_id == user_id:
                return u
        return None

    def count(self) -> int:
        return len(self.all())

    def mark(self, user_id: str, field_name: str) -> bool:
        """将某行为里程碑置为 True（reminder_enabled/draw_checked 等），并回写文件。"""
        allowed = {
            "reminder_enabled", "draw_checked", "claim_completed",
            "asset_viewed", "weekly_report_viewed",
        }
        if field_name not in allowed:
            return False
        # 重建文件：保留已有用户，更新目标用户
        users = self.all()
        found = False
        new_lines = []
        for u in users:
            if u.user_id == user_id:
                setattr(u, field_name, True)
                found = True
            new_lines.append(u.to_dict())
        if not found:
            return False
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                for d in new_lines:
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
        except OSError:
            return False
        return True

    def set_first_ticket_at(self, user_id: str, ts: str) -> bool:
        """记录首次保存彩票时间。"""
        return self._set_ts(user_id, "first_ticket_saved_at", ts)

    def set_first_open_at(self, user_id: str, ts: str) -> bool:
        return self._set_ts(user_id, "first_open_at", ts)

    def _set_ts(self, user_id: str, field_name: str, ts: str) -> bool:
        users = self.all()
        found = False
        new_lines = []
        for u in users:
            if u.user_id == user_id:
                setattr(u, field_name, ts or datetime.now().isoformat(timespec="seconds"))
                found = True
            new_lines.append(u.to_dict())
        if not found:
            return False
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                for d in new_lines:
                    f.write(json.dumps(d, ensure_ascii=False) + "\n")
        except OSError:
            return False
        return True

    def export_csv(self, path: Optional[str] = None) -> str:
        """导出用户清单 CSV（UTF-8 BOM，Excel 友好）。"""
        out_path = path or os.path.join(self._dir, "users_v491_export.csv")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "user_id", "registered_at", "first_open_at",
                "first_ticket_saved_at", "lottery_type", "purchase_frequency",
                "reminder_enabled", "draw_checked", "claim_completed",
                "asset_viewed", "weekly_report_viewed",
            ])
            writer.writeheader()
            for u in self.all():
                writer.writerow(u.to_dict())
        return out_path

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass
