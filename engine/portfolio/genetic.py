"""Genetic Algorithm Portfolio Optimizer."""
from __future__ import annotations
import math, random
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.portfolio.diversity import DiversityOptimizer

@dataclass
class PortfolioOptimizationResult:
    best_population: List[List[int]]; generations: int; best_fitness: float
    fitness_history: List[float]; convergence_rate: float
    def to_dict(self):
        return asdict(self)

class GeneticPortfolioOptimizer:
    def __init__(self, pool: List[int], csize: int, pop_size: int = 50, seed: Optional[int] = None):
        self._pool = pool; self._csize = csize; self._psize = pop_size; self._rng = random.Random(seed)
    def _random(self) -> List[int]:
        return sorted(self._rng.sample(self._pool, min(self._csize, len(self._pool))))
    def _fitness(self, ind: List[int], pop: List[List[int]]) -> float:
        cov = DiversityOptimizer.coverage_score(pop, len(self._pool))
        ent = len(set(ind)) / self._csize if self._csize > 0 else 0
        return cov * 0.5 + ent * 0.5
    def _select(self, pop: List[List[int]], fits: List[float]) -> List[int]:
        i1, i2 = self._rng.randint(0,len(pop)-1), self._rng.randint(0,len(pop)-1)
        return pop[i1] if fits[i1] > fits[i2] else pop[i2]
    def _crossover(self, p1: List[int], p2: List[int]) -> List[int]:
        cut = self._rng.randint(1, min(len(p1),len(p2))-1) if min(len(p1),len(p2)) > 2 else 1
        child = sorted(set(p1[:cut] + p2[cut:])); pool_set = set(self._pool)
        while len(child) < self._csize:
            n = self._rng.choice(list(pool_set - set(child)))
            child.append(n); child.sort()
        return child[:self._csize]
    def _mutate(self, ind: List[int], rate: float = 0.1) -> List[int]:
        r = list(ind); pool_set = set(self._pool)
        for i in range(len(r)):
            if self._rng.random() < rate:
                new_n = self._rng.choice(list(pool_set - set(r)))
                r[i] = new_n
        return sorted(r)
    def optimize(self, generations: int = 100, mut_rate: float = 0.1, elite: int = 2) -> PortfolioOptimizationResult:
        pop = [self._random() for _ in range(self._psize)]
        fhist = []
        for gen in range(generations):
            fits = [self._fitness(ind, pop) for ind in pop]
            fhist.append(max(fits))
            new_pop = [pop[i] for i in sorted(range(len(fits)), key=lambda j: fits[j], reverse=True)[:elite]]
            while len(new_pop) < self._psize:
                p1 = self._select(pop, fits); p2 = self._select(pop, fits)
                child = self._mutate(self._crossover(p1, p2), mut_rate)
                new_pop.append(child)
            pop = new_pop
        final_fits = [self._fitness(ind, pop) for ind in pop]
        bi = final_fits.index(max(final_fits))
        cr = (fhist[-1] - fhist[0]) / (fhist[0] + 0.001) if generations > 1 else 0
        return PortfolioOptimizationResult(best_population=pop[:10], generations=generations,
            best_fitness=max(final_fits), fitness_history=fhist, convergence_rate=round(cr, 4))
