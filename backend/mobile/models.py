"""backend.mobile.models - Mobile MVP 五张核心表（SQLAlchemy 2.x ORM）。

独立于现有 backend.database（现有为 async 研究层），
Mobile MVP 使用同步 SQLite + Repository 层，避免耦合。

表：
  users            - 微信用户（U0001+ 编号，openid 关联）
  tickets          - 用户彩票
  draws            - 开奖数据（复用内置 1200 期 + 增量）
  reminders        - 开奖提醒（微信订阅消息下发记录）
  behavior_events  - 行为埋点（source 隔离 REAL/MOBILE/SIMULATION）
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_uuid() -> str:
    return str(uuid.uuid4())


class MobileBase(DeclarativeBase):
    """Mobile MVP 独立 ORM Base。"""


class MobileUser(MobileBase):
    """用户表：微信授权即账户，user_id=U 编号，openid 为微信唯一标识。"""

    __tablename__ = "mobile_users"
    __table_args__ = (UniqueConstraint("openid", name="uq_mobile_user_openid"),)

    user_id: Mapped[str] = mapped_column(String(10), primary_key=True)  # U0001
    openid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    registered_at: Mapped[str] = mapped_column(String(32), default=_utcnow)
    first_open_at: Mapped[str] = mapped_column(String(32), default=_utcnow)
    first_ticket_saved_at: Mapped[str] = mapped_column(String(32), default="")
    lottery_type: Mapped[str] = mapped_column(String(16), default="大乐透")
    purchase_frequency: Mapped[str] = mapped_column(String(16), default="每周")
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    draw_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    claim_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    asset_viewed: Mapped[bool] = mapped_column(Boolean, default=False)
    weekly_report_viewed: Mapped[bool] = mapped_column(Boolean, default=False)


class MobileTicket(MobileBase):
    """彩票表：一张用户彩票。"""

    __tablename__ = "mobile_tickets"

    ticket_id: Mapped[str] = mapped_column(String(16), primary_key=True)  # T0001
    user_id: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    lottery: Mapped[str] = mapped_column(String(8), nullable=False)  # dlt / ssq
    front: Mapped[Any] = mapped_column(JSON, nullable=False)  # [5] or [6]
    back: Mapped[Any] = mapped_column(JSON, nullable=False)  # [2] or [1]
    cost: Mapped[float] = mapped_column(Float, default=2.0)
    buy_date: Mapped[str] = mapped_column(String(16), default="")
    draw_date: Mapped[str] = mapped_column(String(16), default="")
    issue: Mapped[str] = mapped_column(String(12), default="")
    claimed: Mapped[bool] = mapped_column(Boolean, default=False)


class MobileDraw(MobileBase):
    """开奖表：按期号存储开奖结果。"""

    __tablename__ = "mobile_draws"

    issue: Mapped[str] = mapped_column(String(12), primary_key=True)  # 26086
    lottery: Mapped[str] = mapped_column(String(8), nullable=False, index=True)  # dlt / ssq
    front: Mapped[Any] = mapped_column(JSON, nullable=False)
    back: Mapped[Any] = mapped_column(JSON, nullable=False)
    draw_date: Mapped[str] = mapped_column(String(16), default="")


class MobileReminder(MobileBase):
    """提醒表：开奖提醒下发记录（去重 + 点击追踪）。"""

    __tablename__ = "mobile_reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    user_id: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    ticket_id: Mapped[str] = mapped_column(String(16), nullable=False)
    issue: Mapped[str] = mapped_column(String(12), nullable=False)
    remind_at: Mapped[str] = mapped_column(String(32), default="")
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    clicked: Mapped[bool] = mapped_column(Boolean, default=False)


class MobileBehaviorEvent(MobileBase):
    """行为事件表：17 事件集 + mobile 事件，source 隔离。"""

    __tablename__ = "mobile_behavior_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    event_name: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="MOBILE")
    timestamp: Mapped[str] = mapped_column(String(32), default=_utcnow)
    data: Mapped[Any] = mapped_column(JSON, default=dict)
