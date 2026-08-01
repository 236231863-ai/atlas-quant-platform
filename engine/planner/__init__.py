"""Autonomous Research Planner."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class ResearchPlan:
    objectives: List[str]; experiments: List[Dict[str, Any]]
    priority_order: List[str]; expected_gain: float; weekly_schedule: List[str]
    def to_dict(self):
        return asdict(self)

class ResearchPlanner:
    def __init__(self):
        self._experiment_history: List[Dict[str, Any]] = []

    def add_experiment(self, exp: Dict[str, Any]):
        self._experiment_history.append(exp)

    def generate_roadmap(self, objectives: List[str], available_experiments: List[Dict[str, Any]]) -> ResearchPlan:
        prioritized = sorted(available_experiments, key=lambda e: e.get("priority", 5), reverse=True)
        gain = min(1.0, len(prioritized) * 0.1)
        weekly = [f"Week {i+1}: {p.get('name','experiment')}" for i, p in enumerate(prioritized[:4])]
        return ResearchPlan(objectives=objectives, experiments=prioritized,
                           priority_order=[e.get("name","?") for e in prioritized],
                           expected_gain=round(gain, 2), weekly_schedule=weekly)

    def estimate_information_gain(self, experiment_config: Dict[str, Any]) -> float:
        base = 0.3
        if "params" in experiment_config and len(experiment_config["params"]) > 2: base += 0.2
        if experiment_config.get("type") == "exploration": base += 0.2
        if experiment_config.get("type") == "optimization": base += 0.1
        return min(1.0, base)

    def prioritize_experiments(self, experiments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for e in experiments:
            gain = self.estimate_information_gain(e)
            novelty = 0.2 if not any(h.get("name") == e.get("name") for h in self._experiment_history) else 0.0
            scored.append((gain + novelty, e))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored]
