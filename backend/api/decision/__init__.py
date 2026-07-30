"""Decision API - expose decision intelligence capabilities."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from engine.decision import DecisionSimulator, DecisionReport

class DecisionAPIService:
    def __init__(self): self._decisions: List[DecisionReport] = []
    def simulate_decision(self, goal: str, actions: List[Dict[str, Any]]) -> DecisionReport:
        report = DecisionSimulator.simulate(goal, actions)
        self._decisions.append(report); return report
    def get_latest(self) -> Optional[DecisionReport]:
        return self._decisions[-1] if self._decisions else None
    def get_history(self) -> List[DecisionReport]: return self._decisions
    def count(self) -> int: return len(self._decisions)
