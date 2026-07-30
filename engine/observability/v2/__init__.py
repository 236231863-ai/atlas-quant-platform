"""Observability v2 - complete tracing system for AI decisions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class TraceRecord: trace_id:str; trace_type:str; origin:str; modules:List[str]=field(default_factory=list); agent:str=""; decisions:List[str]=field(default_factory=list); result:str=""; def to_dict(self):return asdict(self)

class TraceEngine:
    def __init__(self): self._traces: Dict[str, TraceRecord] = {}
    def record(self, t: TraceRecord): self._traces[t.trace_id] = t; return t
    def get_trace(self, tid: str) -> Optional[TraceRecord]: return self._traces.get(tid)
    def find_by_agent(self, agent: str) -> List[TraceRecord]:
        return [t for t in self._traces.values() if t.agent == agent]
    def trace_origin(self, tid: str) -> Optional[str]:
        t = self._traces.get(tid); return t.origin if t else None
    def count(self) -> int: return len(self._traces)
