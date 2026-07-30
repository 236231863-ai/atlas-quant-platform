"""Enterprise Identity Layer - organization, enterprise user, roles, permissions."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

Role = Enum("Role", ["OWNER","ADMIN","RESEARCHER","ANALYST","VIEWER"])
@dataclass
class Organization: org_id:str; name:str; owner_id:str; plan:str="free"; created_at:str=""; def to_dict(self):return asdict(self)
@dataclass
class EnterpriseUser: user_id:str; org_id:str; email:str; role:Role=Role.VIEWER; status:str="active"; def to_dict(self):return asdict(self)

class EnterpriseIdentityManager:
    def __init__(self): self._orgs: Dict[str, Organization] = {}; self._members: Dict[str, List[EnterpriseUser]] = {}
    def create_org(self, org: Organization): self._orgs[org.org_id] = org; self._members[org.org_id] = []; return org
    def invite(self, org_id: str, user: EnterpriseUser) -> bool:
        if org_id not in self._members: return False; self._members[org_id].append(user); return True
    def remove(self, org_id: str, uid: str) -> bool:
        if org_id not in self._members: return False; self._members[org_id] = [m for m in self._members[org_id] if m.user_id != uid]; return True
    def check_permission(self, org_id: str, uid: str, required_role: Role) -> bool:
        members = self._members.get(org_id, []); user = next((m for m in members if m.user_id == uid), None)
        if not user: return False
        return user.role.value <= required_role.value
    def list_members(self, org_id: str) -> List[EnterpriseUser]: return self._members.get(org_id, [])
    def count_orgs(self) -> int: return len(self._orgs)
