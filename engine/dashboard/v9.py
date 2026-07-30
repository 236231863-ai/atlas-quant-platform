"""Ecosystem Dashboard - developer, plugin, marketplace metrics."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class EcosystemData:
    developer_count: int=0; plugin_count: int=0; strategy_count: int=0
    data_assets: int=0; agent_count: int=0; api_usage: int=0; community_growth: float=0.0
    def to_dict(self): return asdict(self)

class EcosystemDashboard:
    def __init__(self): self._data = EcosystemData()
    def update(self, data: EcosystemData): self._data = data
    def get_data(self) -> EcosystemData: return self._data
    def summary(self) -> Dict[str, Any]:
        return {"developers": self._data.developer_count, "plugins": self._data.plugin_count,
                "strategies": self._data.strategy_count, "agents": self._data.agent_count}
