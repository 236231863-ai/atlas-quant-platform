"""Research Director v10 - autonomous action & feedback orchestration."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.action import ActionPlanner, ActionPlanReport
from engine.execution_intelligence import ExecutionSimulator, ExecutionReport
from engine.feedback import FeedbackIntelligence, FeedbackInsight
from engine.adaptation import AdaptiveStrategyEngine, AdaptationResult
from engine.workflow import AutonomousWorkflowEngine, WorkflowInstance

class ResearchDirectorV10:
    def __init__(self):
        self._planner = ActionPlanner(); self._simulator = ExecutionSimulator()
        self._feedback = FeedbackIntelligence(); self._adaptation = AdaptiveStrategyEngine()
        self._workflow = AutonomousWorkflowEngine()
    def autonomous_cycle(self, goal: str, steps: List[str]) -> Dict[str, Any]:
        plan = self._planner.create_plan(goal, steps)
        execution = self._simulator.simulate(plan.plan_id, len(steps))
        return {"plan": plan.to_dict(), "execution": execution.to_dict()}
    def record_feedback(self, insight: FeedbackInsight):
        self._feedback.record(insight)
    def adapt(self, param: str, current: float, error: float) -> AdaptationResult:
        return self._adaptation.adjust_parameter(param, current, error)
    def create_workflow(self, decision_id: str) -> WorkflowInstance:
        return self._workflow.create(decision_id)
    def get_planner(self):
        return self._planner
    def get_feedback(self):
        return self._feedback
