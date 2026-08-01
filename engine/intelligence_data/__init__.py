"""Data Intelligence Hub - unified external data management with lineage and quality."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

@dataclass
class DataSource:
    source_id:str
    name:str
    source_type:str="web"
    trust_level:float=0.5
    format:str="json"
    status:str="active"
    last_update:str=""
    def to_dict(self):
        return asdict(self)
@dataclass
class DataLineage:
    lineage_id:str
    source:str
    pipeline:str
    destination:str
    timestamp:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
    usage_count:int=0
    def to_dict(self):
        return asdict(self)

class DataIntelligenceHub:
    def __init__(self):
        self._sources: Dict[str, DataSource] = {}
        self._lineage: List[DataLineage] = []
    def register_source(self, source: DataSource):
        self._sources[source.source_id] = source
        return source
    def record_lineage(self, lineage: DataLineage):
        self._lineage.append(lineage)
        return lineage
    def get_lineage(self, destination: str) -> List[DataLineage]:
        return [l for l in self._lineage if l.destination == destination]
    def list_sources(self) -> List[DataSource]: return list(self._sources.values())
    def count_sources(self) -> int: return len(self._sources)
    def count_lineage(self) -> int: return len(self._lineage)
