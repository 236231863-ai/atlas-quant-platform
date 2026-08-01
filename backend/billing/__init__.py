"""Commercial Foundation - subscription architecture."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

class PlanType(str, Enum):
    FREE="free"
    PRO="pro"
    RESEARCH="research"
PLAN_FEATURES = {"free":["basic_analysis","limited_reports"],"pro":["advanced_analysis","ai_assistant","backtesting"],"research":["custom_strategy","experiments","data_tools"]}

@dataclass
class Subscription:
    user_id: str
    plan: PlanType=PlanType.FREE
    features: List[str]=field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class PlanService:
    def __init__(self):
        self._subscriptions: Dict[str, Subscription] = {}
    def register(self, uid: str):
        self._subscriptions[uid]=Subscription(user_id=uid, plan=PlanType.FREE, features=list(PLAN_FEATURES["free"]))
        return self._subscriptions[uid]
    def upgrade(self, uid: str, plan: PlanType) -> bool:
        sub = self._subscriptions.get(uid)
        if not sub: return False
        sub.plan = plan; sub.features = list(PLAN_FEATURES.get(plan.value, [])); return True
    def check_permission(self, uid: str, feature: str) -> bool:
        sub = self._subscriptions.get(uid)
        return feature in sub.features if sub else False
    def get_subscription(self, uid: str) -> Optional[Subscription]: return self._subscriptions.get(uid)
    def count(self) -> int: return len(self._subscriptions)
