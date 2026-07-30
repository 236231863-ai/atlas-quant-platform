"""Atlas Quant Platform - Strategy Engine.

策略引擎: JSON定义、注册、校验、评估。
Pure computation: no IO, no database.
"""
from __future__ import annotations

from engine.strategy.registry import StrategyDefinition, StrategyRegistry
from engine.strategy.evaluator import StrategyEvaluator

__all__ = [
    "StrategyDefinition", "StrategyRegistry",
    "StrategyEvaluator",
]
