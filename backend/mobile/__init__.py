"""backend.mobile - Mobile MVP（真实用户验证版）。

模块：
  models.py        - 五张核心表（users/tickets/draws/reminders/behavior_events）
  db.py            - SQLite engine/session 工厂
  repositories.py  - Repository 层（业务代码禁止直连数据库）
  service.py       - 业务服务（录票/查奖/提醒/漏斗/埋点）
  wechat.py        - 微信订阅消息接口
  api.py           - FastAPI 路由
"""
from backend.mobile.models import (
    MobileBase,
    MobileBehaviorEvent,
    MobileDraw,
    MobileReminder,
    MobileTicket,
    MobileUser,
)
from backend.mobile.service import (
    DLT_PRIZE_TABLE,
    MOBILE_EVENTS,
    DrawMatcher,
    EVENT_MOBILE_DRAW_VIEWED,
    EVENT_MOBILE_FEEDBACK_SUBMITTED,
    EVENT_MOBILE_OPENED,
    EVENT_MOBILE_REMINDER_ENABLED,
    EVENT_MOBILE_TICKET_SAVED,
    MobileService,
    MobileTicketParser,
)

__all__ = [
    "MobileBase",
    "MobileUser",
    "MobileTicket",
    "MobileDraw",
    "MobileReminder",
    "MobileBehaviorEvent",
    "MobileService",
    "MobileTicketParser",
    "DrawMatcher",
    "DLT_PRIZE_TABLE",
    "MOBILE_EVENTS",
    "EVENT_MOBILE_OPENED",
    "EVENT_MOBILE_TICKET_SAVED",
    "EVENT_MOBILE_REMINDER_ENABLED",
    "EVENT_MOBILE_DRAW_VIEWED",
    "EVENT_MOBILE_FEEDBACK_SUBMITTED",
]
