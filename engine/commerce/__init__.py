"""Commercial Business Layer - license, subscription, order, invoice, commission, revenue."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

class LicenseType(str, Enum): FREE="free"; PRO="pro"; RESEARCH="research"; ENTERPRISE="enterprise"

@dataclass
class License: id:str; user_id:str; license_type:LicenseType=LicenseType.FREE; features:List[str]=field(default_factory=list); expire_date:str=""; status:str="active"; def to_dict(self):return asdict(self)

class LicenseManager:
    def __init__(self): self._licenses: Dict[str, License] = {}
    def generate(self, uid: str, lt: LicenseType, features: List[str]) -> License:
        import uuid; l = License(id=str(uuid.uuid4()), user_id=uid, license_type=lt, features=features)
        self._licenses[l.id] = l; return l
    def validate(self, lid: str) -> bool:
        l = self._licenses.get(lid); return l is not None and l.status == "active"
    def check_feature(self, lid: str, feature: str) -> bool:
        l = self._licenses.get(lid); return feature in l.features if l else False
    def expire(self, lid: str) -> bool:
        l = self._licenses.get(lid)
        if not l: return False; l.status = "expired"; return True
    def count(self) -> int: return len(self._licenses)

class SubscriptionManager:
    def __init__(self): self._subs: Dict[str, str] = {}
    def create(self, uid: str, plan: str): self._subs[uid] = plan; return plan
    def upgrade(self, uid: str, plan: str) -> bool:
        if uid not in self._subs: return False; self._subs[uid] = plan; return True
    def cancel(self, uid: str) -> bool:
        return bool(self._subs.pop(uid, None))
    def get_plan(self, uid: str) -> Optional[str]: return self._subs.get(uid)
    def count(self) -> int: return len(self._subs)

class RevenueAnalyzer:
    def __init__(self): self._records: List[Dict[str, Any]] = []
    def record(self, amount: float, plan: str): self._records.append({"amount":amount,"plan":plan})
    def mrr(self) -> float: return sum(r["amount"] for r in self._records) if self._records else 0.0
    def arr(self) -> float: return self.mrr() * 12
    def count(self) -> int: return len(self._records)
