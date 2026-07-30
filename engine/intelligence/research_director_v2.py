"""Research Director - autonomous experiment lifecycle management v2."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from engine.sandbox import ExperimentSandbox, SandboxSnapshot
from engine.experiment import ExperimentDefinition
from engine.scheduler import ExperimentScheduler, ExperimentJob, ExperimentState
from engine.execution import ExperimentRunner, ExecutionResult
from engine.knowledge import KnowledgeBase, KnowledgeRecord
from engine.review import ResearchReviewSystem, ReviewState
from engine.scoring import ResearchScoreEngine, ResearchScore
from engine.backtest.models import BacktestMetrics

class ResearchDirectorV2:
    def __init__(self):
        self._sandbox = ExperimentSandbox()
        self._scheduler = ExperimentScheduler()
        self._runner = ExperimentRunner()
        self._knowledge = KnowledgeBase()
        self._review = ResearchReviewSystem()

    def propose_experiment(self, objective: str, params: Dict[str, Any], seed: Optional[int] = None) -> str:
        exp_id = f"exp_{len(list(self._sandbox._snapshots.keys())) + 1}"
        self._sandbox.create(exp_id, params, seed)
        self._review.propose(exp_id)
        self._knowledge.add(KnowledgeRecord(id=f"proposal_{exp_id}", type="proposal",
            content=objective, tags=["proposal"], metadata={"experiment_id":exp_id, "params":params}))
        return exp_id

    def define_experiment(self, exp_id: str, strategy: str, dataset: str, features: List[str]) -> ExperimentDefinition:
        snap = self._sandbox.get(exp_id)
        params = snap.parameters if snap else {}
        return ExperimentDefinition(experiment_id=exp_id, strategy=strategy, dataset=dataset,
            features=features, parameters=params)

    def approve_and_schedule(self, exp_id: str, priority: int = 5) -> bool:
        if not self._review.approve(exp_id): return False
        job = self._scheduler.create_job(f"job_{exp_id}", exp_id, priority)
        return self._scheduler.enqueue(job.job_id)

    def execute_and_score(self, exp_id: str, metrics: BacktestMetrics) -> ResearchScore:
        self._review.start_running(exp_id)
        score = ResearchScoreEngine.compute(metrics)
        self._sandbox._snapshots[exp_id].metrics = score.to_dict()
        self._review.complete(exp_id)
        return score

    def get_pipeline_status(self, exp_id: str) -> Dict[str, Any]:
        sandbox = self._sandbox.get(exp_id)
        review = self._review.get(exp_id)
        return {"experiment_id": exp_id, "sandbox_exists": sandbox is not None,
                "review_state": review.state.value if review else "unknown"}
