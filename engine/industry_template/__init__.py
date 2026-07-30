"""Industry Template System - pre-built solutions for industries."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

INDUSTRIES = ["finance","retail","manufacturing","research","marketing","technology"]

@dataclass
class IndustryTemplate: template_id:str; industry:str; name:str; problem:str=""; dataset:str=""; workflow:List[str]=field(default_factory=list); agents:List[str]=field(default_factory=list); report:str=""; metrics:List[str]=field(default_factory=list); version:str="1.0"; def to_dict(self):return asdict(self)

class TemplateRegistry:
    def __init__(self): self._templates: Dict[str, IndustryTemplate] = {}
    def create(self, t: IndustryTemplate): self._templates[t.template_id] = t; return t
    def clone(self, tid: str, new_id: str) -> Optional[IndustryTemplate]:
        orig = self._templates.get(tid)
        if not orig: return None
        clone = IndustryTemplate(template_id=new_id, industry=orig.industry, name=f"{orig.name} (Copy)", problem=orig.problem)
        self._templates[new_id] = clone; return clone
    def list_by_industry(self, industry: str) -> List[IndustryTemplate]:
        return [t for t in self._templates.values() if t.industry == industry]
    def count(self) -> int: return len(self._templates)
