"""Industry Data Connector - connect external data sources."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

CONNECTOR_TYPES = ["csv","database","api","enterprise"]
@dataclass
class DataSource: source_id:str; source_type:str="csv"; config:Dict[str,Any]=field(default_factory=dict); status:str="connected"; last_sync:str=""; def to_dict(self):return asdict(self)

class DataConnector:
    def __init__(self): self._sources: Dict[str, DataSource] = {}
    def connect(self, s: DataSource): self._sources[s.source_id] = s; return s
    def validate(self, sid: str) -> bool:
        s = self._sources.get(sid); return s is not None and s.status == "connected"
    def list_sources(self) -> List[DataSource]: return list(self._sources.values())
    def count(self) -> int: return len(self._sources)
