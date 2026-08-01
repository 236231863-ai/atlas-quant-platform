"""Strategy Marketplace - upgrade community to marketplace."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class StrategyAsset:
    strategy_id:str
    creator:str
    version:str="1.0"
    description:str=""
    backtest_metrics:Dict[str,float]=field(default_factory=dict)
    rating:float=0.0
    license:str="MIT"
    status:str="published"
    def to_dict(self):
        return asdict(self)

class StrategyMarketplace:
    def __init__(self):
        self._assets: Dict[str, StrategyAsset] = {}
    def publish(self, asset: StrategyAsset):
        self._assets[asset.strategy_id] = asset
        return asset
    def fork_strategy(self, sid: str, new_creator: str) -> Optional[StrategyAsset]:
        orig = self._assets.get(sid)
        if not orig: return None
        new = StrategyAsset(strategy_id=f"{sid}_fork_{new_creator}", creator=new_creator, description=f"Fork of {orig.description}", backtest_metrics=dict(orig.backtest_metrics))
        self._assets[new.strategy_id] = new; return new
    def rate_strategy(self, sid: str, rating: float) -> bool:
        asset = self._assets.get(sid)
        if not asset: return False
        asset.rating = (asset.rating + rating) / 2; return True
    def list_strategies(self) -> List[StrategyAsset]: return list(self._assets.values())
    def count(self) -> int: return len(self._assets)
