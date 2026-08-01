"""Knowledge Fusion Engine - merge historical, experimental, external, and user knowledge."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class FusedKnowledge:
    fusion_id:str
    entity:str
    sources:List[str]
    relation:str="related"
    confidence:float=0.5
    description:str=""
    def to_dict(self):
        return asdict(self)

class KnowledgeFusionEngine:
    def __init__(self):
        self._knowledge: Dict[str, FusedKnowledge] = {}
    def fuse(self, knowledge: FusedKnowledge):
        self._knowledge[knowledge.fusion_id] = knowledge
        return knowledge
    def find_entity(self, entity: str) -> List[FusedKnowledge]:
        return [k for k in self._knowledge.values() if entity.lower() in k.entity.lower()]
    def find_relation(self, relation: str) -> List[FusedKnowledge]:
        return [k for k in self._knowledge.values() if k.relation == relation]
    def count(self) -> int: return len(self._knowledge)
