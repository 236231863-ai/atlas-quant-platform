"""Solution Marketplace - publish, purchase, install industry solutions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class SolutionAsset:
    asset_id:str
    name:str
    asset_type:str
    industry:str
    creator:str
    price:float=0.0
    rating:float=0.0
    version:str="1.0"
    status:str="published"
    def to_dict(self):
        return asdict(self)

class SolutionMarketplace:
    def __init__(self):
        self._assets: Dict[str, SolutionAsset] = {}
    def publish(self, a: SolutionAsset):
        self._assets[a.asset_id] = a
        return a
    def install(self, aid: str, org_id: str) -> bool: return aid in self._assets
    def list_by_industry(self, industry: str) -> List[SolutionAsset]:
        return [a for a in self._assets.values() if a.industry == industry]
    def list_by_type(self, asset_type: str) -> List[SolutionAsset]:
        return [a for a in self._assets.values() if a.asset_type == asset_type]
    def count(self) -> int: return len(self._assets)
