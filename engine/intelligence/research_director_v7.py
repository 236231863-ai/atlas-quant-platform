"""Research Director v7 - global resource allocation, model selection, node coordination."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.model_network import ModelRegistry, ModelNode
from engine.agent_personality import PersonalityManager
from engine.global_network import ResearchNodeNetwork, NetworkNode
from engine.mission import ResearchMissionManager, ResearchMission
from engine.knowledge_exchange import KnowledgeExchangeEngine, KnowledgeExchangeRecord

class ResearchDirectorV7:
    def __init__(self):
        self._models = ModelRegistry()
        self._personalities = PersonalityManager()
        self._network = ResearchNodeNetwork()
        self._missions = ResearchMissionManager()
        self._exchange = KnowledgeExchangeEngine()

    def allocate_global_resources(self) -> Dict[str, Any]:
        return {"models": self._models.count(), "personalities": self._personalities.count(),
                "nodes": self._network.count(), "missions": self._missions.count(),
                "exchanges": self._exchange.count()}

    def select_model(self, required: str) -> Optional[ModelNode]:
        return self._models.select_best(required)

    def coordinate_nodes(self) -> Dict[str, Any]:
        return self._network.aggregate_results()

    def supervise_mission(self, mission: ResearchMission) -> ResearchMission:
        return self._missions.create_mission(mission)

    def manage_exchange(self, record: KnowledgeExchangeRecord) -> KnowledgeExchangeRecord:
        return self._exchange.publish_insight(record)

    def get_models(self):
        return self._models
    def get_personalities(self):
        return self._personalities
    def get_network(self):
        return self._network
    def get_missions(self):
        return self._missions
    def get_exchange(self):
        return self._exchange
