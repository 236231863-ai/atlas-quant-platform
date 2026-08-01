"""Multi-Tenant SaaS Layer - tenant isolation, quotas, configuration."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class TenantQuota:
    api_calls:int=1000
    experiments:int=50
    storage_gb:int=10
    agents:int=5
    def to_dict(self):
        return asdict(self)
@dataclass
class Tenant:
    tenant_id:str
    name:str
    plan:str="free"
    quota:TenantQuota=field(default_factory=TenantQuota)
    status:str="active"
    def to_dict(self):
        return asdict(self)

class TenantManager:
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}
    def create(self, tenant: Tenant):
        self._tenants[tenant.tenant_id] = tenant
        return tenant
    def check_quota(self, tid: str, resource: str) -> bool:
        t = self._tenants.get(tid)
        if not t: return False
        return getattr(t.quota, resource, 0) > 0
    def update_quota(self, tid: str, quota: TenantQuota) -> bool:
        t = self._tenants.get(tid)
        if not t: return False; t.quota = quota; return True
    def get_tenant(self, tid: str) -> Optional[Tenant]: return self._tenants.get(tid)
    def count(self) -> int: return len(self._tenants)
