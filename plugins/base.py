"""Atlas Quant Platform - Plugin Base."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.types import LotteryTypeDef, NumberRange, PluginState
from core.plugin_system import PluginManifest, PluginABC


class BasePlugin(PluginABC):
    """插件基类 - 简化插件实现"""

    manifest: PluginManifest
    _state: PluginState = PluginState.REGISTERED

    def __init__(self, manifest: PluginManifest) -> None:
        self.manifest = manifest

    def register(self) -> None:
        self._state = PluginState.LOADED

    @property
    def state(self) -> PluginState:
        return self._state

    def get_builtin_strategies(self) -> List[Dict[str, Any]]:
        return []
