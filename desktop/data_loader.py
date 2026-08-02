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

    优先级：用户导入文件 > 项目真实历史数据(history) > 内置样例。
    """
    prefix = f"{lottery}_"
    # 1. 项目 data/raw 下的用户导入文件（非 _sample 后缀，history 优先）
    project_raw = _user_data_dir()
    if os.path.isdir(project_raw):
        for fn in sorted(os.listdir(project_raw)):
            if (
                fn.startswith(prefix) and fn.endswith(".csv")
                and "_sample" not in fn
            ):
                p = os.path.join(project_raw, fn)
                # 真实历史数据（history 或非样例）优先
                if "history" in fn:
                    return p, "user"
        # 2. 无 history 时，任何非样例 CSV 视为用户数据
        for fn in sorted(os.listdir(project_raw)):
            if (
                fn.startswith(prefix) and fn.endswith(".csv")
                and "_sample" not in fn
            ):
                p = os.path.join(project_raw, fn)
                return p, "user"
    # 3. 内置真实历史数据（打包进 exe）
    history_rel = os.path.join("data", "raw", f"{lottery}_history.csv")
    p = _resource_path(history_rel)
    if p:
        return p, "bundled_history"
    # 4. 内置样例/演示文件
    bundled_rel = os.path.join("data", "raw", f"{lottery}_2024_sample.csv")
    p = _resource_path(bundled_rel)
    if p:
        return p, "bundled"
    return None, "none"


def _parse_csv(path: str, lottery: str) -> List[DrawRecord]:
    """解析彩种 CSV。

    支持三种格式：
      1. front_1..N / back_1..M      （列式样例）
      2. main_1..N / bonus_1..M      （列式样例变体）
      3. numbers 列（如 "10 11 18 22 35|06 12" 或 "10 11 18 22 35 06 12"）
    """
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
                    num = str(row.get("draw_number", "")).strip()
                    date = str(row.get("draw_date", "")).strip()
                    pool = float(row.get("pool_amount") or 0)
                elif f"main_1" in row:
                    front = [int(row[f"main_{i}"]) for i in range(1, front_n + 1)]
                    back = [int(row[f"bonus_{i}"]) for i in range(1, back_n + 1)]
                    num = str(row.get("draw_number", "")).strip()
                    date = str(row.get("draw_date", "")).strip()
                    pool = float(row.get("pool_amount") or 0)
                else:
                    # 统一格式：issue,date,numbers,pool
                    num = str(row.get("issue", "") or row.get("number", "")).strip()
                    date = str(row.get("date", "") or row.get("draw_date", "")).strip()
                    numbers = (row.get("numbers", "") or row.get("result", "")).replace(",", " ")
                    if not num or not numbers:
                        continue
                    if "|" in numbers:
                        f_part, b_part = numbers.split("|", 1)
                        front = [int(x) for x in f_part.split()]
                        back = [int(x) for x in b_part.split()]
                    else:
                        parts = [int(x) for x in numbers.split()]
                        front = parts[:front_n]
                        back = parts[front_n : front_n + back_n]
                    try:
                        pool = float(str(row.get("pool", "")).replace(",", "") or 0)
                    except ValueError:
                        pool = 0.0
                draws.append(
                    DrawRecord(
                        number=num,
                        draw_date=date,
                        front=front,
                        back=back,
                        pool=pool,
                        lottery=lottery,
                    )
                )
            except (ValueError, KeyError, IndexError, TypeError):
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
    elif stype == "bundled_history":
        note = "内置真实历史数据"
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


def _trust_level(total: int) -> str:
    """可信等级：A(>=500) B(>=200) C(>=50) D(<50)。"""
    if total >= 500:
        return "A"
    if total >= 200:
        return "B"
    if total >= 50:
        return "C"
    return "D"


def get_data_quality(lottery: str = "dlt") -> dict:
    """数据质量报告（数量/时间范围/可信等级/是否达标/UI 文案）。

    供 Dashboard 等页面展示「数据不足警告」。
    """
    draws = load_draws(lottery)
    total = len(draws)
    dates = [d.draw_date for d in draws if d.draw_date]
    date_from = min(dates) if dates else ""
    date_to = max(dates) if dates else ""
    level = _trust_level(total)
    labels = {"A": "可信", "B": "基本可用", "C": "数据不足", "D": "严重不足"}
    sufficient = total >= 500
    if sufficient:
        message = f"数据充足：{total} 期（{date_from} ~ {date_to}）· 可信等级 {level}"
    else:
        message = (
            f"⚠️ 数据不足：仅 {total} 期（最低标准 500 期），统计结论可能不稳健 · 可信等级 {level}"
        )
    return {
        "lottery": lottery,
        "total": total,
        "date_from": date_from,
        "date_to": date_to,
        "trust_level": level,
        "trust_label": labels.get(level, "未知"),
        "sufficient": sufficient,
        "message": message,
    }
