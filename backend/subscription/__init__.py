"""subscription - 商业版本基础（v3.7.0 Phase 5）。

Edition：Community / Professional / Research 三版本 + 功能权限矩阵。
FeatureFlag：功能开关检查 + 升级提示。
"""
from .editions import (
    Edition, COMMUNITY, PROFESSIONAL, RESEARCH, EDITIONS,
    get_edition, edition_features, FEATURES,
)
from .feature_flags import FeatureFlag, can_use, gate

__all__ = [
    "Edition", "COMMUNITY", "PROFESSIONAL", "RESEARCH", "EDITIONS",
    "get_edition", "edition_features", "FEATURES",
    "FeatureFlag", "can_use", "gate",
]
