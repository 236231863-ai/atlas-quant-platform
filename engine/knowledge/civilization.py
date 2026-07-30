"""Research Civilization Memory - long-term evolution history."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class EraRecord:
    era_id: str; name: str; key_discoveries: List[str]; contributors: List[str]
    start_time: str = ""; end_time: str = ""
    def to_dict(self): return asdict(self)

@dataclass
class DiscoveryRecord:
    discovery_id: str; description: str; impact_score: float; era: str = ""
    agent_id: str = ""
    def to_dict(self): return asdict(self)

class CivilizationMemory:
    def __init__(self):
        self._eras: Dict[str, EraRecord] = {}
        self._discoveries: Dict[str, DiscoveryRecord] = {}
        self._generations: Dict[str, List[str]] = {}
    def record_era(self, era: EraRecord): self._eras[era.era_id] = era
    def record_discovery(self, discovery: DiscoveryRecord): self._discoveries[discovery.discovery_id] = discovery
    def record_generation(self, gen_id: str, agents: List[str]): self._generations[gen_id] = agents
    def get_eras(self) -> List[EraRecord]: return list(self._eras.values())
    def get_discoveries(self) -> List[DiscoveryRecord]: return list(self._discoveries.values())
    def get_timeline(self) -> List[Dict[str, Any]]:
        return [{"era_id": e.era_id, "name": e.name, "discoveries": len(e.key_discoveries)} for e in self._eras.values()]
    def count_eras(self) -> int: return len(self._eras)
    def count_discoveries(self) -> int: return len(self._discoveries)
