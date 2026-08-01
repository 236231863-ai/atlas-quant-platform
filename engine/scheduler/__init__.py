"""Experiment Scheduler - queue, priority, dependencies, retry."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

class ExperimentState(str, Enum):
    CREATED = "created"; QUEUED = "queued"; RUNNING = "running"
    SUCCESS = "success"; FAILED = "failed"; CANCELLED = "cancelled"

@dataclass
class ExperimentJob:
    job_id: str; experiment_id: str; state: ExperimentState = ExperimentState.CREATED
    priority: int = 5; dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0; max_retries: int = 3; error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    def to_dict(self):
        return asdict(self)

class ExperimentScheduler:
    def __init__(self):
        self._jobs: Dict[str, ExperimentJob] = {}
    def create_job(self, job_id: str, exp_id: str, priority: int = 5, deps: Optional[List[str]] = None) -> ExperimentJob:
        job = ExperimentJob(job_id=job_id, experiment_id=exp_id, priority=priority, dependencies=deps or [])
        self._jobs[job_id] = job; return job
    def enqueue(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.state != ExperimentState.CREATED: return False
        for dep_id in job.dependencies:
            dep = self._jobs.get(dep_id)
            if not dep or dep.state != ExperimentState.SUCCESS: return False
        job.state = ExperimentState.QUEUED; return True
    def start(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.state != ExperimentState.QUEUED: return False
        job.state = ExperimentState.RUNNING; return True
    def complete(self, job_id: str, success: bool) -> bool:
        job = self._jobs.get(job_id)
        if not job: return False
        if success: job.state = ExperimentState.SUCCESS
        else:
            if job.retry_count < job.max_retries:
                job.retry_count += 1; job.state = ExperimentState.QUEUED
            else: job.state = ExperimentState.FAILED
        return True
    def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job: return False
        if job.state in [ExperimentState.CREATED, ExperimentState.QUEUED, ExperimentState.RUNNING]:
            job.state = ExperimentState.CANCELLED; return True
        return False
    def list_by_state(self, state: ExperimentState) -> List[ExperimentJob]:
        return [j for j in self._jobs.values() if j.state == state]
    def next_ready(self) -> Optional[ExperimentJob]:
        ready = sorted([j for j in self._jobs.values() if j.state == ExperimentState.QUEUED], key=lambda j: j.priority, reverse=True)
        return ready[0] if ready else None
    def count(self) -> int: return len(self._jobs)
    def report(self) -> Dict[str, int]:
        return {s.value: len(self.list_by_state(s)) for s in ExperimentState}
