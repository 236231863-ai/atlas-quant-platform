"""Marketplace Dashboard v16 + Marketplace API."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class V16DashboardData:
    creator_metrics:Dict[str,Any]=field(default_factory=dict)
    buyer_metrics:Dict[str,Any]=field(default_factory=dict)
    analytics:Dict[str,Any]=field(default_factory=dict)
    asset_ranking:List[Dict]=field(default_factory=list)
    revenue:Dict[str,Any]=field(default_factory=dict)
    def to_dict(self):
        return asdict(self)

class V16Dashboard:
    def __init__(self):
        self._data = V16DashboardData()
    def update_creator(self, c):
        self._data.creator_metrics = c
    def update_buyer(self, b):
        self._data.buyer_metrics = b
    def get_data(self) -> V16DashboardData: return self._data
    def summary(self):
        return {"creators": len(self._data.creator_metrics), "buyers": len(self._data.buyer_metrics)}

class MarketplaceAPI:
    def __init__(self):
        self._assets: List[Dict]=[]
        self._creators: List[Dict]=[]
        self._purchases: List[Dict]=[]
    def list_assets(self) -> List[Dict]: return self._assets
    def list_creators(self) -> List[Dict]: return self._creators
    def list_purchases(self) -> List[Dict]: return self._purchases
    def record_asset(self, a):
        self._assets.append(a)
    def record_creator(self, c):
        self._creators.append(c)
