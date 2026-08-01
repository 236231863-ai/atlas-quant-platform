"""Access Control System - RBAC, resource permissions, audit logging."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum

ResourceType = Enum("ResourceType", ["DATASET","STRATEGY","MODEL","EXPERIMENT","REPORT","API"])
Action = Enum("Action", ["READ","WRITE","EXECUTE","PUBLISH","MANAGE"])

@dataclass
class AccessControlEntry:
    ace_id:str
    user_id:str
    resource_type:str
    resource_id:str
    permission:str
    def to_dict(self):
        return asdict(self)
@dataclass
class AuditLogEntry:
    log_id:str
    user_id:str
    action:str
    resource:str
    timestamp:str=""
    details:str=""
    def to_dict(self):
        return asdict(self)

class AccessControlSystem:
    def __init__(self):
        self._aces: List[AccessControlEntry] = []
        self._audit: List[AuditLogEntry] = []
    def grant(self, ace: AccessControlEntry):
        self._aces.append(ace)
        return ace
    def check(self, uid: str, resource_type: str, rid: str, action: str) -> bool:
        return any(a.user_id==uid and a.resource_type==resource_type and a.resource_id==rid and a.permission==action for a in self._aces)
    def revoke(self, ace_id: str) -> bool:
        before = len(self._aces); self._aces = [a for a in self._aces if a.ace_id != ace_id]; return len(self._aces) < before
    def log(self, entry: AuditLogEntry):
        self._audit.append(entry)
        return entry
    def get_audit(self) -> List[AuditLogEntry]: return self._audit
    def count_aces(self) -> int: return len(self._aces)
