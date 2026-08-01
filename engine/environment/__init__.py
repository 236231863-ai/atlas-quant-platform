"""Research Environment Simulator - simulate different research environments."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

ENVIRONMENTS = {"normal": "Normal Environment", "high_risk": "High Risk Environment", "data_shift": "Data Shift", "unknown": "Unknown Event"}

@dataclass
class ScenarioResult:
    scenario_name:str
    risk_level:str="normal"
    volatility:float=0.5
    opportunity_score:float=0.5
    recommendation:str=""
    def to_dict(self):
        return asdict(self)

class EnvironmentSimulator:
    def __init__(self):
        self._scenarios: List[ScenarioResult] = []
    def create_scenario(self, name: str, risk: str="normal", vol: float=0.5) -> ScenarioResult:
        sr = ScenarioResult(scenario_name=name, risk_level=risk, volatility=vol)
        self._scenarios.append(sr); return sr
    def stress_test(self, base_score: float, volatility: float) -> Dict[str, float]:
        worst = base_score * (1 - volatility); best = base_score * (1 + volatility)
        return {"base": round(base_score, 4), "worst": round(worst, 4), "best": round(best, 4), "range": round(best - worst, 4)}
    def list_scenarios(self) -> List[ScenarioResult]: return self._scenarios
    def count(self) -> int: return len(self._scenarios)
