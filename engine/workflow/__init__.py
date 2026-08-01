"""Autonomous Workflow Engine - chain decision->action->execution->feedback->learning."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

WorkflowState = Enum("WorkflowState", ["CREATED","PLANNING","EXECUTING","REVIEWING","LEARNING","COMPLETED"])

@dataclass
class WorkflowInstance:
    workflow_id:str
    state:str="CREATED"
    decision_ref:str=""
    action_ref:str=""
    feedback_ref:str=""
    learning_notes:str=""
    def to_dict(self):
        return asdict(self)

class AutonomousWorkflowEngine:
    def __init__(self):
        self._workflows: Dict[str, WorkflowInstance] = {}
    def create(self, decision_id: str) -> WorkflowInstance:
        import uuid; w = WorkflowInstance(workflow_id=str(uuid.uuid4()), state="CREATED", decision_ref=decision_id)
        self._workflows[w.workflow_id] = w; return w
    def transition(self, wid: str, next_state: str) -> bool:
        w = self._workflows.get(wid)
        if not w: return False
        w.state = next_state; return True
    def complete(self, wid: str, notes: str) -> bool:
        w = self._workflows.get(wid)
        if not w: return False
        w.state = "COMPLETED"; w.learning_notes = notes; return True
    def list_workflows(self) -> List[WorkflowInstance]: return list(self._workflows.values())
    def count(self) -> int: return len(self._workflows)
