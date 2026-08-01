"""
Atlas Quant Desktop - 本地数据层

从打包进 exe 的 CSV 读取开奖数据，独立于后端服务运行。
打包后通过 sys._MEIPASS 定位资源；源码运行则从项目 data/ 读取。
"""
import csv
import os
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DrawRecord:
    """一期开奖记录（大乐透：前区 5 码 + 后区 2 码）。"""

    number: str        # 期号，如 24001
    draw_date: str     # 开奖日期
    front: List[int]   # 前区 5 个号码
    back: List[int]    # 后区 2 个号码
    pool: float        # 奖池金额

    @property
    def all_numbers(self) -> List[int]:
        return self.front + self.back

    @property
    def front_sum(self) -> int:
        return sum(self.front)

    @property
    def front_span(self) -> int:
        return max(self.front) - min(self.front)

    def format_front(self) -> str:
        return " ".join(f"{n:02d}" for n in self.front)

    def format_back(self) -> str:
        return " ".join(f"{n:02d}" for n in self.back)

    def format_pool(self) -> str:
        return f"{self.pool / 1e8:.1f} 亿" if self.pool >= 1e8 else f"{self.pool:,.0f}"


def _resource_path(rel: str) -> Optional[str]:
    """定位资源文件：优先打包目录(sys._MEIPASS)，其次源码目录。"""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return p
    candidates = [
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # 项目根(desktop/..)
        os.getcwd(),
    ]
    for root in candidates:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            return p
    return None


_CSV_REL = os.path.join("data", "raw", "dlt_2024_sample.csv")


def load_draws() -> List[DrawRecord]:
    """从 CSV 加载大乐透开奖记录，按期号升序。"""
    path = _resource_path(_CSV_REL)
    draws: List[DrawRecord] = []
    if not path:
        return draws
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                front = [int(row[f"front_{i}"]) for i in range(1, 6)]
                back = [int(row[f"back_{i}"]) for i in range(1, 3)]
                draws.append(
                    DrawRecord(
                        number=row["draw_number"].strip(),
                        draw_date=row["draw_date"].strip(),
                        front=front,
                        back=back,
                        pool=float(row.get("pool_amount") or 0),
                    )
                )
            except (ValueError, KeyError):
                continue
    draws.sort(key=lambda d: d.number)
    return draws
