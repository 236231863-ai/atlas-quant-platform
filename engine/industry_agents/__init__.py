"""Industry Agent System - specialized agents for different industries."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

AGENT_TYPES = {"finance":"Financial analysis, risk assessment, market research","retail":"Customer analysis, sales forecasting","research":"Scientific research, data analysis","business":"Business intelligence, strategy planning"}

@dataclass
class IndustryAgent: agent_id:str; industry:str; name:str; capabilities:List[str]=field(default_factory=list); prompt:str=""; metrics:List[str]=field(default_factory=list); def to_dict(self):return asdict(self)

class IndustryAgentSystem:
    def __init__(self): self._agents: Dict[str, IndustryAgent] = {}
    def register(self, a: IndustryAgent): self._agents[a.agent_id] = a; return a
    def list_by_industry(self, industry: str) -> List[IndustryAgent]:
        return [a for a in self._agents.values() if a.industry == industry]
    def get_agent(self, aid: str) -> Optional[IndustryAgent]: return self._agents.get(aid)
    def count(self) -> int: return len(self._agents)
