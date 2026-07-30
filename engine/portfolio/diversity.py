"""Diversity Optimizer - maximize coverage, minimize similarity."""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Set, Tuple

class DiversityOptimizer:
    @staticmethod
    def jaccard_similarity(a: List[int], b: List[int]) -> float:
        sa, sb = set(a), set(b)
        if not sa and not sb: return 0.0
        intersection = len(sa & sb)
        union = len(sa | sb)
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def pairwise_diversity(combinations: List[List[int]]) -> float:
        if len(combinations) < 2: return 1.0
        total_sim = 0.0; pairs = 0
        for i in range(len(combinations)):
            for j in range(i+1, len(combinations)):
                total_sim += DiversityOptimizer.jaccard_similarity(combinations[i], combinations[j])
                pairs += 1
        avg_sim = total_sim / pairs if pairs > 0 else 0
        return 1.0 - avg_sim

    @staticmethod
    def coverage_score(combinations: List[List[int]], total_range: int) -> float:
        all_nums: Set[int] = set()
        for c in combinations:
            all_nums.update(c)
        return len(all_nums) / total_range if total_range > 0 else 0.0

    @staticmethod
    def optimize(combinations: List[List[int]], pool: List[int], max_iterations: int = 1000, seed: Optional[int] = None) -> List[List[int]]:
        rng = random.Random(seed)
        best = [c[:] for c in combinations]
        best_diversity = DiversityOptimizer.pairwise_diversity(best)
        for _ in range(max_iterations):
            candidate = [c[:] for c in best]
            idx = rng.randint(0, len(candidate) - 1)
            if candidate[idx] and pool:
                old_num = rng.choice(candidate[idx])
                new_num = rng.choice(pool)
                if new_num not in candidate[idx]:
                    candidate[idx][candidate[idx].index(old_num)] = new_num
                    candidate[idx].sort()
            div = DiversityOptimizer.pairwise_diversity(candidate)
            if div > best_diversity:
                best = candidate; best_diversity = div
        return best
