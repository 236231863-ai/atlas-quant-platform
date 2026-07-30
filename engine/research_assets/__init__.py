"""Research Asset Management - manage institutional assets."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchAsset:
    asset_id: str; asset_type: str; owner: str; version: str = "1.0"
    performance: float = 0.5; usage_count: int = 0; value: float = 0.5; status: str = "active"
    def to_dict(self): return asdict(self)

class ResearchAssetManager:
    def __init__(self): self._assets: Dict[str, ResearchAsset] = {}
    def register(self, asset: ResearchAsset): self._assets[asset.asset_id] = asset; return asset
    def evaluate(self, asset_id: str) -> Optional[float]:
        asset = self._assets.get(asset_id)
        if not asset: return None
        asset.value = round((asset.performance + min(1.0, asset.usage_count * 0.1)) / 2, 2)
        return asset.value
    def transfer(self, asset_id: str, new_owner: str) -> bool:
        asset = self._assets.get(asset_id)
        if not asset: return False
        asset.owner = new_owner; return True
    def retire(self, asset_id: str) -> bool:
        asset = self._assets.get(asset_id)
        if not asset: return False
        asset.status = "retired"; return True
    def list_assets(self, asset_type: Optional[str] = None) -> List[ResearchAsset]:
        if asset_type: return [a for a in self._assets.values() if a.asset_type == asset_type]
        return list(self._assets.values())
    def count(self) -> int: return len(self._assets)
