"""Civilization Dashboard - research timeline, goals, knowledge, agents, breakthroughs."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class CivilizationDashboardData:
    research_timeline: List[Dict[str, Any]] = field(default_factory=list)
    goal_evolution: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_growth: Dict[str, Any] = field(default_factory=dict)
    agent_generations: List[Dict[str, Any]] = field(default_factory=list)
    breakthrough_history: List[Dict[str, Any]] = field(default_factory=list)
    capability_improvement: List[Dict[str, Any]] = field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class CivilizationDashboard:
    def __init__(self):
        self._data = CivilizationDashboardData()
    def update_timeline(self, timeline: List[Dict[str, Any]]):
        self._data.research_timeline = timeline
    def update_goal_evolution(self, goals: List[Dict[str, Any]]):
        self._data.goal_evolution = goals
    def update_knowledge_growth(self, growth: Dict[str, Any]):
        self._data.knowledge_growth = growth
    def update_agent_generations(self, gens: List[Dict[str, Any]]):
        self._data.agent_generations = gens
    def update_breakthroughs(self, bts: List[Dict[str, Any]]):
        self._data.breakthrough_history = bts
    def update_capability(self, caps: List[Dict[str, Any]]):
        self._data.capability_improvement = caps
    def get_data(self) -> CivilizationDashboardData: return self._data
    def summary(self) -> Dict[str, Any]:
        return {"eras": len(self._data.research_timeline), "goals": len(self._data.goal_evolution),
                "breakthroughs": len(self._data.breakthrough_history),
                "capability_tracked": len(self._data.capability_improvement)}
