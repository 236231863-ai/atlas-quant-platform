"""Research Director v6 - goal selection, roadmap, council, knowledge, self improvement."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.goal_generation import ResearchGoalGenerator, ResearchGoal
from engine.planner.planner_v2 import AutonomousResearchPlanner
from engine.expert_council import ResearchCouncil
from engine.knowledge.civilization_v2 import CivilizationEngineV2
from engine.self_improvement import SelfImprovementEngine, CapabilityMetrics

class ResearchDirectorV6:
    def __init__(self):
        self._goal_gen = ResearchGoalGenerator()
        self._planner = AutonomousResearchPlanner()
        self._council = ResearchCouncil()
        self._civilization = CivilizationEngineV2()
        self._self_improvement = SelfImprovementEngine()

    def select_goal(self, goals: List[ResearchGoal]) -> Optional[ResearchGoal]:
        if not goals: return None
        return max(goals, key=lambda g: g.priority * g.expected_value / max(g.risk, 0.01))

    def generate_roadmap(self, goal: ResearchGoal) -> Dict[str, Any]:
        return self._planner.create_roadmap(goal.goal_id, goal.title).to_dict()

    def consult_council(self, proposal: str) -> Dict[str, Any]:
        decision = self._council.propose_research(proposal)
        return decision.to_dict()

    def evaluate_capability(self, metrics: CapabilityMetrics) -> Dict[str, Any]:
        self._self_improvement.evaluate_capability(metrics)
        weakness = self._self_improvement.detect_weakness()
        result = {"overall": metrics.overall(), "weakness": weakness}
        if weakness:
            result["improvement_goal"] = self._self_improvement.generate_improvement_goal(weakness)
        return result

    def get_goal_gen(self): return self._goal_gen
    def get_planner(self): return self._planner
    def get_council(self): return self._council
    def get_civilization(self): return self._civilization
    def get_self_improvement(self): return self._self_improvement
