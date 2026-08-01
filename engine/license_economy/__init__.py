"""Asset License Economy - subscription, enterprise, usage, private deployment licenses."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

LICENSE_TYPES = ["subscription","enterprise","usage","private_deployment"]

@dataclass
class AssetLicense:
    license_id:str
    asset_id:str
    licensee:str
    license_type:str="subscription"
    revenue:float=0.0
    author_earnings:float=0.0
    status:str="active"
    def to_dict(self):
        return asdict(self)

class LicenseEconomyManager:
    def __init__(self):
        self._licenses: Dict[str, AssetLicense] = {}
    def issue(self, l: AssetLicense):
        self._licenses[l.license_id] = l
        return l
    def calculate_earnings(self, lid: str, revenue: float, author_share: float=0.7) -> bool:
        lic = self._licenses.get(lid)
        if not lic: return False
        lic.revenue = revenue; lic.author_earnings = revenue * author_share; return True
    def list_licenses(self) -> List[AssetLicense]: return list(self._licenses.values())
    def total_revenue(self) -> float: return sum(l.revenue for l in self._licenses.values())
    def count(self) -> int: return len(self._licenses)
