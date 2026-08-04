"""draw_monitor.reminder_schedule - 开奖提醒计划（v4.6 P2）。

关闭 Atlas 后，Task Scheduler 唤起 worker 时按提醒计划发送：
  - 开奖前 24h 提醒（距开奖 <=24h 且 >3h，每天一次）
  - 开奖前 3h 提醒（距开奖 <=3h）
  - 开奖后自动兑奖提醒（draw_updated 已触发，此处计算文案）

去重：同类型提醒当天只发一次（~/.atlas/reminder_sent.json）
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Optional

DRAW_TIME_HOUR = 20  # 默认开奖时间 20:30，简化为 20 点计算

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class ReminderPlan:
    """一个提醒计划项。"""

    lottery: str
    kind: str            # pre_24h / pre_3h / after_draw
    due_at: str          # 计划触发时间 ISO
    title: str
    message: str

    def to_dict(self) -> dict:
        return {"lottery": self.lottery, "kind": self.kind,
                "due_at": self.due_at, "title": self.title,
                "message": self.message}


class ReminderScheduler:
    """计算何时发什么提醒。"""

    @staticmethod
    def _next_draw_datetime(lottery: str, from_date: Optional[date] = None) -> Optional[datetime]:
        """下一开奖的具体时间（开奖日 20:00 基准）。"""
        from engine.ticket_system.schedule import LotterySchedule
        from_date = from_date or date.today()
        nxt = LotterySchedule.next_draw_date(lottery, from_date.isoformat())
        if not nxt:
            return None
        return datetime.strptime(nxt, "%Y-%m-%d").replace(hour=DRAW_TIME_HOUR)

    @classmethod
    def build_plan(cls, lottery: str, now: Optional[datetime] = None) -> List[ReminderPlan]:
        """构建今日提醒计划（应发的提醒）。"""
        now = now or datetime.now()
        nxt = cls._next_draw_datetime(lottery, now.date())
        plans = []
        if not nxt:
            return plans
        delta = (nxt - now).total_seconds() / 3600
        name = LOTTERY_NAMES.get(lottery, lottery)

        if delta <= 0:
            # 开奖后（当天）：兑奖提醒（draw_updated 由 monitor 处理）
            plans.append(ReminderPlan(
                lottery, "after_draw", now.isoformat(timespec="seconds"),
                f"🎯 {name}已开奖",
                f"{name}最新开奖已更新，打开 Atlas 自动兑奖"))
        elif delta <= 3:
            plans.append(ReminderPlan(
                lottery, "pre_3h", now.isoformat(timespec="seconds"),
                f"⏰ {name}即将开奖",
                f"{name}距开奖不到 3 小时，别忘了查看你的彩票"))
        elif delta <= 24:
            plans.append(ReminderPlan(
                lottery, "pre_24h", now.isoformat(timespec="seconds"),
                f"📅 {name}明日开奖",
                f"{name}明天开奖（{nxt.date()}），你有彩票待确认"))
        return plans

    # ---------- 去重 ----------
    @classmethod
    def _sent_path(cls, storage_dir: Optional[str] = None) -> str:
        d = (storage_dir or os.environ.get("ATLAS_STORAGE_DIR")
             or os.path.join(os.path.expanduser("~"), ".atlas"))
        return os.path.join(d, "reminder_sent.json")

    @classmethod
    def _load_sent(cls, storage_dir: Optional[str] = None) -> dict:
        p = cls._sent_path(storage_dir)
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    @classmethod
    def _mark_sent(cls, key: str, storage_dir: Optional[str] = None) -> None:
        sent = cls._load_sent(storage_dir)
        sent[key] = date.today().isoformat()
        try:
            os.makedirs(os.path.dirname(cls._sent_path(storage_dir)), exist_ok=True)
            with open(cls._sent_path(storage_dir), "w", encoding="utf-8") as f:
                json.dump(sent, f, ensure_ascii=False)
        except OSError:
            pass

    @classmethod
    def already_sent(cls, lottery: str, kind: str,
                     storage_dir: Optional[str] = None) -> bool:
        """今天是否已发过该类提醒。"""
        sent = cls._load_sent(storage_dir)
        return sent.get(f"{lottery}:{kind}") == date.today().isoformat()

    @classmethod
    def due_reminders(cls, lottery: str, now: Optional[datetime] = None,
                      storage_dir: Optional[str] = None) -> List[ReminderPlan]:
        """应发且未发过的提醒。"""
        plans = cls.build_plan(lottery, now)
        due = []
        for p in plans:
            if not cls.already_sent(p.lottery, p.kind, storage_dir):
                due.append(p)
        return due

    @classmethod
    def mark_reminders_sent(cls, plans: List[ReminderPlan],
                            storage_dir: Optional[str] = None) -> None:
        for p in plans:
            cls._mark_sent(f"{p.lottery}:{p.kind}", storage_dir)
