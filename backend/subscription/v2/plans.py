"""subscription/v2 - 订阅计划与访问控制。"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class SubscriptionPlan:
    """订阅计划。"""

    id: str
    name: str
    price_month: float = 0.0
    features: List[str] = field(default_factory=list)

    def can(self, feature: str) -> bool:
        return feature in self.features


FREE = SubscriptionPlan(
    id="free", name="FREE", price_month=0.0,
    features=["dashboard", "analysis_basic", "backtest_basic", "export_basic", "data_full"],
)
PRO = SubscriptionPlan(
    id="pro", name="PRO", price_month=9.9,
    features=["dashboard", "analysis_basic", "analysis_advanced", "backtest_basic",
              "backtest_advanced", "export_basic", "export_advanced", "daily_intelligence", "data_full"],
)
ENTERPRISE = SubscriptionPlan(
    id="enterprise", name="ENTERPRISE", price_month=29.9,
    features=["dashboard", "analysis_basic", "analysis_advanced", "backtest_basic",
              "backtest_advanced", "export_basic", "export_advanced", "daily_intelligence",
              "data_full", "ai_online", "priority_support", "batch_analysis"],
)

PLANS: Dict[str, SubscriptionPlan] = {p.id: p for p in (FREE, PRO, ENTERPRISE)}


def can_access(plan_id: Optional[str], feature: str) -> bool:
    p = PLANS.get(plan_id or "free", FREE)
    return p.can(feature)


def upgrade_hint(plan_id: Optional[str], feature: str) -> Optional[str]:
    p = PLANS.get(plan_id or "free", FREE)
    if p.can(feature):
        return None
    return f"「{feature}」为付费功能，当前 {p.name} 版不可用。升级 PRO/ENTERPRISE 后可用。"


class SubscriptionManager:
    """订阅管理器（本地记录用户计划 + 转化事件）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self._path = os.path.join(self._dir, "subscription_v2.json")
        self._data: Dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get_plan(self, user_id: str = "default") -> str:
        return self._data.get(user_id, {}).get("plan", "free")

    def set_plan(self, user_id: str, plan_id: str) -> bool:
        if plan_id not in PLANS:
            return False
        self._data.setdefault(user_id, {})["plan"] = plan_id
        self._data[user_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        return True

    def record_conversion(self, user_id: str, from_plan: str = "free", to_plan: str = "pro") -> bool:
        if to_plan not in PLANS:
            return False
        conv = self._data.setdefault(user_id, {}).setdefault("conversions", [])
        conv.append({"from": from_plan, "to": to_plan, "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        self._data[user_id]["plan"] = to_plan
        self._save()
        return True

    def conversion_count(self) -> int:
        return sum(len(u.get("conversions", [])) for u in self._data.values())

    def plan_distribution(self) -> Dict[str, int]:
        d: Dict[str, int] = {}
        for u in self._data.values():
            p = u.get("plan", "free")
            d[p] = d.get(p, 0) + 1
        return d

    def report(self) -> dict:
        return {
            "conversion_count": self.conversion_count(),
            "plan_distribution": self.plan_distribution(),
            "user_count": len(self._data),
        }

    def clear(self) -> None:
        self._data = {}
        if os.path.exists(self._path):
            try:
                os.remove(self._path)
            except OSError:
                pass
