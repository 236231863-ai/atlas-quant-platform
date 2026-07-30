"""User Feedback Intelligence - learn from user interactions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class UserAction: action_id:str; user_id:str; action_type:str; target:str; timestamp:str=""; def to_dict(self):return asdict(self)
@dataclass
class UserInsight: insight_id:str; preference:str; effective_suggestions:List[str]=field(default_factory=list); failed_suggestions:List[str]=field(default_factory=list); def to_dict(self):return asdict(self)

class UserFeedbackEngine:
    def __init__(self): self._actions: List[UserAction] = []; self._insights: List[UserInsight] = []
    def record_action(self, action: UserAction): self._actions.append(action); return action
    def analyze(self) -> UserInsight:
        viewed = sum(1 for a in self._actions if a.action_type=="view_report")
        adopted = sum(1 for a in self._actions if a.action_type=="adopt_suggestion")
        return UserInsight(insight_id="ui1", preference="balanced", effective_suggestions=["s1"] if adopted>viewed/2 else [])
    def get_actions(self) -> List[UserAction]: return self._actions
    def count_actions(self) -> int: return len(self._actions)
