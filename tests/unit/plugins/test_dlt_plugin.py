"""Tests for DLT plugin."""
from __future__ import annotations

import pytest

from plugins.dlt.plugin import DltPlugin, DLT_MANIFEST


class TestDltPlugin:
    def setup_method(self) -> None:
        self.plugin = DltPlugin()

    def test_plugin_manifest_id(self) -> None:
        assert self.plugin.manifest.id == "dlt"

    def test_plugin_manifest_name(self) -> None:
        assert self.plugin.manifest.name == "大乐透"

    def test_plugin_register_changes_state(self) -> None:
        from core.types import PluginState
        assert self.plugin.state == PluginState.REGISTERED
        self.plugin.register()
        assert self.plugin.state == PluginState.ACTIVE

    def test_get_lottery_type_code(self) -> None:
        lt = self.plugin.get_lottery_type()
        assert lt.code == "dlt"

    def test_get_lottery_type_main_range(self) -> None:
        lt = self.plugin.get_lottery_type()
        assert lt.main_range.max_value == 35
        assert lt.main_range.count == 5

    def test_get_lottery_type_bonus_range(self) -> None:
        lt = self.plugin.get_lottery_type()
        assert lt.bonus_range is not None
        assert lt.bonus_range.max_value == 12

    def test_get_data_source(self) -> None:
        ds = self.plugin.get_data_source()
        from plugins.dlt.data_source import DltDataSource
        assert isinstance(ds, DltDataSource)

    def test_get_builtin_strategies_returns_list(self) -> None:
        strategies = self.plugin.get_builtin_strategies()
        assert len(strategies) >= 1
        assert strategies[0]["strategy_id"] == "dlt_cold_tracker"

    def test_builtin_strategies_have_rules(self) -> None:
        strategies = self.plugin.get_builtin_strategies()
        assert len(strategies[0]["rules"]) > 0
