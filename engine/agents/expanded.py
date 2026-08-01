"""Research Agent Expansion - specialized research agents."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from engine.agent_protocol import ResearchTask, AgentResult

@dataclass
class AgentDefinition:
    agent_id: str; role: str; description: str; input_schema: List[str]; output_schema: List[str]
    def to_dict(self):
        return asdict(self)

class DiscoveryAgent:
    def __init__(self):
        self._id = "discovery_agent"
    @property
    def definition(self) -> AgentDefinition:
        return AgentDefinition(self._id,"Discovery","Discover research opportunities",
            ["discovery_report"],["research_task"])
    def analyze(self, report: Dict[str, Any]) -> ResearchTask:
        discoveries = report.get("discoveries", [])
        top = discoveries[0] if discoveries else {}
        return ResearchTask(task_id=f"task_{self._id}_{len(discoveries)}",type="discovery",
            objective=top.get("recommendation","explore"),params=top)

class PatternAgent:
    def __init__(self):
        self._id = "pattern_agent"
    @property
    def definition(self) -> AgentDefinition:
        return AgentDefinition(self._id,"Pattern","Extract research patterns",
            ["patterns","experiments"],["insights"])
    def analyze(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"agent":"pattern_agent","patterns_found":len(patterns),
                "top_pattern": patterns[0] if patterns else {}}

class StrategyArchitectAgent:
    def __init__(self):
        self._id = "strategy_architect"
    @property
    def definition(self) -> AgentDefinition:
        return AgentDefinition(self._id,"Strategy Architect","Design strategy templates",
            ["patterns","knowledge"],["strategy_candidates"])
    def design(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"strategy_id":f"arch_{i}","source":"architect","pattern":p} for i,p in enumerate(patterns[:3])]

class ExperimentManagerAgent:
    def __init__(self):
        self._id = "experiment_manager"
    @property
    def definition(self) -> AgentDefinition:
        return AgentDefinition(self._id,"Experiment Manager","Manage experiments",
            ["experiment_definitions"],["experiment_plan"])
    def plan(self, strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {"agent":"experiment_manager","experiments_planned":len(strategies)}

class BenchmarkAgent:
    def __init__(self):
        self._id = "benchmark_agent"
    @property
    def definition(self) -> AgentDefinition:
        return AgentDefinition(self._id,"Benchmark","Evaluate strategy performance",
            ["strategy_results"],["benchmark_scores"])
    def evaluate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        scores = [r.get("score",0) for r in results]
        return {"agent":"benchmark_agent","avg_score":sum(scores)/len(scores) if scores else 0,"count":len(results)}

class ResearchHistorianAgent:
    def __init__(self):
        self._id = "research_historian"
    @property
    def definition(self) -> AgentDefinition:
        return AgentDefinition(self._id,"Research Historian","Track research history",
            ["experiments","results","decisions"],["history_report"])
    def summarize(self, experiments: List[Dict[str, Any]]) -> str:
        return f"Research historian report: {len(experiments)} experiments tracked."
