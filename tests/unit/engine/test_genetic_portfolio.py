"""Tests for Genetic Portfolio Optimizer."""
from __future__ import annotations
import pytest
from engine.portfolio.genetic import GeneticPortfolioOptimizer, PortfolioOptimizationResult

class TestGeneticPortfolio:
    def test_init_pool(self):
        g = GeneticPortfolioOptimizer(list(range(1,36)), 5)
        assert g._pool[0] == 1
    def test_optimize_returns_result(self):
        g = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        r = g.optimize(generations=5, mut_rate=0.2, elite=2)
        assert isinstance(r, PortfolioOptimizationResult)
    def test_best_fitness_positive(self):
        g = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        r = g.optimize(generations=5, mut_rate=0.2, elite=2)
        assert r.best_fitness > 0
    def test_population_returned(self):
        g = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        r = g.optimize(generations=5, mut_rate=0.2, elite=2)
        assert len(r.best_population) == 10
    def test_convergence_rate(self):
        g = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        r = g.optimize(generations=5, mut_rate=0.2, elite=2)
        assert r.convergence_rate != 0
    def test_reproducible_seed(self):
        g1 = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        g2 = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        r1 = g1.optimize(generations=5); r2 = g2.optimize(generations=5)
        assert r1.best_fitness == r2.best_fitness
    def test_different_seeds(self):
        g1 = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=1)
        g2 = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=99)
        r1 = g1.optimize(generations=5); r2 = g2.optimize(generations=5)
        assert r1.fitness_history != r2.fitness_history or r1.best_fitness != r2.best_fitness
    def test_gen_count(self):
        g = GeneticPortfolioOptimizer(list(range(1,20)), 5, pop_size=10, seed=42)
        r = g.optimize(generations=10)
        assert len(r.fitness_history) == 10
class X2: pass
class X3: pass

