"""Commercial Service Layer - subscription, plan, usage metering."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class Plan:
    plan_id:str
    name:str
    price:float=0.0
    features:List[str]=field(default_factory=list)
    limits:Dict[str,int]=field(default_factory=dict)
    def to_dict(self):
        return asdict(self)
@dataclass
class UsageRecord:
    user_id:str
    api_calls:int=0
    experiments:int=0
    storage_mb:int=0
    agents:int=0
    period:str="monthly"
    def to_dict(self):
        return asdict(self)

PLANS = {"free": Plan("free","Free",0,["basic_analysis"],{"api_calls":100}),"pro": Plan("pro","Professional",29,["advanced","ai_assistant"],{"api_calls":1000}),"enterprise": Plan("enterprise","Enterprise",99,["all","custom"],{"api_calls":9999})}

class CommercialServiceManager:
    def __init__(self):
        self._subscriptions: Dict[str, str] = {}
        self._usage: Dict[str, UsageRecord] = {}
    def subscribe(self, uid: str, plan: str):
        self._subscriptions[uid] = plan
        return plan
    def check_access(self, uid: str, feature: str) -> bool:
        plan_name = self._subscriptions.get(uid, "free"); plan = PLANS.get(plan_name)
        return feature in plan.features if plan else False
    def record_usage(self, uid: str, record: UsageRecord):
        self._usage[uid] = record
        return record
    def get_plan(self, name: str) -> Optional[Plan]: return PLANS.get(name)
    def count_subs(self) -> int: return len(self._subscriptions)
