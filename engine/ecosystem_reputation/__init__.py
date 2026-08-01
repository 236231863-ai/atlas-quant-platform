"""Ecosystem Reputation System - creator ratings and rankings."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

CreatorLevel = Enum("CreatorLevel", ["NEW","VERIFIED","EXPERT","ENTERPRISE"])
@dataclass
class CreatorReputation:
    creator_id:str
    technical_quality:float=0.5
    usage_count:int=0
    satisfaction:float=0.5
    stability:float=0.5
    innovation:float=0.5
    level:CreatorLevel=CreatorLevel.NEW
    def overall(self)->float: return round((self.technical_quality+self.satisfaction+self.stability+self.innovation)/4,4)
    def to_dict(self):
        return asdict(self)

class ReputationSystem:
    def __init__(self):
        self._reputations: Dict[str, CreatorReputation] = {}
    def register(self, r: CreatorReputation):
        self._reputations[r.creator_id] = r
        return r
    def promote(self, cid: str) -> bool:
        r = self._reputations.get(cid)
        if not r: return False
        if r.overall() > 0.8: r.level = CreatorLevel.EXPERT
        elif r.overall() > 0.6: r.level = CreatorLevel.VERIFIED
        return True
    def get_reputation(self, cid: str) -> Optional[CreatorReputation]: return self._reputations.get(cid)
    def ranking(self) -> List[Dict[str, Any]]:
        return sorted([{"creator_id": c, "score": r.overall(), "level": r.level.name} for c,r in self._reputations.items()], key=lambda x: x["score"], reverse=True)
    def count(self) -> int: return len(self._reputations)
