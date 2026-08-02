"""
Atlas Quant Desktop - 本地数据层

支持多彩种开奖数据加载：
1. 优先加载「用户数据目录」中的真实数据（用户导入）
2. 其次加载项目 data/raw/ 下的数据文件
3. 回退到打包进 exe 的内置演示数据

数据来源优先级保证用户真实数据始终可用。
"""
import csv
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# 彩种定义：文件名前缀 -> (前区范围, 后区范围)
LOTTERY_SPECS = {
    "dlt": {"name": "大乐透", "front": (1, 35), "back": (1, 12), "front_n": 5, "back_n": 2},
    "ssq": {"name": "双色球", "front": (1, 33), "back": (1, 16), "front_n": 6, "back_n": 1},
}


@dataclass
class DrawRecord:
    """一期开奖记录。"""

    number: str        # 期号，如 24001
    draw_date: str     # 开奖日期
    front: List[int]   # 前区号码
    back: List[int]    # 后区号码
    pool: float        # 奖池金额
    lottery: str = "dlt"  # 彩种

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


@dataclass
class DataSourceInfo:
    """数据来源信息。"""

    lottery: str
    path: str
    source_type: str  # user / project / bundled
    draw_count: int
    note: str = ""


def _resource_path(rel: str) -> Optional[str]:
    """定位打包目录/源码目录中的资源文件。"""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        p = os.path.join(base, rel)
        if os.path.exists(p):
            return p
    for root in [
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.getcwd(),
    ]:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            return p
    return None


def _user_data_dir() -> str:
    """用户数据目录：优先桌面/AtlasData，其次项目 data/raw。"""
    project_raw = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    return project_raw


def _find_data_file(lottery: str) -> tuple:
    """按优先级查找数据文件，返回 (path, source_type)。

    优先级：用户导入文件 > 项目文件 > 打包内置文件。
    """
    prefix = f"{lottery}_"
    # 1. 项目 data/raw 下的用户文件（非 _sample 后缀）
    project_raw = _user_data_dir()
    if os.path.isdir(project_raw):
        for fn in sorted(os.listdir(project_raw)):
            if fn.startswith(prefix) and fn.endswith(".csv") and "_sample" not in fn:
                p = os.path.join(project_raw, fn)
                return p, "user"
    # 2. 内置样例/演示文件
    bundled_rel = os.path.join("data", "raw", f"{lottery}_2024_sample.csv")
    p = _resource_path(bundled_rel)
    if p:
        return p, "bundled"
    return None, "none"


def _parse_csv(path: str, lottery: str) -> List[DrawRecord]:
    """解析彩种 CSV。支持列名 front_1..N / back_1..M 或 main_1..N / bonus_1..M。"""
    spec = LOTTERY_SPECS.get(lottery, LOTTERY_SPECS["dlt"])
    front_n, back_n = spec["front_n"], spec["back_n"]
    draws: List[DrawRecord] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                if f"front_1" in row:
                    front = [int(row[f"front_{i}"]) for i in range(1, front_n + 1)]
                    back = [int(row[f"back_{i}"]) for i in range(1, back_n + 1)]
                elif f"main_1" in row:
                    front = [int(row[f"main_{i}"]) for i in range(1, front_n + 1)]
                    back = [int(row[f"bonus_{i}"]) for i in range(1, back_n + 1)]
                else:
                    continue
                draws.append(
                    DrawRecord(
                        number=str(row.get("draw_number", "")).strip(),
                        draw_date=str(row.get("draw_date", "")).strip(),
                        front=front,
                        back=back,
                        pool=float(row.get("pool_amount") or 0),
                        lottery=lottery,
                    )
                )
            except (ValueError, KeyError, IndexError):
                continue
    draws.sort(key=lambda d: d.number)
    return draws


def load_draws(lottery: str = "dlt") -> List[DrawRecord]:
    """加载指定彩种的开奖记录（用户数据优先）。"""
    path, _stype = _find_data_file(lottery)
    if not path:
        return []
    return _parse_csv(path, lottery)


def get_data_source(lottery: str = "dlt") -> DataSourceInfo:
    """返回当前数据来源信息。"""
    path, stype = _find_data_file(lottery)
    draws = load_draws(lottery)
    note = ""
    if stype == "user":
        note = "用户导入数据"
    elif stype == "bundled":
        note = "内置演示数据（可在 data/raw/ 放入真实数据替换）"
    else:
        note = "暂无数据"
    return DataSourceInfo(
        lottery=lottery,
        path=path or "",
        source_type=stype,
        draw_count=len(draws),
        note=note,
    )
