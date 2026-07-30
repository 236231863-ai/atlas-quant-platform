"""Agent Communication Protocol - standard communication layer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class ResearchTask:
    task_id: str; type: str; objective: str; params: Dict[str, Any] = field(default_factory=dict)
    assigned_to: str = ""; status: str = "created"
    def to_dict(self): return asdict(self)

@dataclass
class ResearchMessage:
    message_id: str; sender: str; recipient: str; content: str; task_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self): return asdict(self)

@dataclass
class AgentResult:
    agent_id: str; task_id: str; result: Dict[str, Any]; confidence: float = 0.5
    def to_dict(self): return asdict(self)

@dataclass
class AgentFeedback:
    agent_id: str; target_id: str; feedback_type: str; content: str; score: float = 0.0
    def to_dict(self): return asdict(self)

class AgentProtocol:
    def __init__(self): self._messages: List[ResearchMessage] = []; self._tasks: Dict[str, ResearchTask] = {}
    def create_task(self, task: ResearchTask) -> ResearchTask:
        self._tasks[task.task_id] = task; return task
    def get_task(self, task_id: str) -> Optional[ResearchTask]: return self._tasks.get(task_id)
    def send_message(self, msg: ResearchMessage) -> ResearchMessage:
        self._messages.append(msg); return msg
    def receive_messages(self, agent_id: str) -> List[ResearchMessage]:
        return [m for m in self._messages if m.recipient == agent_id]
    def trace_history(self, task_id: str) -> List[ResearchMessage]:
        return [m for m in self._messages if m.task_id == task_id]
    def validate_message(self, msg: ResearchMessage) -> List[str]:
        errors = []
        if not msg.message_id: errors.append("message_id required")
        if not msg.sender: errors.append("sender required")
        if not msg.recipient: errors.append("recipient required")
        if not msg.content: errors.append("content required")
        return errors
    def count_messages(self) -> int: return len(self._messages)
    def count_tasks(self) -> int: return len(self._tasks)
