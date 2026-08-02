"""Atlas 数据导入工具 - 导入用户真实开奖数据。

用法：
    python tools/import_data.py <csv文件> --lottery dlt
    python tools/import_data.py <csv文件> --lottery ssq

CSV 格式（列名）：
    draw_number,draw_date,front_1,...,front_N,back_1,...,back_M,pool_amount
    或
    draw_number,draw_date,main_1,...,main_N,bonus_1,...,bonus_M,pool_amount
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys


def _validate(path: str, lottery: str) -> tuple:
    """校验 CSV 格式，返回 (是否有效, 期数, 错误信息)。"""
    specs = {
        "dlt": (5, 2),
        "ssq": (6, 1),
    }
    if lottery not in specs:
        return False, 0, f"不支持的彩种: {lottery}（支持 dlt/ssq）"
    front_n, back_n = specs[lottery]
    count = 0
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return False, 0, "空文件或缺少表头"
        for row in reader:
            try:
                if "front_1" in row:
                    front = [int(row[f"front_{i}"]) for i in range(1, front_n + 1)]
                    back = [int(row[f"back_{i}"]) for i in range(1, back_n + 1)]
                elif "main_1" in row:
                    front = [int(row[f"main_{i}"]) for i in range(1, front_n + 1)]
                    back = [int(row[f"bonus_{i}"]) for i in range(1, back_n + 1)]
                else:
                    return False, count, "缺少 front_1 或 main_1 列"
                if not all(1 <= n for n in front) or not all(1 <= n for n in back):
                    return False, count, "号码需为正整数"
                count += 1
            except (ValueError, KeyError):
                return False, count, f"第 {count + 1} 行解析失败"
    return True, count, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Atlas 数据导入工具")
    parser.add_argument("csv", help="要导入的 CSV 文件路径")
    parser.add_argument("--lottery", default="dlt", choices=["dlt", "ssq"], help="彩种")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"错误: 文件不存在 {args.csv}")
        return 1

    ok, count, err = _validate(args.csv, args.lottery)
    if not ok:
        print(f"校验失败: {err}")
        return 1
    print(f"校验通过: {count} 期 {args.lottery} 数据")

    # 复制到数据目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"{args.lottery}_user_data.csv")
    shutil.copy2(args.csv, dest)
    print(f"已导入: {dest}")
    print("桌面端将自动优先加载此数据（数据来源显示为「用户导入数据」）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
