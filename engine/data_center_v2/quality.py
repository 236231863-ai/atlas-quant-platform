"""data_center_v2 - 数据质量报告。

DataQualityReport：量化数据质量，输出
  数据数量 / 时间范围 / 完整率 / 可信等级（A/B/C/D）。
供 UI 展示「数据不足警告」依据。
"""
from __future__ import annotations

import dataclasses
from typing import List

from .models import DrawRecord

# 可信度阈值（期数）
TRUST_THRESHOLDS = {
    "A": 500,   # >=500 期：可信
    "B": 200,   # >=200 期：基本可用
    "C": 50,    # >=50 期：不足
    "D": 0,     # <50 期：严重不足
}


@dataclasses.dataclass
class DataQualityReport:
    """数据质量报告。"""

    lottery: str
    total: int = 0
    date_from: str = ""
    date_to: str = ""
    completeness: float = 0.0   # 完整率 0-1（奖池缺失率等）
    pool_missing: int = 0
    format_errors: int = 0
    source_type: str = "unknown"
    source_path: str = ""

    # ---- 派生 ----
    @property
    def trust_level(self) -> str:
        """可信等级 A/B/C/D。"""
        for level, threshold in sorted(
            TRUST_THRESHOLDS.items(), key=lambda kv: -kv[1]
        ):
            if self.total >= threshold:
                return level
        return "D"

    @property
    def trust_label(self) -> str:
        labels = {"A": "可信", "B": "基本可用", "C": "数据不足", "D": "严重不足"}
        return labels.get(self.trust_level, "未知")

    @property
    def is_sufficient(self) -> bool:
        """是否达到最低标准（>=500期）。"""
        return self.total >= 500

    def warning_message(self) -> str:
        """UI 数据不足警告文案。"""
        if self.is_sufficient:
            return f"数据充足：{self.total} 期（{self.date_from} ~ {self.date_to}）· 可信等级 {self.trust_level}"
        return (
            f"⚠️ 数据不足：仅 {self.total} 期（低于最低标准 500 期），"
            f"统计结论可能不稳健 · 可信等级 {self.trust_level}"
        )

    @classmethod
    def build(
        cls,
        lottery: str,
        draws: List[DrawRecord],
        source_type: str = "unknown",
        source_path: str = "",
    ) -> "DataQualityReport":
        """从数据构建质量报告。"""
        total = len(draws)
        dates = [d.draw_date for d in draws if d.draw_date]
        pool_missing = sum(1 for d in draws if d.pool <= 0 and d.number)
        completeness = 1.0
        if total:
            completeness = 1.0 - pool_missing / total
        return cls(
            lottery=lottery,
            total=total,
            date_from=min(dates) if dates else "",
            date_to=max(dates) if dates else "",
            completeness=round(completeness, 4),
            pool_missing=pool_missing,
            format_errors=0,
            source_type=source_type,
            source_path=source_path,
        )

    def summary_dict(self) -> dict:
        return {
            "lottery": self.lottery,
            "total": self.total,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "completeness": self.completeness,
            "pool_missing": self.pool_missing,
            "trust_level": self.trust_level,
            "trust_label": self.trust_label,
            "sufficient": self.is_sufficient,
            "source_type": self.source_type,
            "source_path": self.source_path,
        }
