"""Combination Generator - generate diverse candidate combinations."""
from __future__ import annotations
import random
from typing import Any, Dict, List, Optional, Set, Tuple

class CombinationGenerator:
    @staticmethod
    def generate_random(numbers: List[int], count: int, seed: Optional[int] = None) -> List[int]:
        rng = random.Random(seed)
        return sorted(rng.sample(numbers, min(count, len(numbers))))

    @staticmethod
    def generate_multiple(pool: List[int], combination_size: int, num_combinations: int, seed: Optional[int] = None) -> List[List[int]]:
        rng = random.Random(seed)
        result = []
        for _ in range(num_combinations):
            result.append(sorted(rng.sample(pool, min(combination_size, len(pool)))))
        return result

    @staticmethod
    def generate_from_strategies(pool: List[int], combination_size: int, strategies: List[str], params: Optional[Dict[str,Any]] = None) -> List[List[int]]:
        result = []
        for s in strategies:
            if s == "random":
                c = CombinationGenerator.generate_random(pool, combination_size)
                result.append(c)
            elif s == "even":
                evens = [n for n in pool if n % 2 == 0]
                c = sorted(random.sample(evens, min(combination_size, len(evens)))) if len(evens) >= combination_size else evens[:combination_size]
                result.append(c)
            elif s == "odd":
                odds = [n for n in pool if n % 2 == 1]
                c = sorted(random.sample(odds, min(combination_size, len(odds)))) if len(odds) >= combination_size else odds[:combination_size]
                result.append(c)
        return result
