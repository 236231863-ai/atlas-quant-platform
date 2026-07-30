"""Tests for StrategyRegistry and StrategyDefinition."""
from __future__ import annotations

import pytest
from engine.strategy.registry import StrategyDefinition, StrategyRegistry


class TestStrategyDefinition:
    def test_from_dict(self):
        s = StrategyDefinition.from_dict({
            "strategy_id": "test", "name": "Test", "strategy_type": "random", "params": {},
        })
        assert s.strategy_id == "test"

    def test_from_json(self):
        s = StrategyDefinition.from_json(
            '{"strategy_id": "jtest", "name": "JTest", "strategy_type": "hot", "params": {}}'
        )
        assert s.strategy_id == "jtest"
        assert s.strategy_type == "hot"

    def test_validate_valid(self):
        s = StrategyDefinition({"strategy_id": "v", "name": "V", "strategy_type": "random", "params": {}})
        assert s.is_valid()
        assert s.validate() == []

    def test_validate_missing_id(self):
        s = StrategyDefinition({"name": "X", "strategy_type": "random", "params": {}})
        assert not s.is_valid()
        assert "strategy_id" in s.validate()[0]

    def test_validate_missing_name(self):
        s = StrategyDefinition({"strategy_id": "x", "strategy_type": "random", "params": {}})
        assert not s.is_valid()

    def test_validate_unknown_type(self):
        s = StrategyDefinition({"strategy_id": "x", "name": "X", "strategy_type": "unknown", "params": {}})
        assert not s.is_valid()

    def test_default_values(self):
        s = StrategyDefinition({"strategy_id": "x", "name": "X", "strategy_type": "random", "params": {}})
        assert s.version == 1
        assert s.combinator == "AND"

    def test_to_dict(self):
        s = StrategyDefinition({"strategy_id": "x", "name": "X", "strategy_type": "fixed", "params": {"numbers": [1, 2]}})
        d = s.to_dict()
        assert d["strategy_type"] == "fixed"
        assert d["params"]["numbers"] == [1, 2]

    def test_metadata_optional(self):
        s = StrategyDefinition({"strategy_id": "x", "name": "X", "strategy_type": "random", "params": {}})
        assert s.metadata == {}


class TestStrategyRegistry:
    def setup_method(self):
        self.reg = StrategyRegistry()

    def test_initial_empty(self):
        assert self.reg.count() == 0

    def test_register_strategy(self):
        s = StrategyDefinition({"strategy_id": "a", "name": "A", "strategy_type": "random", "params": {}})
        self.reg.register(s)
        assert self.reg.count() == 1

    def test_get_registered(self):
        s = StrategyDefinition({"strategy_id": "b", "name": "B", "strategy_type": "hot", "params": {}})
        self.reg.register(s)
        assert self.reg.get("b") is not None

    def test_get_nonexistent(self):
        assert self.reg.get("nonexistent") is None

    def test_register_invalid_raises(self):
        s = StrategyDefinition({"name": "NoID", "strategy_type": "random", "params": {}})
        with pytest.raises(ValueError, match="Invalid"):
            self.reg.register(s)

    def test_list_ids(self):
        s1 = StrategyDefinition({"strategy_id": "x", "name": "X", "strategy_type": "random", "params": {}})
        s2 = StrategyDefinition({"strategy_id": "y", "name": "Y", "strategy_type": "cold", "params": {}})
        self.reg.register_many([s1, s2])
        ids = self.reg.list_ids()
        assert "x" in ids
        assert "y" in ids

    def test_register_builtin(self):
        self.reg.register_builtin()
        assert self.reg.count() >= 3
        assert self.reg.get("cold_number_tracker") is not None
        assert self.reg.get("random_selection") is not None

    def test_remove_strategy(self):
        s = StrategyDefinition({"strategy_id": "r", "name": "R", "strategy_type": "random", "params": {}})
        self.reg.register(s)
        assert self.reg.count() == 1
        self.reg.remove("r")
        assert self.reg.count() == 0

    def test_clear_all(self):
        s = StrategyDefinition({"strategy_id": "a", "name": "A", "strategy_type": "random", "params": {}})
        self.reg.register(s)
        self.reg.clear()
        assert self.reg.count() == 0

    def test_list_returns_copy(self):
        s = StrategyDefinition({"strategy_id": "a", "name": "A", "strategy_type": "random", "params": {}})
        self.reg.register(s)
        lst = self.reg.list()
        assert len(lst) == 1
        assert lst[0].strategy_id == "a"
