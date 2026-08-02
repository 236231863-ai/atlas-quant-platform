"""export - CSV 导出。"""
from __future__ import annotations

import csv
import os
from typing import List


class CSVExporter:
    """将表格数据导出为 CSV。"""

    @staticmethod
    def export(headers: List[str], rows: List[list], path: str) -> str:
        """写入 .csv 文件，返回最终路径。"""
        if not path.lower().endswith(".csv"):
            path += ".csv"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(rows)
        return path

    @staticmethod
    def export_records(records: list, path: str) -> str:
        """导出回测逐期明细（records 为 BacktestRecord 列表）。

        列：期号 / 推荐前区 / 实际前区 / 前区命中 / 后区命中 / 中奖 / 奖金 / 累计收益
        """
        headers = ["期号", "推荐前区", "实际前区", "前区命中", "后区命中", "中奖", "奖金", "累计收益"]
        rows = [
            [
                r.issue,
                r.recommended,
                r.actual,
                r.front_hit,
                r.back_hit,
                r.prize_name or "",
                r.amount,
                round(r.equity, 2),
            ]
            for r in records
        ]
        return CSVExporter.export(headers, rows, path)
