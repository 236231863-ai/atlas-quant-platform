"""backend.mobile.repositories - Repository 层（强制，禁止业务代码直连数据库）。

每个 Repository 封装一种实体的全部持久化操作。
业务服务（service.py）与 API（api.py）只依赖 Repository 接口。
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Protocol

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from backend.mobile.models import (
    MobileBehaviorEvent,
    MobileDraw,
    MobileReminder,
    MobileTicket,
    MobileUser,
)

# 用户编号正则（与 engine/user_experiment/registry.py 一致）
USER_ID_PATTERN = "^U\\d{4,}$"


class _BaseRepo:
    """Repository 公共基类。"""

    def __init__(self, session: Session) -> None:
        self._s = session


# ---- User Repository ----
class UserRepository(_BaseRepo):
    """用户表 Repository。"""

    def get(self, user_id: str) -> Optional[MobileUser]:
        return self._s.get(MobileUser, user_id)

    def get_by_openid(self, openid: str) -> Optional[MobileUser]:
        stmt = select(MobileUser).where(MobileUser.openid == openid)
        return self._s.execute(stmt).scalar_one_or_none()

    def all(self) -> List[MobileUser]:
        return list(self._s.execute(select(MobileUser).order_by(MobileUser.user_id)).scalars())

    def count(self) -> int:
        return len(self.all())

    def next_user_id(self) -> str:
        """分配下一个编号：U0001, U0002, ...（基于现有最大编号）。"""
        import re

        max_seq = 0
        for u in self.all():
            m = re.match(USER_ID_PATTERN, u.user_id)
            if m:
                max_seq = max(max_seq, int(u.user_id[1:]))
        return f"U{max_seq + 1:04d}"

    def create(self, openid: str, lottery_type: str = "大乐透",
               purchase_frequency: str = "每周") -> MobileUser:
        user = MobileUser(
            user_id=self.next_user_id(),
            openid=openid,
            lottery_type=lottery_type,
            purchase_frequency=purchase_frequency,
        )
        self._s.add(user)
        self._s.commit()
        return user

    def save(self, user: MobileUser) -> MobileUser:
        self._s.add(user)
        self._s.commit()
        return user

    def mark(self, user_id: str, field: str) -> bool:
        """将行为里程碑字段置 True。"""
        allowed = {
            "reminder_enabled", "draw_checked", "claim_completed",
            "asset_viewed", "weekly_report_viewed",
        }
        if field not in allowed:
            return False
        user = self.get(user_id)
        if user is None:
            return False
        setattr(user, field, True)
        self._s.commit()
        return True

    def set_first_ticket_at(self, user_id: str, ts: str) -> bool:
        user = self.get(user_id)
        if user is None:
            return False
        user.first_ticket_saved_at = ts
        self._s.commit()
        return True


# ---- Ticket Repository ----
class TicketRepository(_BaseRepo):
    """彩票表 Repository。"""

    def get(self, ticket_id: str) -> Optional[MobileTicket]:
        return self._s.get(MobileTicket, ticket_id)

    def list_by_user(self, user_id: str) -> List[MobileTicket]:
        stmt = (
            select(MobileTicket)
            .where(MobileTicket.user_id == user_id)
            .order_by(MobileTicket.buy_date)
        )
        return list(self._s.execute(stmt).scalars())

    def count_by_user(self, user_id: str) -> int:
        return len(self.list_by_user(user_id))

    def next_ticket_id(self) -> str:
        import re

        max_seq = 0
        stmt = select(MobileTicket.ticket_id)
        for (tid,) in self._s.execute(stmt).all():
            m = re.match(r"^T(\d{4,})$", tid)
            if m:
                max_seq = max(max_seq, int(m.group(1)))
        return f"T{max_seq + 1:04d}"

    def create(self, user_id: str, lottery: str, front: List[int],
               back: List[int], cost: float = 2.0, buy_date: str = "",
               draw_date: str = "", issue: str = "") -> MobileTicket:
        ticket = MobileTicket(
            ticket_id=self.next_ticket_id(),
            user_id=user_id,
            lottery=lottery,
            front=front,
            back=back,
            cost=cost,
            buy_date=buy_date,
            draw_date=draw_date,
            issue=issue,
        )
        self._s.add(ticket)
        self._s.commit()
        return ticket

    def save(self, ticket: MobileTicket) -> MobileTicket:
        self._s.add(ticket)
        self._s.commit()
        return ticket

    def delete(self, ticket_id: str) -> bool:
        stmt = delete(MobileTicket).where(MobileTicket.ticket_id == ticket_id)
        self._s.execute(stmt)
        self._s.commit()
        return True

    def list_by_issue(self, issue: str) -> List[MobileTicket]:
        stmt = select(MobileTicket).where(MobileTicket.issue == issue)
        return list(self._s.execute(stmt).scalars())

    def list_pending_draw(self) -> List[MobileTicket]:
        """开奖日期在 3 天内且尚未匹配期号的票（提醒候选）。"""
        stmt = select(MobileTicket).where(MobileTicket.issue == "")
        return list(self._s.execute(stmt).scalars())


# ---- Draw Repository ----
class DrawRepository(_BaseRepo):
    """开奖表 Repository。"""

    def get(self, issue: str) -> Optional[MobileDraw]:
        return self._s.get(MobileDraw, issue)

    def latest(self, lottery: str) -> Optional[MobileDraw]:
        stmt = (
            select(MobileDraw)
            .where(MobileDraw.lottery == lottery)
            .order_by(MobileDraw.issue.desc())
            .limit(1)
        )
        return self._s.execute(stmt).scalar_one_or_none()

    def list_recent(self, lottery: str, limit: int = 20) -> List[MobileDraw]:
        stmt = (
            select(MobileDraw)
            .where(MobileDraw.lottery == lottery)
            .order_by(MobileDraw.issue.desc())
            .limit(limit)
        )
        return list(self._s.execute(stmt).scalars())

    def upsert(self, issue: str, lottery: str, front: List[int],
               back: List[int], draw_date: str = "") -> MobileDraw:
        draw = self.get(issue)
        if draw is None:
            draw = MobileDraw(issue=issue, lottery=lottery, front=front, back=back, draw_date=draw_date)
            self._s.add(draw)
        else:
            draw.lottery = lottery
            draw.front = front
            draw.back = back
            draw.draw_date = draw_date
        self._s.commit()
        return draw

    def count(self) -> int:
        return len(list(self._s.execute(select(MobileDraw)).scalars()))


# ---- Reminder Repository ----
class ReminderRepository(_BaseRepo):
    """提醒表 Repository。"""

    def create(self, user_id: str, ticket_id: str, issue: str,
               remind_at: str = "") -> MobileReminder:
        r = MobileReminder(user_id=user_id, ticket_id=ticket_id, issue=issue, remind_at=remind_at)
        self._s.add(r)
        self._s.commit()
        return r

    def get(self, rid: str) -> Optional[MobileReminder]:
        return self._s.get(MobileReminder, rid)

    def exists(self, user_id: str, ticket_id: str, issue: str) -> bool:
        stmt = select(MobileReminder.id).where(
            MobileReminder.user_id == user_id,
            MobileReminder.ticket_id == ticket_id,
            MobileReminder.issue == issue,
        )
        return self._s.execute(stmt).first() is not None

    def list_unsent(self) -> List[MobileReminder]:
        stmt = select(MobileReminder).where(MobileReminder.sent == False)  # noqa: E712
        return list(self._s.execute(stmt).scalars())

    def mark_sent(self, rid: str) -> bool:
        stmt = update(MobileReminder).where(MobileReminder.id == rid).values(sent=True)
        self._s.execute(stmt)
        self._s.commit()
        return True

    def mark_clicked(self, rid: str) -> bool:
        stmt = update(MobileReminder).where(MobileReminder.id == rid).values(clicked=True)
        self._s.execute(stmt)
        self._s.commit()
        return True

    def count(self) -> int:
        return len(list(self._s.execute(select(MobileReminder)).scalars()))

    def click_rate(self) -> float:
        """提醒点击率 = clicked / sent（0 分母时返回 0.0）。"""
        sent = len(list(self._s.execute(select(MobileReminder)).scalars()))
        clicked = len(list(self._s.execute(select(MobileReminder).where(MobileReminder.clicked == True)).scalars()))  # noqa: E712
        if sent == 0:
            return 0.0
        return round(clicked / sent, 4)


# ---- Behavior Event Repository ----
class BehaviorEventRepository(_BaseRepo):
    """行为事件表 Repository。"""

    def record(self, event_name: str, user_id: str, source: str = "MOBILE",
               metadata: Optional[Dict[str, Any]] = None) -> MobileBehaviorEvent:
        evt = MobileBehaviorEvent(
            id=str(uuid.uuid4()),
            event_name=event_name,
            user_id=user_id,
            source=source,
            data=metadata or {},
        )
        self._s.add(evt)
        self._s.commit()
        return evt

    def list_by_user(self, user_id: str) -> List[MobileBehaviorEvent]:
        stmt = (
            select(MobileBehaviorEvent)
            .where(MobileBehaviorEvent.user_id == user_id)
            .order_by(MobileBehaviorEvent.timestamp)
        )
        return list(self._s.execute(stmt).scalars())

    def list_by_source(self, source: str) -> List[MobileBehaviorEvent]:
        stmt = (
            select(MobileBehaviorEvent)
            .where(MobileBehaviorEvent.source == source)
            .order_by(MobileBehaviorEvent.timestamp)
        )
        return list(self._s.execute(stmt).scalars())

    def count_by_event(self, event_name: str) -> int:
        stmt = select(MobileBehaviorEvent).where(MobileBehaviorEvent.event_name == event_name)
        return len(list(self._s.execute(stmt).scalars()))

    def count(self) -> int:
        return len(list(self._s.execute(select(MobileBehaviorEvent)).scalars()))
