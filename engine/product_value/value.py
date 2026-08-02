"""product_value - 功能价值分析。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FeatureValue:
    """单个功能价值。"""

    feature: str
    usage: int = 0           # 使用次数
    duration_min: float = 0.0  # 平均使用时长（分钟）
    satisfaction: float = 0.0  # 满意度 0-5
    conversion: float = 0.0    # 付费转化贡献 0-1
    value: float = 0.0         # 综合价值 0-100

    def to_dict(self) -> dict:
        return {
            "feature": self.feature, "usage": self.usage,
            "duration_min": round(self.duration_min, 1),
            "satisfaction": self.satisfaction, "conversion": self.conversion,
            "value": round(self.value, 1),
        }


class FeatureValueEngine:
    """功能价值引擎。"""

    @staticmethod
    def score(
        feature: str, usage: int = 0, duration_min: float = 0.0,
        satisfaction: float = 0.0, conversion: float = 0.0,
    ) -> FeatureValue:
        """计算单功能综合价值（0-100）。

        权重：usage 40% / duration 20% / satisfaction 20% / conversion 20%。
        """
        u = min(100, usage * 5) * 0.4
        d = min(100, duration_min * 2) * 0.2
        s = min(5, max(0, satisfaction)) / 5 * 100 * 0.2
        c = min(1, max(0, conversion)) * 100 * 0.2
        return FeatureValue(
            feature=feature, usage=usage, duration_min=duration_min,
            satisfaction=satisfaction, conversion=conversion, value=u + d + s + c,
        )

    @staticmethod
    def rank(items: List[FeatureValue]) -> List[FeatureValue]:
        return sorted(items, key=lambda x: x.value, reverse=True)


def analyze_features(features: List[dict]) -> List[FeatureValue]:
    """批量分析功能价值。features: [{feature, usage, duration_min, satisfaction, conversion}]"""
    return [FeatureValueEngine.score(**f) for f in features]
