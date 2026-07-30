"""Enterprise Workspace - organizations, teams, members."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class Organization: org_id:str; name:str; owner:str; created_at:str=""; def to_dict(self):return asdict(self)
@dataclass
class Team: team_id:str; org_id:str; name:str; members:List[str]=field(default_factory=list); def to_dict(self):return asdict(self)

class EnterpriseWorkspace:
    def __init__(self): self._orgs: Dict[str, Organization] = {}; self._teams: Dict[str, Team] = {}
    def create_org(self, org: Organization): self._orgs[org.org_id] = org; return org
    def create_team(self, team: Team): self._teams[team.team_id] = team; return team
    def invite_member(self, team_id: str, user_id: str) -> bool:
        t = self._teams.get(team_id)
        if not t: return False
        t.members.append(user_id); return True
    def list_orgs(self) -> List[Organization]: return list(self._orgs.values())
    def list_teams(self, org_id: str) -> List[Team]:
        return [t for t in self._teams.values() if t.org_id == org_id]
    def count_orgs(self) -> int: return len(self._orgs)
