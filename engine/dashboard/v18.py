"""Platform Dashboard v18 + Platform API - Atlas Control Center."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class V18DashboardData: platform_health:Dict[str,Any]=field(default_factory=dict); reliability:Dict[str,Any]=field(default_factory=dict); security:Dict[str,Any]=field(default_factory=dict); release_status:List[Dict]=field(default_factory=list); recovery_history:List[Dict]=field(default_factory=list); ai_traces:List[Dict]=field(default_factory=list); quality_score:float=0.0; def to_dict(self):return asdict(self)

class V18Dashboard:
    def __init__(self): self._data = V18DashboardData()
    def update_health(self, h): self._data.platform_health = h; def update_reliability(self, r): self._data.reliability = r
    def update_security(self, s): self._data.security = s; def update_releases(self, r): self._data.release_status = r
    def update_recovery(self, r): self._data.recovery_history = r; def update_traces(self, t): self._data.ai_traces = t
    def get_data(self) -> V18DashboardData: return self._data
    def summary(self): return {"health": len(str(self._data.platform_health)), "releases": len(self._data.release_status)}

class PlatformAPI:
    def __init__(self): self._health_records: List[Dict]=[]; self._release_records: List[Dict]=[]
    def record_health(self, h): self._health_records.append(h)
    def record_release(self, r): self._release_records.append(r)
    def get_health_history(self) -> List[Dict]: return self._health_records
    def get_release_history(self) -> List[Dict]: return self._release_records
