"""data_quality.quality - 数据质量系统（v4.8 P5）。

检查：重复票 / 错误号码 / 日期异常 / 金额异常 / 彩种错误 → 可信等级 A/B/C。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

RULES = {
    "dlt": {"front_n": 5, "back_n": 2, "front_max": 35, "back_max": 12},
    "ssq": {"front_n": 6, "back_n": 1, "front_max": 33, "back_max": 16},
}


@dataclass
class QualityReport:
    """数据质量报告。"""

    total_tickets: int = 0
    duplicates: int = 0
    invalid_numbers: int = 0
    date_anomalies: int = 0
    amount_anomalies: int = 0
    lottery_errors: int = 0
    issues: List[str] = field(default_factory=list)

    @property
    def issue_count(self) -> int:
        return self.duplicates + self.invalid_numbers + self.date_anomalies + \
            self.amount_anomalies + self.lottery_errors

    @property
    def trust_level(self) -> str:
        """A 优 / B 可 / C 差。"""
        if self.total_tickets == 0:
            return "A"
        ratio = self.issue_count / self.total_tickets
        if ratio == 0:
            return "A"
        if ratio < 0.1:
            return "B"
        return "C"

    def to_dict(self) -> dict:
        return {"total_tickets": self.total_tickets, "duplicates": self.duplicates,
                "invalid_numbers": self.invalid_numbers,
                "date_anomalies": self.date_anomalies,
                "amount_anomalies": self.amount_anomalies,
                "lottery_errors": self.lottery_errors,
                "trust_level": self.trust_level}

    def summary_text(self) -> str:
        lines = ["🛡 数据质量报告"]
        lines.append(f"· 总数：{self.total_tickets} 张 · 可信等级 {self.trust_level}")
        lines.append(f"· 重复票：{self.duplicates} · 错误号码：{self.invalid_numbers}")
        lines.append(f"· 日期异常：{self.date_anomalies} · 金额异常：{self.amount_anomalies}")
        lines.append(f"· 彩种错误：{self.lottery_errors}")
        if self.issues:
            for i in self.issues[:5]:
                lines.append(f"  ⚠️ {i}")
        return "\n".join(lines)


class DataQualityChecker:
    """数据质量检查器。"""

    @classmethod
    def _combo_key(cls, t: dict) -> str:
        f = " ".join(str(n) for n in t.get("front", []))
        b = " ".join(str(n) for n in t.get("back", []))
        return f"{f}+{b}"

    @classmethod
    def check(cls, tickets: List[dict]) -> QualityReport:
        """检查全部票据。"""
        rep = QualityReport(total_tickets=len(tickets))
        if not tickets:
            return rep

        # 重复票
        combos = Counter(cls._combo_key(t) for t in tickets)
        rep.duplicates = sum(v - 1 for v in combos.values() if v > 1)

        today = date.today().isoformat()
        for t in tickets:
            lottery = t.get("lottery", "dlt")
            rule = RULES.get(lottery, RULES["dlt"])
            front = t.get("front", [])
            back = t.get("back", [])

            # 错误号码（数量/范围）
            if len(front) != rule["front_n"] or len(back) != rule["back_n"]:
                rep.invalid_numbers += 1
                rep.issues.append(f"号码数量错误：{t.get('ticket_id', '?')}")
            elif not all(1 <= n <= rule["front_max"] for n in front) or \
                 not all(1 <= n <= rule["back_max"] for n in back):
                rep.invalid_numbers += 1
                rep.issues.append(f"号码越界：{t.get('ticket_id', '?')}")

            # 日期异常
            d = t.get("buy_date") or t.get("saved_at", "")[:10]
            if d and len(d) == 10 and d > today:
                rep.date_anomalies += 1
            elif d and len(d) != 10:
                rep.date_anomalies += 1

            # 金额异常
            cost = t.get("cost", 2.0)
            if cost <= 0 or cost > 10000:
                rep.amount_anomalies += 1

            # 彩种错误（号码不在彩种范围）
            if lottery == "ssq" and max(front or [1]) > 33:
                rep.lottery_errors += 1
            elif lottery == "dlt" and max(front or [1]) > 35:
                rep.lottery_errors += 1
        return rep


def check_data_quality(tickets: List[dict]) -> QualityReport:
    """便捷函数。"""
    return DataQualityChecker.check(tickets)
