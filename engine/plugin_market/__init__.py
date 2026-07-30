"""Plugin Marketplace - third-party extension system."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class PluginManifest: plugin_id:str; name:str; version:str="1.0"; author:str=""; plugin_type:str="analysis"; permissions:List[str]=field(default_factory=list); entry_point:str=""; status:str="inactive"; def to_dict(self):return asdict(self)

class PluginRegistry:
    def __init__(self): self._plugins: Dict[str, PluginManifest] = {}
    def register(self, plugin: PluginManifest): self._plugins[plugin.plugin_id] = plugin
    def install(self, pid: str) -> bool:
        p = self._plugins.get(pid)
        if not p: return False
        p.status = "active"; return True
    def uninstall(self, pid: str) -> bool:
        p = self._plugins.get(pid)
        if not p: return False
        p.status = "inactive"; return True
    def validate_plugin(self, manifest: PluginManifest) -> List[str]:
        errors = []
        if not manifest.plugin_id: errors.append("plugin_id required")
        if not manifest.name: errors.append("name required")
        if manifest.plugin_type not in ["analysis","strategy","data","report"]: errors.append("Invalid type")
        return errors
    def list_plugins(self, plugin_type: Optional[str]=None) -> List[PluginManifest]:
        if plugin_type: return [p for p in self._plugins.values() if p.plugin_type == plugin_type]
        return list(self._plugins.values())
    def count(self) -> int: return len(self._plugins)
