"""Platform Director - unified platform health, version, risk, security, resource management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.reliability import ReliabilityEngine, PlatformReliabilityScore
from engine.resilience import RecoveryEngine, RecoveryRecord
from engine.quality import QualityGateEngine, ReleaseQualityReport
from engine.security import SecurityAuditEngine, SecurityReport

class PlatformDirector:
    def __init__(self):
        self._reliability = ReliabilityEngine(); self._resilience = RecoveryEngine()
        self._quality = QualityGateEngine(); self._security = SecurityAuditEngine()
    def run_platform_cycle(self) -> Dict[str, Any]:
        reliability = self._reliability.assess()
        security = self._security.audit()
        return {"reliability": reliability.to_dict(), "security": security.to_dict()}
    def get_reliability(self): return self._reliability; def get_resilience(self): return self._resilience
    def get_quality(self): return self._quality; def get_security(self): return self._security
