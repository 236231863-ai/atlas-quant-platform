"""Civilization Engine v2 - research eras, discoveries, breakthroughs."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class EraRecord:
    era_id: str; name: str; description: str; discoveries: List[str] = field(default_factory=list)
    failed_theories: List[str] = field(default_factory=list); agents: List[str] = field(default_factory=list)
    def to_dict(self): return asdict(self)

@dataclass
class BreakthroughRecord:
    breakthrough_id: str; name: str; description: str; era_id: str; impact_score: float
    def to_dict(self): return asdict(self)

class CivilizationEngineV2:
    def __init__(self):
        self._eras: Dict[str, EraRecord] = {}
        self._breakthroughs: Dict[str, BreakthroughRecord] = {}

    def record_era(self, era: EraRecord): self._eras[era.era_id] = era; return era
    def record_breakthrough(self, bt: BreakthroughRecord):
        self._breakthroughs[bt.breakthrough_id] = bt
        if bt.era_id in self._eras: self._eras[bt.era_id].discoveries.append(bt.name)
        return bt

    def get_eras(self) -> List[EraRecord]: return list(self._eras.values())
    def get_breakthroughs(self) -> List[BreakthroughRecord]: return list(self._breakthroughs.values())
    def count_eras(self) -> int: return len(self._eras)
    def count_breakthroughs(self) -> int: return len(self._breakthroughs)
