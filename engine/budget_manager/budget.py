"""budget_manager - 预算规划器（v4.0.0 Phase 2）。

功能：
  用户设置月预算 / 年度预算
  计算：实际投入、预算占比、超额提醒
  输出 BudgetHealthReport

持久化：本地 JSON（~/.atlas/budget_v400.json，支持 ATLAS_STORAGE_DIR）。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import List, Optional

DISCLAIMER = "预算管理帮助你控制购彩支出，理性消费。彩票开奖结果具有随机性。"

DEFAULT_MONTH_BUDGET = 500.0
DEFAULT_YEAR_BUDGET = 6000.0


@dataclass
class BudgetSettings:
    """预算设置。"""

    month_budget: float = DEFAULT_MONTH_BUDGET
    year_budget: float = DEFAULT_YEAR_BUDGET

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BudgetHealthReport:
    """预算健康报告。"""

    month_budget: float = DEFAULT_MONTH_BUDGET
    year_budget: float = DEFAULT_YEAR_BUDGET
    month_spent: float = 0.0
    year_spent: float = 0.0
    month_ratio: float = 0.0
    year_ratio: float = 0.0
    month_over: bool = False
    year_over: bool = False
    exceed_amount: float = 0.0
    health_score: int = 100
    suggestions: List[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "month_budget": self.month_budget, "year_budget": self.year_budget,
            "month_spent": round(self.month_spent, 2),
            "year_spent": round(self.year_spent, 2),
            "month_ratio": round(self.month_ratio, 4),
            "year_ratio": round(self.year_ratio, 4),
            "month_over": self.month_over, "year_over": self.year_over,
            "exceed_amount": round(self.exceed_amount, 2),
            "health_score": self.health_score,
            "suggestions": list(self.suggestions),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = ["💰 预算健康报告"]
        lines.append(f"· 月预算：¥{self.month_budget:,.0f} | 本月已投入：¥{self.month_spent:,.0f}")
        lines.append(f"· 月预算占比：{self.month_ratio * 100:.0f}%")
        if self.month_over:
            lines.append(f"· ⚠️ 本月已超额 ¥{self.exceed_amount:,.0f}")
        lines.append(f"· 年预算：¥{self.year_budget:,.0f} | 今年已投入：¥{self.year_spent:,.0f}")
        lines.append(f"· 年预算占比：{self.year_ratio * 100:.0f}%")
        lines.append(f"· 预算健康度：{self.health_score}/100")
        if self.suggestions:
            lines.append("· 建议：")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class BudgetPlanner:
    """预算规划器。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "budget_v400.json")
        self._settings = BudgetSettings()
        self._load()

    # ---------- 持久化 ----------
    def _load(self) -> None:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    d = json.load(f)
                self._settings = BudgetSettings(**{k: v for k, v in d.items()
                                                   if k in BudgetSettings.__dataclass_fields__})
            except (json.JSONDecodeError, OSError, TypeError):
                self._settings = BudgetSettings()

    def _save(self) -> None:
        os.makedirs(self._dir, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._settings.to_dict(), f, ensure_ascii=False, indent=2)

    # ---------- 设置 ----------
    def set_budget(self, month_budget: Optional[float] = None,
                   year_budget: Optional[float] = None) -> BudgetSettings:
        if month_budget is not None:
            self._settings.month_budget = float(month_budget)
        if year_budget is not None:
            self._settings.year_budget = float(year_budget)
        self._save()
        return self._settings

    def get_settings(self) -> BudgetSettings:
        return self._settings

    @property
    def month_budget(self) -> float:
        return self._settings.month_budget

    @property
    def year_budget(self) -> float:
        return self._settings.year_budget

    # ---------- 实际投入计算 ----------
    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        if not date_str:
            return None
        try:
            if len(date_str) == 10:
                return date.fromisoformat(date_str)
            if len(date_str) == 5:
                return date.fromisoformat(f"{date.today().year}-{date_str}")
        except ValueError:
            return None
        return None

    @classmethod
    def spent_from_tickets(cls, tickets: List[dict]) -> tuple:
        """从票据计算 (本月投入, 今年投入)。"""
        today = date.today()
        month_spent = 0.0
        year_spent = 0.0
        for t in tickets:
            d = cls._parse_date(t.get("buy_date") or t.get("saved_at", "")[:10])
            cost = float(t.get("cost", 2.0))
            if d is None:
                continue
            if d.year == today.year:
                year_spent += cost
                if d.month == today.month:
                    month_spent += cost
        return month_spent, year_spent

    # ---------- 评估 ----------
    @classmethod
    def evaluate(cls, month_spent: float, year_spent: float,
                 month_budget: float = DEFAULT_MONTH_BUDGET,
                 year_budget: float = DEFAULT_YEAR_BUDGET) -> BudgetHealthReport:
        """评估预算健康度。"""
        month_ratio = month_spent / month_budget if month_budget > 0 else 0
        year_ratio = year_spent / year_budget if year_budget > 0 else 0
        month_over = month_spent > month_budget
        year_over = year_spent > year_budget
        exceed = max(0.0, month_spent - month_budget) + max(0.0, year_spent - year_budget)

        # 健康度：100 - 占比惩罚
        score = 100
        if month_ratio > 1:
            score -= min(40, int((month_ratio - 1) * 100))
        elif month_ratio > 0.8:
            score -= 15
        if year_ratio > 1:
            score -= min(30, int((year_ratio - 1) * 50))
        elif year_ratio > 0.8:
            score -= 10
        score = max(0, min(100, score))

        suggestions = []
        if month_over:
            suggestions.append(f"本月已超预算 ¥{month_spent - month_budget:,.0f}，建议暂停购彩")
        elif month_ratio > 0.8:
            suggestions.append(f"月预算已用 {month_ratio * 100:.0f}%，请注意控制")
        if year_over:
            suggestions.append("年度预算已超额，建议大幅缩减后续投入")
        if not suggestions:
            suggestions.append("预算控制良好，请保持")

        return BudgetHealthReport(
            month_budget=month_budget, year_budget=year_budget,
            month_spent=month_spent, year_spent=year_spent,
            month_ratio=month_ratio, year_ratio=year_ratio,
            month_over=month_over, year_over=year_over,
            exceed_amount=exceed, health_score=score,
            suggestions=suggestions,
        )

    def evaluate_tickets(self, tickets: List[dict]) -> BudgetHealthReport:
        """从票据评估。"""
        month, year = self.spent_from_tickets(tickets)
        return self.evaluate(month, year, self.month_budget, self.year_budget)
