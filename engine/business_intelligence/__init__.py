"""Business Intelligence Engine - revenue, retention, growth opportunities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class BusinessReport: revenue_insights:Dict[str,float]=field(default_factory=dict); retention_rate:float=0.0; growth_opportunities:List[str]=field(default_factory=list); def to_dict(self):return asdict(self)

class BusinessIntelligenceEngine:
    def __init__(self): self._reports: List[BusinessReport] = []
    def analyze_revenue(self, subscriptions: List[str], prices: Dict[str,float]) -> Dict[str,float]:
        return {"total_users": len(subscriptions), "mrr": round(len(subscriptions)*sum(prices.values())/max(len(prices),1), 2)}
    def analyze_retention(self, active_users: int, total_users: int) -> float:
        return round(active_users/max(total_users,1), 4)
    def find_opportunities(self, churn_risks: Dict[str,float]) -> List[str]:
        high_risk = sum(1 for r in churn_risks.values() if r > 0.5)
        return ["Launch retention campaign"] if high_risk > 0 else []
    def generate_report(self) -> BusinessReport: return BusinessReport()
    def count(self) -> int: return len(self._reports)
