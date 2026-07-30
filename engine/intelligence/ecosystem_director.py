"""Ecosystem Director - orchestrate autonomous ecosystem operations."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.ecosystem_operation import EcosystemOperationEngine, EcosystemHealthReport
from engine.autonomous_growth import AutonomousGrowthIntelligence, GrowthForecast
from engine.ecosystem_strategy import EcosystemStrategyPlanner, EcosystemStrategy
from engine.creator_intelligence import CreatorIntelligence, CreatorInsight
from engine.enterprise_success import EnterpriseSuccessIntelligence, EnterpriseHealth
from engine.ecosystem_governance import AutonomousGovernance, GovernancePolicy

class EcosystemDirector:
    def __init__(self):
        self._operation = EcosystemOperationEngine(); self._growth = AutonomousGrowthIntelligence()
        self._strategy = EcosystemStrategyPlanner(); self._creators = CreatorIntelligence()
        self._enterprise = EnterpriseSuccessIntelligence(); self._governance = AutonomousGovernance()
    def run_ecosystem_cycle(self) -> Dict[str, Any]:
        health = self._operation.assess_health()
        forecast = self._growth.predict_growth(health.active_creators, health.total_transactions)
        return {"health": health.to_dict(), "forecast": forecast.to_dict()}
    def get_operation(self): return self._operation; def get_growth(self): return self._growth
    def get_strategy(self): return self._strategy; def get_creators(self): return self._creators
    def get_enterprise(self): return self._enterprise; def get_governance(self): return self._governance
