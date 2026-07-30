"""
Atlas Quant Platform - Strategy Registry.

Loads, validates, and manages strategy definitions from JSON.
Strategies are data, not code. Pure computation, no IO.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class StrategyDefinition:
    """Strategy definition loaded from JSON data.

    A strategy is a JSON object with rules that define how to select numbers.
    """

    def __init__(self, strategy_json: Dict[str, Any]) -> None:
        self.raw: Dict[str, Any] = strategy_json
        self.strategy_id: str = strategy_json.get("strategy_id", "")
        self.name: str = strategy_json.get("name", "")
        self.version: int = strategy_json.get("version", 1)
        self.strategy_type: str = strategy_json.get("strategy_type", "gap_based")
        self.params: Dict[str, Any] = strategy_json.get("params", {})
        self.combinator: str = strategy_json.get("combinator", "AND")
        self.metadata: Dict[str, Any] = strategy_json.get("metadata", {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StrategyDefinition:
        return cls(data)

    @classmethod
    def from_json(cls, json_str: str) -> StrategyDefinition:
        return cls(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "version": self.version,
            "strategy_type": self.strategy_type,
            "params": self.params,
            "combinator": self.combinator,
            "metadata": self.metadata,
        }

    def validate(self) -> List[str]:
        """Validate strategy definition. Returns list of error messages."""
        errors: List[str] = []
        if not self.strategy_id:
            errors.append("strategy_id is required")
        if not self.name:
            errors.append("name is required")
        if not self.strategy_type:
            errors.append("strategy_type is required")
        valid_types = {"gap_based", "hot", "cold", "fixed", "random", "even", "odd", "mixed"}
        if self.strategy_type not in valid_types:
            errors.append(f"Unknown strategy_type: {self.strategy_type}. Valid: {valid_types}")
        if self.params is None:
            errors.append("params must be a dict")
        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0


class StrategyRegistry:
    """Registry for managing strategy definitions."""

    def __init__(self) -> None:
        self._strategies: Dict[str, StrategyDefinition] = {}

    def register(self, strategy: StrategyDefinition) -> None:
        """Register a strategy definition."""
        if not strategy.is_valid():
            raise ValueError(f"Invalid strategy: {strategy.validate()}")
        self._strategies[strategy.strategy_id] = strategy

    def register_many(self, strategies: List[StrategyDefinition]) -> None:
        for s in strategies:
            self.register(s)

    def get(self, strategy_id: str) -> Optional[StrategyDefinition]:
        return self._strategies.get(strategy_id)

    def list(self) -> List[StrategyDefinition]:
        return list(self._strategies.values())

    def list_ids(self) -> List[str]:
        return list(self._strategies.keys())

    def remove(self, strategy_id: str) -> None:
        self._strategies.pop(strategy_id, None)

    def clear(self) -> None:
        self._strategies.clear()

    def count(self) -> int:
        return len(self._strategies)

    def register_builtin(self) -> None:
        """Register built-in strategy templates."""
        builtins = [
            StrategyDefinition({
                "strategy_id": "cold_number_tracker",
                "name": "冷号追踪策略",
                "version": 1,
                "strategy_type": "gap_based",
                "params": {"min_gap": 10},
                "combinator": "AND",
                "metadata": {"author": "system", "description": "追踪遗漏超过10期的冷号"},
            }),
            StrategyDefinition({
                "strategy_id": "hot_number_tracker",
                "name": "热号追踪策略",
                "version": 1,
                "strategy_type": "hot",
                "params": {},
                "combinator": "AND",
                "metadata": {"author": "system", "description": "追踪出现频率最高的热号"},
            }),
            StrategyDefinition({
                "strategy_id": "random_selection",
                "name": "随机选号策略",
                "version": 1,
                "strategy_type": "random",
                "params": {},
                "combinator": "OR",
                "metadata": {"author": "system", "description": "完全随机选号（基准线）"},
            }),
            StrategyDefinition({
                "strategy_id": "even_odd_balanced",
                "name": "奇偶平衡策略",
                "version": 1,
                "strategy_type": "gap_based",
                "params": {"min_gap": 5},
                "combinator": "AND",
                "metadata": {"author": "system", "description": "在冷号中平衡奇偶比"},
            }),
        ]
        self.register_many(builtins)
