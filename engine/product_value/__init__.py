"""product_value - 功能价值引擎（v3.8.0 Phase 3）。

按 usage / duration / satisfaction / conversion 四维分析功能价值。
"""
from .value import FeatureValueEngine, FeatureValue, analyze_features

__all__ = ["FeatureValueEngine", "FeatureValue", "analyze_features"]
