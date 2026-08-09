"""backend.mobile.service - Mobile MVP 业务服务层（可测试核心）。

职责：
  1. 号码解析（普通格式 / 连续格式，含范围校验）
  2. 录票（保存 + 期号推断 + 埋点）
  3. 开奖匹配（票 vs 开奖 → 中奖状态）
  4. 提醒调度（创建 / 下发 / 点击回执）
  5. 用户漏斗统计
  6. 埋点记录（source=MOBILE）

依赖：只依赖 Repository 层（不直接操作数据库）。
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from backend.mobile.repositories import (
    BehaviorEventRepository,
    DrawRepository,
    ReminderRepository,
    TicketRepository,
    UserRepository,
)

# 彩种配置：彩种 → (前区范围, 后区范围, 前区个数, 后区个数)
LOTTERY_CONFIG = {
    "dlt": ((1, 35), (1, 12), 5, 2),   # 大乐透
    "ssq": ((1, 33), (1, 16), 6, 1),   # 双色球
}

# 事件集（与 engine/user_experiment/events.py 对齐 + mobile 事件）
EVENT_MOBILE_OPENED = "mobile_opened"
EVENT_MOBILE_TICKET_SAVED = "mobile_ticket_saved"
EVENT_MOBILE_REMINDER_ENABLED = "mobile_reminder_enabled"
EVENT_MOBILE_DRAW_VIEWED = "mobile_draw_viewed"
EVENT_MOBILE_FEEDBACK_SUBMITTED = "mobile_feedback_submitted"

MOBILE_EVENTS = (
    EVENT_MOBILE_OPENED,
    EVENT_MOBILE_TICKET_SAVED,
    EVENT_MOBILE_REMINDER_ENABLED,
    EVENT_MOBILE_DRAW_VIEWED,
    EVENT_MOBILE_FEEDBACK_SUBMITTED,
)

# 奖级定义（大乐透：前区命中数, 后区命中数）→ (奖级, 奖金)
# 注意：八等奖/九等奖各有多个命中组合（官方规则）。
DLT_PRIZE_TABLE = [
    ((5, 2), "一等奖", 10000000),
    ((5, 1), "二等奖", 500000),
    ((5, 0), "三等奖", 10000),
    ((4, 2), "四等奖", 3000),
    ((4, 1), "五等奖", 300),
    ((3, 2), "六等奖", 200),
    ((4, 0), "七等奖", 100),
    ((3, 1), "八等奖", 15),
    ((2, 2), "八等奖", 15),
    ((3, 0), "九等奖", 5),
    ((1, 2), "九等奖", 5),
    ((2, 1), "九等奖", 5),
    ((0, 2), "九等奖", 5),
]


class MobileTicketParser:
    """号码解析：支持 '01 05 12 23 30 + 06 08' 与连续格式。"""

    @staticmethod
    def parse(text: str, lottery: str = "dlt") -> Optional[Tuple[List[int], List[int]]]:
        """解析一行号码 → (front, back)；非法返回 None。"""
        if lottery not in LOTTERY_CONFIG:
            return None
        (fr_lo, fr_hi), (ba_lo, ba_hi), fr_n, ba_n = LOTTERY_CONFIG[lottery]

        # 统一分隔符
        t = text.strip().replace("，", ",").replace("＋", "+").replace("|", "+")
        # 连续格式（纯数字长度 = (fr_n+ba_n)*2）
        digits = re.sub(r"[^0-9]", "", t)
        if len(digits) == (fr_n + ba_n) * 2 and not re.search(r"[+\s,]", t):
            front = [int(digits[i * 2:(i + 1) * 2]) for i in range(fr_n)]
            back = [int(digits[(fr_n + i) * 2:(fr_n + i + 1) * 2]) for i in range(ba_n)]
            return MobileTicketParser._validate(front, back, lottery)

        # 分隔格式
        parts = re.split(r"[+\s,]+", t)
        parts = [p for p in parts if p.strip()]
        if len(parts) != fr_n + ba_n:
            return None
        try:
            nums = [int(p) for p in parts]
        except ValueError:
            return None
        front = nums[:fr_n]
        back = nums[fr_n:]
        return MobileTicketParser._validate(front, back, lottery)

    @staticmethod
    def _validate(front: List[int], back: List[int], lottery: str) -> Optional[Tuple[List[int], List[int]]]:
        (fr_lo, fr_hi), (ba_lo, ba_hi), fr_n, ba_n = LOTTERY_CONFIG[lottery]
        if len(front) != fr_n or len(back) != ba_n:
            return None
        if len(set(front)) != fr_n or len(set(back)) != ba_n:
            return None  # 重复号码
        if any(not (fr_lo <= x <= fr_hi) for x in front):
            return None
        if any(not (ba_lo <= x <= ba_hi) for x in back):
            return None
        return sorted(front), sorted(back)


class DrawMatcher:
    """开奖匹配：一张票 vs 一期开奖 → 中奖状态。"""

    @staticmethod
    def match(ticket_front: List[int], ticket_back: List[int],
              draw_front: List[int], draw_back: List[int]) -> Dict[str, Any]:
        front_hit = len(set(ticket_front) & set(draw_front))
        back_hit = len(set(ticket_back) & set(draw_back))
        for key, level, amount in DLT_PRIZE_TABLE:
            if (front_hit, back_hit) == key:
                return {
                    "front_hit": front_hit, "back_hit": back_hit,
                    "won": True, "level": level, "amount": float(amount),
                }
        return {
            "front_hit": front_hit, "back_hit": back_hit,
            "won": False, "level": None, "amount": 0.0,
        }


class MobileService:
    """Mobile MVP 业务服务。"""

    def __init__(self, session):
        self.users = UserRepository(session)
        self.tickets = TicketRepository(session)
        self.draws = DrawRepository(session)
        self.reminders = ReminderRepository(session)
        self.events = BehaviorEventRepository(session)
        self._session = session

    # ---- 用户 ----
    # 允许值（与 registry.py 一致，禁止自由文本污染统计）
    ALLOWED_LOTTERY_TYPES = ("大乐透", "双色球", "两者都有", "其他")
    ALLOWED_FREQUENCIES = ("每周", "每月", "偶尔", "首次")

    def _normalize(self, lottery_type: str, purchase_frequency: str):
        if lottery_type not in self.ALLOWED_LOTTERY_TYPES:
            lottery_type = "其他"
        if purchase_frequency not in self.ALLOWED_FREQUENCIES:
            purchase_frequency = "首次"
        return lottery_type, purchase_frequency

    def register_or_get(self, openid: str, lottery_type: str = "大乐透",
                        purchase_frequency: str = "每周") -> Any:
        """微信授权登录：openid → 已有返回，无则注册。"""
        lottery_type, purchase_frequency = self._normalize(lottery_type, purchase_frequency)
        user = self.users.get_by_openid(openid)
        if user is not None:
            return user
        return self.users.create(openid, lottery_type, purchase_frequency)

    # ---- 录票 ----
    def save_ticket(self, user_id: str, lottery: str, text: str,
                    buy_date: str = "", draw_date: str = "") -> Dict[str, Any]:
        """解析并保存一张票；非法号码抛 ValueError。"""
        parsed = MobileTicketParser.parse(text, lottery)
        if parsed is None:
            raise ValueError("号码格式错误或越界")
        front, back = parsed
        ticket = self.tickets.create(
            user_id=user_id, lottery=lottery, front=front, back=back,
            buy_date=buy_date, draw_date=draw_date,
        )
        # 埋点
        self.events.record(EVENT_MOBILE_TICKET_SAVED, user_id, source="MOBILE",
                           metadata={"ticket_id": ticket.ticket_id, "lottery": lottery})
        # 里程碑：首次保存
        user = self.users.get(user_id)
        if user is not None and not user.first_ticket_saved_at:
            self.users.set_first_ticket_at(user_id, datetime.now().isoformat(timespec="seconds"))
        return {
            "ticket_id": ticket.ticket_id,
            "front": front, "back": back,
            "draw_date": draw_date,
        }

    def list_tickets(self, user_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "ticket_id": t.ticket_id, "lottery": t.lottery,
                "front": t.front, "back": t.back, "cost": t.cost,
                "buy_date": t.buy_date, "draw_date": t.draw_date,
                "issue": t.issue, "claimed": t.claimed,
            }
            for t in self.tickets.list_by_user(user_id)
        ]

    # ---- 开奖 ----
    def check_ticket(self, user_id: str, ticket_id: str, issue: str) -> Dict[str, Any]:
        """用指定期号核对一张票。"""
        ticket = self.tickets.get(ticket_id)
        if ticket is None or ticket.user_id != user_id:
            return {"ok": False, "reason": "not_found"}
        draw = self.draws.get(issue)
        if draw is None:
            return {"ok": False, "reason": "draw_not_found"}
        result = DrawMatcher.match(ticket.front, ticket.back, draw.front, draw.back)
        self.events.record(EVENT_MOBILE_DRAW_VIEWED, user_id, source="MOBILE",
                           metadata={"ticket_id": ticket_id, "issue": issue})
        return {"ok": True, "result": result, "issue": issue}

    def latest_draw(self, lottery: str) -> Optional[Dict[str, Any]]:
        draw = self.draws.latest(lottery)
        if draw is None:
            return None
        return {"issue": draw.issue, "front": draw.front, "back": draw.back, "draw_date": draw.draw_date}

    # ---- 提醒 ----
    def create_reminder(self, user_id: str, ticket_id: str, issue: str,
                        remind_at: str = "") -> Dict[str, Any]:
        """创建开奖提醒（去重）。"""
        if self.reminders.exists(user_id, ticket_id, issue):
            return {"ok": True, "duplicated": True}
        r = self.reminders.create(user_id, ticket_id, issue, remind_at)
        self.events.record(EVENT_MOBILE_REMINDER_ENABLED, user_id, source="MOBILE",
                           metadata={"reminder_id": r.id, "issue": issue})
        self.users.mark(user_id, "reminder_enabled")
        return {"ok": True, "duplicated": False, "reminder_id": r.id}

    def mark_reminder_clicked(self, reminder_id: str) -> bool:
        return self.reminders.mark_clicked(reminder_id)

    # ---- 漏斗 ----
    def funnel(self) -> Dict[str, int]:
        """用户漏斗：注册 → 首存 → 开提醒 → 查开奖。"""
        users = self.users.all()
        total = len(users)
        first_saved = sum(1 for u in users if u.first_ticket_saved_at)
        reminder_on = sum(1 for u in users if u.reminder_enabled)
        draw_checked = sum(1 for u in users if u.draw_checked)
        return {
            "registered": total,
            "first_ticket_saved": first_saved,
            "reminder_enabled": reminder_on,
            "draw_checked": draw_checked,
        }

    def save_rate(self) -> float:
        """首次保存率 = first_ticket_saved / registered。"""
        f = self.funnel()
        if f["registered"] == 0:
            return 0.0
        return round(f["first_ticket_saved"] / f["registered"], 4)

    # ---- 埋点 ----
    def track(self, event_name: str, user_id: str, source: str = "MOBILE",
              metadata: Optional[Dict[str, Any]] = None) -> bool:
        if event_name not in MOBILE_EVENTS and event_name not in (
            "app_install", "app_open", "onboarding_start", "ticket_saved",
            "reminder_enabled", "reminder_sent", "draw_reminder_clicked",
            "draw_checked", "claim_checked", "claim_completed", "asset_viewed",
            "report_viewed", "weekly_report_viewed", "premium_view", "premium_click",
            "weekly_return",
        ):
            return False
        self.events.record(event_name, user_id, source=source, metadata=metadata)
        return True
