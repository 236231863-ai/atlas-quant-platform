"""Decision Intelligence Dashboard - timeline, risk map, opportunities, scenario comparison."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class DecisionDashboardData: decision_timeline:List[Dict]=field(default_factory=list); risk_map:List[Dict]=field(default_factory=list); opportunity_map:List[Dict]=field(default_factory=list); scenario_comparison:List[Dict]=field(default_factory=list); prediction_accuracy:float=0.0; def to_dict(self):return asdict(self)

class DecisionDashboard:
    def __init__(self): self._data = DecisionDashboardData()
    def update_timeline(self, t): self._data.decision_timeline = t
    def update_risk_map(self, r): self._data.risk_map = r
    def update_opportunities(self, o): self._data.opportunity_map = o
    def update_scenarios(self, s): self._data.scenario_comparison = s
    def get_data(self) -> DecisionDashboardData: return self._data
    def summary(self): return {"decisions": len(self._data.decision_timeline), "risks": len(self._data.risk_map),
        "opportunities": len(self._data.opportunity_map), "scenarios": len(self._data.scenario_comparison)}
