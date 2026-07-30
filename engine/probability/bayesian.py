import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class BayesianResult:
    number: int; prior_alpha: float; prior_beta: float; posterior_alpha: float; posterior_beta: float
    prior_mean: float; posterior_mean: float; credible_interval_lower: float; credible_interval_upper: float
    evidence_count: int; probability_change: float
    def to_dict(self): return asdict(self)

class BayesianEngine:
    @staticmethod
    def analyze_number(number: int, occurrences: int, total_draws: int, prior_alpha: float = 1.0, prior_beta: float = 1.0) -> BayesianResult:
        if total_draws <= 0: raise ValueError("total_draws must be positive")
        if occurrences < 0: raise ValueError("occurrences cannot be negative")
        failures = total_draws - occurrences
        pa, pb = prior_alpha + occurrences, prior_beta + failures
        pm = prior_alpha / (prior_alpha + prior_beta) if (prior_alpha + prior_beta) > 0 else 0.5
        pom = pa / (pa + pb)
        z = 1.96; std = math.sqrt(pa * pb / ((pa + pb) ** 2 * (pa + pb + 1))) if pa + pb > 1 else 0.5
        lo, hi = max(0.0, pom - z * std), min(1.0, pom + z * std)
        return BayesianResult(number=number, prior_alpha=prior_alpha, prior_beta=prior_beta,
            posterior_alpha=pa, posterior_beta=pb, prior_mean=round(pm,6), posterior_mean=round(pom,6),
            credible_interval_lower=round(lo,6), credible_interval_upper=round(hi,6),
            evidence_count=occurrences, probability_change=round(pom - pm,6))

    @staticmethod
    def analyze_batch(occurrence_counts: Dict[int, int], total_draws: int, prior_alpha: float = 1.0, prior_beta: float = 1.0) -> List[BayesianResult]:
        results = [BayesianEngine.analyze_number(n, o, total_draws, prior_alpha, prior_beta) for n, o in occurrence_counts.items()]
        results.sort(key=lambda r: r.posterior_mean, reverse=True); return results

    @staticmethod
    def sequential_posterior(initial_alpha: float, initial_beta: float, observations: List[int]) -> List[Tuple[float, float, float, float]]:
        a, b, hist = initial_alpha, initial_beta, []
        for o in observations:
            if o == 1: a += 1
            else: b += 1
            m = a / (a + b); s = math.sqrt(a * b / ((a + b) ** 2 * (a + b + 1))) if a + b > 1 else 0.5
            hist.append((a, b, round(m, 6), round(s, 6)))
        return hist
