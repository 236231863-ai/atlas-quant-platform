"""Risk Intelligence Upgrade - prediction, propagation, radar."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class RiskIntelligenceReport: risks:List[Dict[str,Any]]=field(default_factory=list); overall_risk:float=0.0; top_risk:str=""; def to_dict(self):return asdict(self)

class RiskIntelligenceEngine:
    def __init__(self): self._risks: Dict[str, List[float]] = {}
    def record_risk(self, risk_id: str, value: float):
        if risk_id not in self._risks: self._risks[risk_id] = []
        self._risks[risk_id].append(value)
    def predict_trend(self, risk_id: str) -> Optional[float]:
        vals = self._risks.get(risk_id)
        if not vals or len(vals) < 2: return None
        return round((vals[-1] - vals[0]) / len(vals), 4)
    def get_propagation(self, risk_id: str, network: Dict[str, List[str]]) -> List[str]:
        affected = network.get(risk_id, []); return affected
    def generate_report(self) -> RiskIntelligenceReport:
        avg_risks = {rid: sum(vals)/len(vals) for rid, vals in self._risks.items() if vals}
        if not avg_risks: return RiskIntelligenceReport()
        top = max(avg_risks, key=avg_risks.get)
        risks = [{"risk_id": rid, "avg": round(val,4)} for rid, val in avg_risks.items()]
        return RiskIntelligenceReport(risks=risks, overall_risk=round(sum(avg_risks.values())/len(avg_risks),4), top_risk=top)
    def count_risks(self) -> int: return len(self._risks)
