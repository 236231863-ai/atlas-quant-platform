"""Industry Knowledge Base - domain-specific knowledge graphs."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class IndustryEntity:
    entity_id:str
    industry:str
    name:str
    entity_type:str="concept"
    relations:List[str]=field(default_factory=list)
    def to_dict(self):
        return asdict(self)

class IndustryKnowledgeGraph:
    def __init__(self):
        self._entities: Dict[str, IndustryEntity] = {}
    def add_entity(self, e: IndustryEntity):
        self._entities[e.entity_id] = e
        return e
    def search(self, industry: str, query: str) -> List[IndustryEntity]:
        q = query.lower()
        return [e for e in self._entities.values() if e.industry == industry and (q in e.name.lower() or q in e.entity_type.lower())]
    def get_relations(self, eid: str) -> List[str]:
        e = self._entities.get(eid); return e.relations if e else []
    def count(self) -> int: return len(self._entities)
