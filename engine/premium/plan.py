"""premium - Atlas Premium 会员体系（v4.2 Phase 5 会员价值验证）。

不要销售预测。付费价值围绕「数据服务」：
  免费：基础兑奖
  会员：自动提醒 / 无限历史 / 年度报告 / 高级复盘

红线：任何套餐都不含预测、选号、提高中奖概率类功能。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

PLAN_FREE = "free"
PLAN_PREMIUM = "premium"

TIER_NAMES = {PLAN_FREE: "免费版", PLAN_PREMIUM: "Atlas Premium"}


@dataclass
class PremiumFeature:
    """一个会员功能点。"""

    key: str
    name: str
    tier: str               # free / premium
    description: str

    def to_dict(self) -> dict:
        return {"key": self.key, "name": self.name, "tier": self.tier,
                "description": self.description}


FEATURES = [
    # 免费层
    PremiumFeature("basic_claim", "基础兑奖", PLAN_FREE, "手动输入号码核对开奖结果"),
    PremiumFeature("ticket_save", "票据保存", PLAN_FREE, "保存彩票记录（免费 100 张）"),
    PremiumFeature("budget_center", "预算中心", PLAN_FREE, "周/月/年预算设置与预警"),
    PremiumFeature("health_index", "健康指数", PLAN_FREE, "购彩健康指数 A/B/C"),
    # 会员层
    PremiumFeature("auto_remind", "自动提醒", PLAN_PREMIUM, "开奖桌面通知 + 待兑奖提醒"),
    PremiumFeature("unlimited_history", "无限历史", PLAN_PREMIUM, "票据无限保存，历史完整沉淀"),
    PremiumFeature("annual_report", "年度报告", PLAN_PREMIUM, "PDF 年度彩票总结报告"),
    PremiumFeature("advanced_review", "高级复盘", PLAN_PREMIUM, "自动复盘 + 多期对比分析"),
]

FEATURE_BY_KEY = {f.key: f for f in FEATURES}


class PremiumPlan:
    """套餐定义。"""

    @classmethod
    def get_feature(cls, key: str) -> Optional[PremiumFeature]:
        return FEATURE_BY_KEY.get(key)

    @classmethod
    def all_features(cls) -> List[PremiumFeature]:
        return list(FEATURES)

    @classmethod
    def features_for(cls, tier: str) -> List[PremiumFeature]:
        """某套餐包含的功能。"""
        return [f for f in FEATURES if f.tier == tier]

    @classmethod
    def entitlements(cls, tier: str) -> List[str]:
        """该套餐可用的功能 key 列表（会员含免费功能）。"""
        keys = [f.key for f in FEATURES if f.tier == PLAN_FREE]
        if tier == PLAN_PREMIUM:
            keys += [f.key for f in FEATURES if f.tier == PLAN_PREMIUM]
        return keys

    @classmethod
    def is_entitled(cls, tier: str, feature_key: str) -> bool:
        return feature_key in cls.entitlements(tier)

    @classmethod
    def tier_name(cls, tier: str) -> str:
        return TIER_NAMES.get(tier, tier)

    @classmethod
    def pricing_hint(cls) -> dict:
        """定价建议（验证用，非最终价格）。"""
        return {
            "free": 0,
            "premium": 9.9,  # 元/月（建议值，需真实验证）
            "currency": "CNY",
            "billing": "monthly",
            "policy": "会员仅解锁数据服务，不包含任何预测功能",
        }


class PremiumManager:
    """会员状态管理（本地 JSON 快照，便于验证）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "premium_v42.json")
        self._tier = PLAN_FREE
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    d = json.load(f)
                self._tier = d.get("tier", PLAN_FREE)
            except (json.JSONDecodeError, OSError, TypeError):
                self._tier = PLAN_FREE

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"tier": self._tier}, f, ensure_ascii=False, indent=2)

    def set_tier(self, tier: str) -> str:
        self._tier = tier if tier in (PLAN_FREE, PLAN_PREMIUM) else PLAN_FREE
        self._save()
        return self._tier

    def get_tier(self) -> str:
        return self._tier

    def is_premium(self) -> bool:
        return self._tier == PLAN_PREMIUM

    def is_allowed(self, feature_key: str) -> bool:
        """功能门控：该功能是否对当前用户开放。"""
        return PremiumPlan.is_entitled(self._tier, feature_key)


def feature_matrix() -> List[dict]:
    """功能权限矩阵（免费/会员对照）。"""
    rows = []
    for f in FEATURES:
        rows.append({
            "feature": f.name,
            "key": f.key,
            "free": f.tier == PLAN_FREE,
            "premium": True,
            "description": f.description,
        })
    return rows
