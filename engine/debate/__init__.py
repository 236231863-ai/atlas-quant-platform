"""Research Debate Engine - agents challenge decisions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from engine.agent_protocol import AgentFeedback

@dataclass
class DebateArgument:
    agent_id: str; position: str; reasoning: str; evidence: List[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass
class DebateReport:
    topic: str; arguments: List[DebateArgument]; votes: Dict[str, int]; decision: str; confidence: float
    def to_dict(self): return asdict(self)

class ResearchDebateSystem:
    def __init__(self): self._arguments: List[DebateArgument] = []; self._votes: Dict[str, int] = {}
    def argument(self, agent: str, position: str, reasoning: str) -> DebateArgument:
        arg = DebateArgument(agent_id=agent, position=position, reasoning=reasoning)
        self._arguments.append(arg); return arg
    def counter_argument(self, agent: str, target: str, reasoning: str) -> DebateArgument:
        arg = DebateArgument(agent_id=agent, position=f"counter_{target}", reasoning=f"Disagree: {reasoning}")
        self._arguments.append(arg); return arg
    def vote(self, agent: str, proposal: str) -> Dict[str, int]:
        self._votes[agent] = self._votes.get(agent, 0) + 1
        return {"agent":agent,"votes_cast":self._votes[agent]}
    def final_decision(self) -> DebateReport:
        total_votes = sum(self._votes.values())
        consensus = total_votes > len(self._votes) * 0.5
        return DebateReport(topic="research_debate", arguments=self._arguments,
            votes=dict(self._votes), decision="approved" if consensus else "rejected",
            confidence=min(1.0, total_votes / max(1, len(self._votes) * 2)))
