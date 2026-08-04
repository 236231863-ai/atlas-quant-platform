"""premium.feature_test - Premium Feature Test（v4.6 P6 商业化验证）。

不开发支付，只验证付费意愿：
  - 高级功能列表：自动兑奖提醒 / 年度彩票报告 / 无限历史保存 / 家庭彩票管理
  - 免费用户看到「升级 Atlas Premium 解锁」
  - 记录 premium_view / premium_click
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

PREMIUM_FEATURES = (
    "自动兑奖提醒",
    "年度彩票报告",
    "无限历史保存",
    "家庭彩票管理",
)

UNLOCK_TEXT = "升级 Atlas Premium 解锁"


@dataclass
class FeatureStatus:
    """一个高级功能的状态。"""

    name: str
    locked: bool = True
    unlock_text: str = UNLOCK_TEXT

    def __post_init__(self):
        if not self.locked:
            self.unlock_text = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "locked": self.locked,
                "unlock_text": self.unlock_text}


class PremiumFeatureTest:
    """商业化验证：功能状态 + 埋点。"""

    @classmethod
    def features(cls, is_premium: bool = False) -> List[FeatureStatus]:
        """所有高级功能状态。"""
        return [FeatureStatus(name=f, locked=not is_premium) for f in PREMIUM_FEATURES]

    @classmethod
    def feature_status(cls, feature: str, is_premium: bool = False) -> FeatureStatus:
        return FeatureStatus(name=feature, locked=not is_premium)

    @classmethod
    def view(cls, feature: str, source: str = "desktop") -> None:
        """记录 premium_view 事件。"""
        from engine.user_analytics import AnalyticsTracker
        AnalyticsTracker().record("premium_view", source=source,
                                  metadata={"feature": feature})

    @classmethod
    def click(cls, feature: str, source: str = "desktop") -> None:
        """记录 premium_click 事件。"""
        from engine.user_analytics import AnalyticsTracker
        AnalyticsTracker().record("premium_click", source=source,
                                  metadata={"feature": feature})

    @classmethod
    def locked_text(cls, is_premium: bool = False) -> str:
        """免费用户可见的解锁提示。"""
        if is_premium:
            return ""
        return f"🔒 {UNLOCK_TEXT}（自动兑奖提醒 · 年度报告 · 无限历史 · 家庭管理）"


def premium_features(is_premium: bool = False) -> List[FeatureStatus]:
    """便捷函数。"""
    return PremiumFeatureTest.features(is_premium)
