"""Institution Director v1 - manage entire AI institution."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.institution.governance import ResearchGovernanceEngine, ResearchPolicy
from engine.institution.departments import ResearchDepartmentManager, ResearchDepartment
from engine.institution.career import ResearchCareerManager, ScientistProfile
from engine.publication import ResearchPublicationSystem, Publication

class InstitutionDirector:
    def __init__(self):
        self._governance = ResearchGovernanceEngine()
        self._departments = ResearchDepartmentManager()
        self._career = ResearchCareerManager()
        self._publications = ResearchPublicationSystem()
    def get_summary(self) -> Dict[str, Any]:
        return {"policies": self._governance.count(), "departments": self._departments.count(),
                "scientists": self._career.count(), "publications": self._publications.count()}
    def get_governance(self): return self._governance
    def get_departments(self): return self._departments
    def get_career(self): return self._career
    def get_publications(self): return self._publications
