"""task_context - PendingTaskManager（v3.8.2-P1 Phase 1）。

保存待确认任务上下文，支持用户确认后自动恢复。

字段（任务书要求）：
  user_id / task_type / lottery_type / tickets / purchase_date
  / draw_date / issue / created_time / expire_time

能力（任务书要求）：
  create_task() / get_pending_task() / confirm_task() / clear_task()

确认词（任务书要求）：
  "是" "好的" "确认" "按这个算" → 自动恢复上一任务。
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import List, Optional

# 任务过期时间（分钟）
DEFAULT_EXPIRE_MINUTES = 60

# 确认回复词（短文本精确匹配）
CONFIRM_WORDS = {
    "是", "是的", "是的是的", "嗯", "嗯嗯", "对", "对的", "对对", "可以",
    "好的", "好", "行", "没问题", "没错",
    "确认", "确定", "确认了", "就这么算", "就这样算",
    "按这个算", "按这个开奖算", "按这个",
}

# 否定词（命中即不算确认）
NEGATE_WORDS = {"不", "不是", "不对", "不要", "别", "不行", "不能", "没有", "无需", "不必", "等等", "先别"}

# 归一化：去空白与常见标点
_NORM_RE = re.compile(r"[\s，。！？!?、,.;；:：\"'\"'（）()【】\[\]]")


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _parse_time(s: str) -> Optional[datetime]:
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


@dataclass
class PendingTask:
    """一个待确认任务。"""

    user_id: str
    task_type: str = "prize"            # 任务类型：prize（兑奖）等
    lottery_type: str = "dlt"           # dlt / ssq
    tickets: List[dict] = field(default_factory=list)   # [{"front":[...], "back":[...]}]
    purchase_date: str = ""             # 购买日期 YYYY-MM-DD
    draw_date: str = ""                 # 开奖日期 YYYY-MM-DD
    issue: str = ""                     # 开奖期号
    created_time: str = field(default_factory=_now_str)
    expire_time: str = field(default_factory=lambda: (datetime.now() + timedelta(minutes=DEFAULT_EXPIRE_MINUTES)).strftime("%Y-%m-%d %H:%M:%S"))

    @property
    def note_count(self) -> int:
        return len(self.tickets)

    def is_expired(self, now: Optional[str] = None) -> bool:
        exp = _parse_time(self.expire_time)
        if exp is None:
            return False
        base = _parse_time(now) if now else datetime.now()
        return base >= exp

    def to_dict(self) -> dict:
        return asdict(self)

    def ticket_front_back(self, index: int = 0):
        """第 index 注的前/后区号码。"""
        if 0 <= index < len(self.tickets):
            t = self.tickets[index]
            return list(t.get("front", [])), list(t.get("back", []))
        return [], []


class PendingTaskManager:
    """待确认任务管理器（持久化到本地 JSON，重启可恢复）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        # 优先级：显式目录 > 环境变量（测试/可配置）> 默认 ~/.atlas
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_TASK_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "pending_tasks_v382.json")
        self._tasks: dict = {}   # user_id -> PendingTask
        self._load()

    # ---------- 持久化 ----------
    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    data = json.load(f)
                for uid, d in data.items():
                    keep = {k: v for k, v in d.items() if k in PendingTask.__dataclass_fields__}
                    self._tasks[uid] = PendingTask(**keep)
            except (json.JSONDecodeError, OSError, TypeError):
                self._tasks = {}

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({uid: t.to_dict() for uid, t in self._tasks.items()},
                      f, ensure_ascii=False, indent=2)

    # ---------- 确认词判断 ----------
    @staticmethod
    def normalize(text: str) -> str:
        return _NORM_RE.sub("", (text or "")).strip().lower()

    @staticmethod
    def is_confirm_reply(text: str) -> bool:
        """判断用户回复是否为确认（是/好的/确认/按这个算…）。"""
        t = PendingTaskManager.normalize(text)
        if not t:
            return False
        # 否定词优先
        for n in NEGATE_WORDS:
            if t.startswith(n):
                return False
        # 短回复精确命中
        if len(t) <= 12 and t in CONFIRM_WORDS:
            return True
        # "按8月1日算" / "按2026-08-01开奖计算" → 按...算
        if re.fullmatch(r"按.{1,16}算", t):
            return True
        # "就这么算 / 就这样算"（以 就/这么 开头 + 算 结尾）
        if re.fullmatch(r"(?:就|这么|就这样|就按这个).{0,10}算", t):
            return True
        # "按这个" 结尾（省略"算"的口语）
        if re.fullmatch(r"(?:是|好|行|对|可以|嗯|确认|就)?(?:按这个|这样)", t):
            return True
        # 以确认词开头 + 以 算/这个 结尾 的短回复（"嗯好，就这么算" / "行吧按这个"）
        if (len(t) <= 16
                and any(t.startswith(w) for w in ("是", "好", "行", "对", "可以", "嗯", "确认"))
                and (t.endswith("算") or t.endswith("这个"))):
            return True
        return False

    @staticmethod
    def is_deny_reply(text: str) -> bool:
        """判断用户回复是否为否定（不/别/不是…）。"""
        t = PendingTaskManager.normalize(text)
        if not t:
            return False
        return any(t.startswith(n) for n in NEGATE_WORDS)

    # ---------- 任务 CRUD ----------
    def create_task(self, user_id: str, task_type: str = "prize", lottery_type: str = "dlt",
                    tickets: Optional[List[dict]] = None, purchase_date: str = "",
                    draw_date: str = "", issue: str = "",
                    expire_minutes: int = DEFAULT_EXPIRE_MINUTES) -> PendingTask:
        """创建待确认任务（覆盖同用户旧任务）。"""
        task = PendingTask(
            user_id=user_id, task_type=task_type, lottery_type=lottery_type,
            tickets=list(tickets or []), purchase_date=purchase_date,
            draw_date=draw_date, issue=issue,
            expire_time=(datetime.now() + timedelta(minutes=expire_minutes)).strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._tasks[user_id] = task
        self._save()
        return task

    def get_pending_task(self, user_id: str) -> Optional[PendingTask]:
        """取用户待确认任务（过期自动清除）。"""
        task = self._tasks.get(user_id)
        if task is None:
            return None
        if task.is_expired():
            self._tasks.pop(user_id, None)
            self._save()
            return None
        return task

    def has_pending(self, user_id: str) -> bool:
        return self.get_pending_task(user_id) is not None

    def confirm_task(self, user_id: str) -> Optional[PendingTask]:
        """确认并取走任务（一次性：返回后清除）。"""
        task = self.get_pending_task(user_id)
        if task is None:
            return None
        self._tasks.pop(user_id, None)
        self._save()
        return task

    def clear_task(self, user_id: str) -> bool:
        """清除用户任务。"""
        if user_id in self._tasks:
            del self._tasks[user_id]
            self._save()
            return True
        return False

    def list_all(self) -> List[PendingTask]:
        """全部未过期任务。"""
        out = []
        for uid in list(self._tasks.keys()):
            t = self.get_pending_task(uid)
            if t is not None:
                out.append(t)
        return out

    def count(self) -> int:
        return len(self.list_all())
