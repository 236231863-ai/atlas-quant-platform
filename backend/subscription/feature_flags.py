"""subscription - 功能开关（Feature Flag）。

基于用户当前版本检查功能可用性；未授权功能返回友好提示。
"""
from __future__ import annotations

from typing import Optional

from .editions import Edition, EDITIONS, get_edition


class FeatureFlag:
    """功能开关检查器。"""

    @staticmethod
    def current_edition(edition_id: Optional[str]) -> Edition:
        """解析用户版本；未知/缺失回退 Community。"""
        return get_edition(edition_id) or EDITIONS["community"]

    @staticmethod
    def can(edition_id: Optional[str], feature: str) -> bool:
        """用户版本是否可用某功能。"""
        return FeatureFlag.current_edition(edition_id).has(feature)

    @staticmethod
    def gate_message(edition_id: Optional[str], feature: str) -> Optional[str]:
        """若不可用返回升级提示，否则 None。"""
        ed = FeatureFlag.current_edition(edition_id)
        if ed.has(feature):
            return None
        return (
            f"「{feature}」为 {feature_upgrade_hint(feature)} 功能，"
            f"当前 {ed.name} 版不可用。升级 Professional/Research 后可用。"
        )

    @staticmethod
    def available_features(edition_id: Optional[str]) -> list:
        return list(FeatureFlag.current_edition(edition_id).features)


def feature_upgrade_hint(feature: str) -> str:
    """功能归属提示。"""
    from .editions import FEATURES
    return FEATURES.get(feature, feature)


def can_use(edition_id: Optional[str], feature: str) -> bool:
    """便捷函数。"""
    return FeatureFlag.can(edition_id, feature)


def gate(edition_id: Optional[str], feature: str) -> Optional[str]:
    """便捷函数。"""
    return FeatureFlag.gate_message(edition_id, feature)
