"""Atlas Quant Platform - Bayesian Optimization Engine."""
from __future__ import annotations
import math, random
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

class BayesianOptimizer:
    def __init__(self, random_seed: Optional[int] = None): self._rng = random.Random(random_seed)
    @staticmethod
    def expected_improvement(mean: float, std: float, best: float, eps: float = 0.01) -> float:
        if std <= 0: return 0.0
        z = (mean - best - eps) / std; cdf = 0.5 * (1 + math.erf(z / math.sqrt(2)))
        pdf = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
        return (mean - best - eps) * cdf + std * pdf
    def optimize(self, fn: Callable, space: Dict[str, List[Any]], n_trials: int = 30, n_init: int = 5) -> Dict[str, Any]:
        keys = list(space.keys()); trials, scores = [], []
        for i in range(n_trials):
            if i < n_init:
                params = {k: self._rng.choice(space[k]) for k in keys}
            else:
                bi = max(range(len(scores)), key=lambda j: scores[j]) if scores else 0
                params = trials[bi].copy() if trials else {}
                if params: params[keys[self._rng.randint(0,len(keys)-1)]] = self._rng.choice(space[keys[self._rng.randint(0,len(keys)-1)]])
            try:
                s = fn(params); trials.append(params); scores.append(s)
            except: continue
        bi = max(range(len(scores)), key=lambda j: scores[j]) if scores else 0
        return {"best_params":trials[bi] if trials else {},"best_score":scores[bi] if scores else 0,"n_trials":len(trials),"history":[{"params":p,"score":s} for p,s in zip(trials,scores)]}
