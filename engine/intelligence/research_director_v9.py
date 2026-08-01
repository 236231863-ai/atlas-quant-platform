"""Research Director v9 - autonomous decision intelligence orchestration."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.decision import DecisionSimulator, DecisionReport
from engine.opportunity import OpportunityDiscoveryEngine, OpportunityRanking
from engine.risk_intelligence import RiskIntelligenceEngine, RiskIntelligenceReport

class ResearchDirectorV9:
    def __init__(self):
        self._risk = RiskIntelligenceEngine()
        self._opportunity = OpportunityDiscoveryEngine()
        self._decisions: List[Dict[str, Any]] = []
    def decision_workflow(self, goal: str, actions: List[Dict[str, Any]]) -> DecisionReport:
        report = DecisionSimulator.simulate(goal, actions)
        self._decisions.append({"goal": goal, "report": report.to_dict()})
        return report
    def get_risk_report(self) -> RiskIntelligenceReport: return self._risk.generate_report()
    def get_opportunity_ranking(self) -> OpportunityRanking: return self._opportunity.rank()
    def get_decision_count(self) -> int: return len(self._decisions)
    def get_risk(self):
        return self._risk
        def get_opportunity(self):
            return self._opportunity
