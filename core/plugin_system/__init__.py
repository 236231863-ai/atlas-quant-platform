"""
Atlas Quant Platform - Plugin System.

插件系统负责插件的注册、发现、加载和生命周期管理。

每个插件:
- 包含plugin.json元数据
- 实现PluginABC接口
- 注册后自动被系统发现
- 提供领域特定数据 (号码规则、数据源)
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from core.types import LotteryTypeDef, PluginState


@dataclass
class PluginManifest:
    """插件清单 (从plugin.json解析)"""
    id: str
    name: str
    version: str
    author: str = ""
    description: str = ""
    entry: str = ""
    dependencies: List[str] = field(default_factory=list)
    engine_version: str = ">=0.1.0"

    @classmethod
    def from_json(cls, path: Path) -> PluginManifest:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


class PluginABC(ABC):
    """插件抽象基类 - 所有插件必须实现"""

    manifest: PluginManifest

    @abstractmethod
    def register(self) -> None:
        """注册到系统"""
        ...

    @abstractmethod
    def get_lottery_type(self) -> LotteryTypeDef:
        """返回彩种定义"""
        ...

    @abstractmethod
    def get_builtin_strategies(self) -> List[Dict[str, Any]]:
        """返回内置策略模板列表"""
        ...

    @property
    @abstractmethod
    def state(self) -> PluginState:
        """当前插件状态"""
        ...


class PluginRegistry:
    """插件注册表 - 管理所有已注册插件"""

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginABC] = {}
        self._plugin_dir: Path = Path("plugins")

    def register(self, plugin: PluginABC) -> None:
        pid = plugin.manifest.id
        if pid in self._plugins:
            raise ValueError(f"Plugin '{pid}' is already registered")
        plugin.register()
        self._plugins[pid] = plugin

    def discover(self) -> List[PluginABC]:
        """从plugins/目录发现并加载插件"""
        discovered: List[PluginABC] = []
        for plugin_path in self._plugin_dir.iterdir():
            manifest_path = plugin_path / "plugin.json"
            if manifest_path.exists():
                manifest = PluginManifest.from_json(manifest_path)
                # TODO: 动态加载插件
                discovered.append(self._load_plugin(manifest))
        return discovered

    def _load_plugin(self, manifest: PluginManifest) -> PluginABC:
        """根据清单动态加载插件实例"""
        # 后续实现: 动态导入 entry 指向的类
        raise NotImplementedError("Dynamic loading coming in Sprint 2")

    def get(self, plugin_id: str) -> Optional[PluginABC]:
        return self._plugins.get(plugin_id)

    def list(self) -> List[PluginABC]:
        return list(self._plugins.values())

    def unregister(self, plugin_id: str) -> None:
        self._plugins.pop(plugin_id, None)
