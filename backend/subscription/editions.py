"""subscription - 产品版本（Edition）定义。

v3.7.0 商业基础：定义三个版本与功能权限矩阵（feature flag）。
Community 免费，Professional 付费，Research 高阶。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# 功能标识（feature keys）
FEATURES = {
    "dashboard": "数据看板",
    "analysis_basic": "基础分析（频率/和值）",
    "analysis_advanced": "高级分析（跨度/奇偶）",
    "backtest_basic": "基础回测",
    "backtest_advanced": "深度回测（样本外/随机基准）",
    "export_basic": "基础导出（MD/CSV）",
    "export_advanced": "高级导出（PDF/PNG）",
    "daily_intelligence": "每日智能",
    "data_full": "双彩种全量数据",
    "ai_online": "在线 AI 助手",
    "priority_support": "优先支持",
}


@dataclass
class Edition:
    """产品版本定义。"""

    id: str
    name: str
    description: str
    features: List[str]
    price_label: str = "免费"

    def has(self, feature: str) -> bool:
        return feature in self.features

    def missing(self, feature: str) -> bool:
        return not self.has(feature)


# 三个版本
COMMUNITY = Edition(
    id="community",
    name="Community",
    description="免费版：基础分析与基础导出",
    features=[
        "dashboard", "analysis_basic", "backtest_basic",
        "export_basic", "data_full",
    ],
    price_label="免费",
)

PROFESSIONAL = Edition(
    id="professional",
    name="Professional",
    description="付费版：全功能，适合高频用户",
    features=[
        "dashboard", "analysis_basic", "analysis_advanced",
        "backtest_basic", "backtest_advanced",
        "export_basic", "export_advanced",
        "daily_intelligence", "data_full",
    ],
    price_label="¥/月",
)

RESEARCH = Edition(
    id="research",
    name="Research",
    description="高阶版：深度研究 + 优先支持",
    features=[
        "dashboard", "analysis_basic", "analysis_advanced",
        "backtest_basic", "backtest_advanced",
        "export_basic", "export_advanced",
        "daily_intelligence", "data_full", "ai_online", "priority_support",
    ],
    price_label="¥/月",
)

EDITIONS: Dict[str, Edition] = {
    e.id: e for e in (COMMUNITY, PROFESSIONAL, RESEARCH)
}


def get_edition(edition_id: str) -> Optional[Edition]:
    return EDITIONS.get(edition_id)


def edition_features(edition_id: str) -> List[str]:
    e = EDITIONS.get(edition_id)
    return list(e.features) if e else []
