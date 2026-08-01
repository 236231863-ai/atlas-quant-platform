"""Data Marketplace - data asset exchange."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class DataAsset:
    id:str
    creator:str
    dataset_type:str
    description:str
    schema:List[str]=field(default_factory=list)
    version:str="1.0"
    license:str="MIT"
    status:str="published"
    def to_dict(self):
        return asdict(self)

class DataMarketplace:
    def __init__(self):
        self._assets: Dict[str, DataAsset] = {}
    def upload(self, asset: DataAsset):
        self._assets[asset.id] = asset
        return asset
    def list_datasets(self, dt: Optional[str]=None) -> List[DataAsset]:
        if dt: return [a for a in self._assets.values() if a.dataset_type == dt]
        return list(self._assets.values())
    def count(self) -> int: return len(self._assets)
