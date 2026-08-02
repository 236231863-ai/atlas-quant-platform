"""beta - Beta 用户管理（BetaUserManager）。

管理 Beta 测试用户：
  - 用户编号（自动分配 BETA-0001...）
  - 测试批次（batch 1/2/3）
  - 版本记录（用户使用的版本）
  - 反馈状态（feedback status）

输出：BetaUserReport（汇总用户/批次/版本/反馈统计）。
"""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

BATCHES = {"1", "2", "3"}
FEEDBACK_STATUSES = {"none", "new", "reviewing", "fixed", "closed"}


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class BetaUser:
    """一个 Beta 用户。"""

    user_id: str
    name: str = ""
    batch: str = "1"
    version: str = "v3.7.1-beta"
    join_date: str = ""
    last_active: str = ""
    feedback_status: str = "none"  # none/new/reviewing/fixed/closed
    feedback_count: int = 0
    notes: str = ""


class BetaUserManager:
    """Beta 用户管理器（本地 JSON 存储）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "beta_users.json")
        self._users: Dict[str, BetaUser] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    data = json.load(f)
                for uid, d in data.items():
                    self._users[uid] = BetaUser(**{k: v for k, v in d.items() if k in BetaUser.__dataclass_fields__})
            except (json.JSONDecodeError, OSError):
                self._users = {}

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({uid: u.__dict__ for uid, u in self._users.items()}, f, ensure_ascii=False, indent=2)

    # ---- 用户操作 ----
    def register(self, name: str = "", batch: str = "1", version: str = "v3.7.1-beta") -> BetaUser:
        """注册新用户，自动分配编号。"""
        if batch not in BATCHES:
            batch = "1"
        uid = f"BETA-{len(self._users) + 1:04d}"
        # 避免重复（用短随机后缀保证唯一）
        while uid in self._users:
            uid = f"BETA-{len(self._users) + 1:04d}"
        user = BetaUser(
            user_id=uid, name=name, batch=batch, version=version,
            join_date=_now(), last_active=_now(),
        )
        self._users[uid] = user
        self._save()
        return user

    def get(self, user_id: str) -> Optional[BetaUser]:
        return self._users.get(user_id)

    def exists(self, user_id: str) -> bool:
        return user_id in self._users

    def update_version(self, user_id: str, version: str) -> bool:
        u = self._users.get(user_id)
        if not u:
            return False
        u.version = version
        u.last_active = _now()
        self._save()
        return True

    def touch(self, user_id: str) -> bool:
        u = self._users.get(user_id)
        if not u:
            return False
        u.last_active = _now()
        self._save()
        return True

    def set_feedback_status(self, user_id: str, status: str) -> bool:
        if status not in FEEDBACK_STATUSES:
            return False
        u = self._users.get(user_id)
        if not u:
            return False
        u.feedback_status = status
        if status in ("new", "reviewing", "fixed", "closed"):
            u.feedback_count += 1
        self._save()
        return True

    def all(self) -> List[BetaUser]:
        return list(self._users.values())

    def count(self) -> int:
        return len(self._users)

    def by_batch(self, batch: str) -> List[BetaUser]:
        return [u for u in self._users.values() if u.batch == batch]

    def clear(self) -> None:
        self._users = {}
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass

    # ---- 报告 ----
    def report(self) -> dict:
        users = self.all()
        from collections import Counter
        batch_counter = Counter(u.batch for u in users)
        version_counter = Counter(u.version for u in users)
        status_counter = Counter(u.feedback_status for u in users)
        active = sum(1 for u in users if u.last_active)
        return {
            "total_users": len(users),
            "by_batch": dict(batch_counter),
            "by_version": dict(version_counter),
            "by_feedback_status": dict(status_counter),
            "active_users": active,
            "feedback_total": sum(u.feedback_count for u in users),
            "latest_join": max((u.join_date for u in users), default=""),
        }
