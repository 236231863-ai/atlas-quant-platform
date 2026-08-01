"""Recommendation Marketplace - intelligent recommendation engine for all assets."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class RecommendedAsset:
    asset_id:str
    asset_type:str
    score:float=0.0
    reason:str=""
    similarity:float=0.0
    def to_dict(self):
        return asdict(self)

class RecommendationMarket:
    def __init__(self):
        self._user_history: Dict[str, List[str]] = {}
        self._assets: Dict[str, str] = {}
    def register_asset(self, aid: str, a_type: str):
        self._assets[aid] = a_type
    def record_interaction(self, uid: str, aid: str):
        if uid not in self._user_history: self._user_history[uid] = []
        self._user_history[uid].append(aid)
    def recommend(self, uid: str, limit: int = 5) -> List[RecommendedAsset]:
        history = self._user_history.get(uid, [])
        if not history: return [RecommendedAsset("basic_analysis","strategy",0.5,"Start with basic analysis",0.0)]
        inter_types = set(self._assets.get(a, "") for a in history if a in self._assets)
        recs = []
        for aid, at in self._assets.items():
            if aid not in history and at in inter_types:
                recs.append(RecommendedAsset(aid, at, 0.7, f"Based on your interest in {at}", 0.6))
        return recs[:limit]
    def count_assets(self) -> int: return len(self._assets)
