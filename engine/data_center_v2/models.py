"""data_center_v2 - 统一数据模型。

v3.6.1 数据真实性升级：统一 DrawRecord 数据模型，
与 desktop/data_loader.py 字段兼容，支撑多数据源（CSV/Excel/API/Database）。
"""
from __future__ import annotations

import dataclasses
from typing import List, Optional


@dataclasses.dataclass
class DrawRecord:
    """一期开奖记录（统一模型）。"""

    number: str        # 期号，如 26086
    draw_date: str     # 开奖日期 YYYY-MM-DD
    front: List[int]   # 前区号码
    back: List[int]    # 后区号码
    pool: float = 0.0  # 奖池金额
    lottery: str = "dlt"  # 彩种代码

    # ---- 派生属性（与 desktop.data_loader 兼容） ----
    @property
    def all_numbers(self) -> List[int]:
        return self.front + self.back

    @property
    def front_sum(self) -> int:
        return sum(self.front)

    @property
    def front_span(self) -> int:
        return max(self.front) - min(self.front) if self.front else 0

    def format_front(self) -> str:
        return " ".join(f"{n:02d}" for n in self.front)

    def format_back(self) -> str:
        return " ".join(f"{n:02d}" for n in self.back)

    def format_pool(self) -> str:
        if self.pool >= 1e8:
            return f"{self.pool / 1e8:.1f} 亿"
        return f"{self.pool:,.0f}"


@dataclasses.dataclass
class DataSourceInfo:
    """数据来源信息（供 UI 展示数据透明度）。"""

    source_type: str        # csv / excel / api / database
    source_path: str = ""   # 文件路径或 API 标识
    record_count: int = 0
    updated_at: str = ""
    is_builtin: bool = False  # 是否内置演示数据


# 彩种规格（数据驱动，支持新彩种零代码接入）
LOTTERY_SPECS = {
    "dlt": {"name": "大乐透", "front": (1, 35), "back": (1, 12), "front_n": 5, "back_n": 2},
    "ssq": {"name": "双色球", "front": (1, 33), "back": (1, 16), "front_n": 6, "back_n": 1},
}


def lottery_name(code: str) -> str:
    spec = LOTTERY_SPECS.get(code)
    return spec["name"] if spec else code
