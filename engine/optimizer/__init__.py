"""Atlas Quant Platform - Optimizer Engine.

Parameter optimization for strategy parameters.
Supports grid search and (optionally) Optuna.
"""
from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

from engine import EngineResult


@dataclass
class OptimizationResult:
    """Result of a parameter optimization run."""
    best_params: Dict[str, Any]
    best_score: float
    all_scores: List[Dict[str, Any]]
    param_space: Dict[str, List[Any]]
    objective: str
    n_trials: int
    best_trial_index: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def grid_search(
    objective_fn: Callable[[Dict[str, Any]], float],
    param_space: Dict[str, List[Any]],
    maximize: bool = True,
) -> OptimizationResult:
    """Grid search optimization.

    Args:
        objective_fn: Function that takes params dict and returns a score.
        param_space: Dict of param_name -> list of possible values.
        maximize: If True, maximize the score; if False, minimize.

    Returns:
        OptimizationResult with best parameters and all scores.
    """
    keys = list(param_space.keys())
    values = list(param_space.values())
    all_scores: List[Dict[str, Any]] = []

    best_score = -float("inf") if maximize else float("inf")
    best_params = {}
    best_idx = 0

    for i, combo in enumerate(itertools.product(*values)):
        params = dict(zip(keys, combo))
        try:
            score = objective_fn(params)
        except Exception:
            continue

        all_scores.append({"params": params, "score": score})
        if (maximize and score > best_score) or (not maximize and score < best_score):
            best_score = score
            best_params = params
            best_idx = i

    return OptimizationResult(
        best_params=best_params,
        best_score=best_score,
        all_scores=all_scores,
        param_space=param_space,
        objective="maximize" if maximize else "minimize",
        n_trials=len(all_scores),
        best_trial_index=best_idx,
    )


def random_search(
    objective_fn: Callable[[Dict[str, Any]], float],
    param_space: Dict[str, List[Any]],
    n_trials: int = 50,
    maximize: bool = True,
    random_seed: Optional[int] = None,
) -> OptimizationResult:
    """Random search optimization.

    Instead of exhaustive grid search, randomly sample the parameter space.
    More efficient for high-dimensional spaces.
    """
    rng = random.Random(random_seed)
    keys = list(param_space.keys())
    all_scores: List[Dict[str, Any]] = []

    best_score = -float("inf") if maximize else float("inf")
    best_params = {}
    best_idx = 0

    for i in range(n_trials):
        params = {}
        for k in keys:
            params[k] = rng.choice(param_space[k])
        try:
            score = objective_fn(params)
        except Exception:
            continue

        all_scores.append({"params": params, "score": score})
        if (maximize and score > best_score) or (not maximize and score < best_score):
            best_score = score
            best_params = params
            best_idx = i

    return OptimizationResult(
        best_params=best_params,
        best_score=best_score,
        all_scores=all_scores,
        param_space=param_space,
        objective="maximize" if maximize else "minimize",
        n_trials=len(all_scores),
        best_trial_index=best_idx,
    )
