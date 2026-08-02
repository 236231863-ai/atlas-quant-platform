"""subscription/v2 - 订阅验证（v3.8.0 Phase 4）。

版本：FREE / PRO / ENTERPRISE + 功能门槛 + 转化跟踪。
"""
from .plans import (
    SubscriptionManager, SubscriptionPlan, FREE, PRO, ENTERPRISE,
    can_access, upgrade_hint,
)

__all__ = ["SubscriptionManager", "SubscriptionPlan", "FREE", "PRO", "ENTERPRISE", "can_access", "upgrade_hint"]
