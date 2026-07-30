"""Atlas Quant Platform - DLT Plugin.

大乐透 (Da Le Tou) plugin for the Atlas Quant Platform.
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.plugin_system import PluginManifest
from core.types import PluginState, LotteryTypeDef, NumberRange
from plugins.base import BasePlugin
from plugins.dlt.data_source import DltDataSource, DLT_GAME_DEF


DLT_MANIFEST = PluginManifest(
    id="dlt",
    name="大乐透",
    version="1.0.0",
    author="Atlas Quant Team",
    description="中国体育彩票大乐透 (DLT) 插件",
    entry="plugins.dlt:DltPlugin",
)


class DltPlugin(BasePlugin):
    """大乐透插件实现。"""

    def __init__(self) -> None:
        super().__init__(DLT_MANIFEST)
        self._data_source = DltDataSource()

    def get_lottery_type(self) -> LotteryTypeDef:
        return LotteryTypeDef(
            code="dlt",
            name="大乐透",
            region="CN",
            main_range=NumberRange(min_value=1, max_value=35, count=5),
            bonus_range=NumberRange(min_value=1, max_value=12, count=2),
        )

    def get_data_source(self) -> DltDataSource:
        return self._data_source

    def get_builtin_strategies(self) -> List[Dict[str, Any]]:
        return [
            {
                "strategy_id": "dlt_cold_tracker",
                "name": "大乐透冷号追踪",
                "version": 1,
                "rules": [
                    {"type": "filter", "target": "main_numbers", "condition": "min_gap", "params": {"value": 8}},
                ],
                "combinator": "AND",
                "metadata": {"author": "system", "description": "追踪遗漏超过8期的冷号"},
            },
        ]

    def register(self) -> None:
        super().register()
        self._state = PluginState.ACTIVE
