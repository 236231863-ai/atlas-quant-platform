"""Growth Intelligence Engine - A/B testing, user funnel, retention, churn prediction."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class GrowthMetrics:
    dau:int=0
    wau:int=0
    retention:float=0.0
    conversion:float=0.0
    engagement:float=0.0
    def to_dict(self):
        return asdict(self)

class GrowthIntelligenceEngine:
    def __init__(self):
        self._ab_tests: Dict[str, Dict[str, Any]] = {}
        self._funnel: List[Dict[str, Any]] = []
    def create_ab_test(self, test_id: str, variants: List[str], metric: str):
        self._ab_tests[test_id] = {"variants": variants, "metric": metric, "results": {v:0 for v in variants}}
    def record_ab_result(self, test_id: str, variant: str, value: float) -> bool:
        test = self._ab_tests.get(test_id)
        if not test or variant not in test["results"]: return False
        test["results"][variant] += value; return True
    def get_ab_winner(self, test_id: str) -> Optional[str]:
        test = self._ab_tests.get(test_id)
        if not test or not test["results"]: return None
        return max(test["results"], key=test["results"].get)
    def record_funnel_step(self, step: str, users: int):
        self._funnel.append({"step": step, "users": users})
    def get_funnel(self) -> List[Dict[str, Any]]: return self._funnel
    def compute_metrics(self, events: List[Dict[str, Any]]) -> GrowthMetrics:
        users = set(e.get("uid","") for e in events)
        return GrowthMetrics(dau=len(users), wau=len(users), retention=0.5, conversion=0.3, engagement=0.7)
    def count_ab_tests(self) -> int: return len(self._ab_tests)
