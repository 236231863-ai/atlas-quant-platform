"""data_center.validation - 开奖数据校验（v4.5 P1）。

每次开奖更新必须检查：
  - 期号递增
  - 日期合法
  - 前区数量
  - 后区数量
  - 号码范围

失败：禁止覆盖旧数据。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

# 彩种规则
RULES = {
    "dlt": {"front_n": 5, "back_n": 2, "front_max": 35, "back_max": 12},
    "ssq": {"front_n": 6, "back_n": 1, "front_max": 33, "back_max": 16},
}


@dataclass
class ValidationResult:
    """一次校验结果。"""

    valid: bool = True
    issues: List[str] = field(default_factory=list)
    new_issue: str = ""
    last_issue: str = ""

    def add_issue(self, msg: str) -> None:
        self.valid = False
        self.issues.append(msg)


class DrawValidator:
    """开奖数据校验器。"""

    @classmethod
    def validate(cls, new_records: List, lottery: str = "dlt",
                 last_issue: str = "") -> ValidationResult:
        """校验一批新开奖记录（通常 1-30 期）。

        new_records: 按从新到旧或从旧到新均可，自动排序后校验递增。
        任一校验失败 → valid=False。
        """
        rule = RULES.get(lottery, RULES["dlt"])
        res = ValidationResult(last_issue=last_issue)
        if not new_records:
            res.add_issue("无数据")
            return res

        # 按期号排序（从旧到新）
        records = sorted(new_records, key=lambda r: int(r.number))
        prev = last_issue
        for rec in records:
            issue = str(rec.number)
            # 1. 期号递增
            if prev and int(issue) <= int(prev):
                res.add_issue(f"期号未递增: {issue} <= {prev}")
            prev = issue
            # 2. 日期合法
            if rec.draw_date and not cls._valid_date(rec.draw_date):
                res.add_issue(f"日期非法: {issue}={rec.draw_date}")
            # 3. 前区数量
            if len(rec.front) != rule["front_n"]:
                res.add_issue(f"前区数量错误: {issue} front={len(rec.front)}")
            # 4. 后区数量
            if len(rec.back) != rule["back_n"]:
                res.add_issue(f"后区数量错误: {issue} back={len(rec.back)}")
            # 5. 号码范围
            if not all(1 <= n <= rule["front_max"] for n in rec.front):
                res.add_issue(f"前区越界: {issue}")
            if not all(1 <= n <= rule["back_max"] for n in rec.back):
                res.add_issue(f"后区越界: {issue}")

        if records:
            res.new_issue = str(records[-1].number)
        return res

    @staticmethod
    def _valid_date(d: str) -> bool:
        try:
            datetime.strptime(d, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False


def validate_records(records: List, lottery: str = "dlt",
                     last_issue: str = "") -> ValidationResult:
    """便捷函数。"""
    return DrawValidator.validate(records, lottery, last_issue)
