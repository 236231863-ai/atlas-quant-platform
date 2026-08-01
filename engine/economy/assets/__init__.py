"""Scientific Asset Economy - manage asset pricing, licensing, transfer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AssetPrice:
    asset_id: str; base_value: float; usage_score: float; impact_score: float; demand_score: float
    final_price: float = 0.0
    def compute(self):
        self.final_price = round((self.base_value+self.usage_score+self.impact_score+self.demand_score)/4, 2)
    def to_dict(self):
        return asdict(self)

class ScientificAssetMarket:
    def __init__(self):
        self._prices: Dict[str, AssetPrice] = {}
    def register(self, price: AssetPrice):
        price.compute()
        self._prices[price.asset_id] = price
        return price
    def price_asset(self, asset_id: str) -> Optional[float]:
        p = self._prices.get(asset_id); return p.final_price if p else None
    def transfer(self, asset_id: str, new_owner: str) -> bool: return True
    def retire(self, asset_id: str) -> bool:
        return bool(self._prices.pop(asset_id, None))
    def list_assets(self) -> List[AssetPrice]: return list(self._prices.values())
    def count(self) -> int: return len(self._prices)
