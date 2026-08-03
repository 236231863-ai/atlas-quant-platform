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
from datetime import date, timedelta
from typing import List, Optional

DISCLAIMER = "预算管理帮助你控制购彩支出，理性消费。彩票开奖结果具有随机性。"

DEFAULT_WEEK_BUDGET = 120.0
DEFAULT_MONTH_BUDGET = 500.0
DEFAULT_YEAR_BUDGET = 6000.0


@dataclass
class BudgetSettings:
    """预算设置（v4.1 阶段3：周/月/年）。"""

    week_budget: float = DEFAULT_WEEK_BUDGET
    month_budget: float = DEFAULT_MONTH_BUDGET
    year_budget: float = DEFAULT_YEAR_BUDGET

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BudgetHealthReport:
    """预算健康报告（v4.1 阶段3：周/月/年 + 亏损率 + 预警）。"""

    week_budget: float = DEFAULT_WEEK_BUDGET
    month_budget: float = DEFAULT_MONTH_BUDGET
    year_budget: float = DEFAULT_YEAR_BUDGET
    week_spent: float = 0.0
    month_spent: float = 0.0
    year_spent: float = 0.0
    week_ratio: float = 0.0
    month_ratio: float = 0.0
    year_ratio: float = 0.0
    week_over: bool = False
    month_over: bool = False
    year_over: bool = False
    exceed_amount: float = 0.0
    loss_rate: float = 0.0               # 亏损率（净收益/投入）
    warning_level: str = "正常"           # 正常/预警/超支
    health_score: int = 100
    suggestions: List[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "week_budget": self.week_budget, "month_budget": self.month_budget,
            "year_budget": self.year_budget,
            "week_spent": round(self.week_spent, 2),
            "month_spent": round(self.month_spent, 2),
            "year_spent": round(self.year_spent, 2),
            "week_ratio": round(self.week_ratio, 4),
            "month_ratio": round(self.month_ratio, 4),
            "year_ratio": round(self.year_ratio, 4),
            "week_over": self.week_over, "month_over": self.month_over,
            "year_over": self.year_over,
            "exceed_amount": round(self.exceed_amount, 2),
            "loss_rate": round(self.loss_rate, 4),
            "warning_level": self.warning_level,
            "health_score": self.health_score,
            "suggestions": list(self.suggestions),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = ["💰 预算中心（周/月/年）"]
        lines.append(f"· 本周：¥{self.week_spent:,.0f} / ¥{self.week_budget:,.0f}（{self.week_ratio * 100:.0f}%）")
        lines.append(f"· 本月：¥{self.month_spent:,.0f} / ¥{self.month_budget:,.0f}（{self.month_ratio * 100:.0f}%）")
        lines.append(f"· 今年：¥{self.year_spent:,.0f} / ¥{self.year_budget:,.0f}（{self.year_ratio * 100:.0f}%）")
        if self.week_over:
            lines.append(f"· ⚠️ 本周已超额 ¥{self.week_spent - self.week_budget:,.0f}")
        if self.month_over:
            lines.append(f"· ⚠️ 本月已超额 ¥{self.month_spent - self.month_budget:,.0f}")
        if self.year_over:
            lines.append(f"· ⚠️ 年度已超额 ¥{self.year_spent - self.year_budget:,.0f}")
        lines.append(f"· 累计亏损率：{self.loss_rate * 100:+.1f}%")
        lines.append(f"· 预警级别：{self.warning_level} | 健康度：{self.health_score}/100")
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
    def set_budget(self, week_budget: Optional[float] = None,
                   month_budget: Optional[float] = None,
                   year_budget: Optional[float] = None) -> BudgetSettings:
        if week_budget is not None:
            self._settings.week_budget = float(week_budget)
        if month_budget is not None:
            self._settings.month_budget = float(month_budget)
        if year_budget is not None:
            self._settings.year_budget = float(year_budget)
        self._save()
        return self._settings

    def get_settings(self) -> BudgetSettings:
        return self._settings

    @property
    def week_budget(self) -> float:
        return self._settings.week_budget

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

    @staticmethod
    def _week_start(d: date) -> date:
        """ISO 周起始（周一）。"""
        return d - timedelta(days=d.weekday())

    @classmethod
    def spent_from_tickets(cls, tickets: List[dict]) -> tuple:
        """从票据计算 (本周投入, 本月投入, 今年投入)。"""
        today = date.today()
        week_start = cls._week_start(today)
        week_spent = 0.0
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
                if week_start <= d <= today:
                    week_spent += cost
        return week_spent, month_spent, year_spent

    # ---------- 评估 ----------
    @classmethod
    def evaluate(cls, week_spent: float, month_spent: float, year_spent: float,
                 week_budget: float = DEFAULT_WEEK_BUDGET,
                 month_budget: float = DEFAULT_MONTH_BUDGET,
                 year_budget: float = DEFAULT_YEAR_BUDGET,
                 loss_rate: float = 0.0) -> BudgetHealthReport:
        """评估预算健康度（v4.1 阶段3：周/月/年 + 亏损率 + 预警）。"""
        week_ratio = week_spent / week_budget if week_budget > 0 else 0
        month_ratio = month_spent / month_budget if month_budget > 0 else 0
        year_ratio = year_spent / year_budget if year_budget > 0 else 0
        week_over = week_spent > week_budget
        month_over = month_spent > month_budget
        year_over = year_spent > year_budget
        exceed = (max(0.0, week_spent - week_budget)
                  + max(0.0, month_spent - month_budget)
                  + max(0.0, year_spent - year_budget))

        # 健康度：100 - 占比惩罚
        score = 100
        if week_ratio > 1:
            score -= min(20, int((week_ratio - 1) * 50))
        elif week_ratio > 0.8:
            score -= 8
        if month_ratio > 1:
            score -= min(35, int((month_ratio - 1) * 80))
        elif month_ratio > 0.8:
            score -= 15
        if year_ratio > 1:
            score -= min(30, int((year_ratio - 1) * 40))
        elif year_ratio > 0.8:
            score -= 10
        score = max(0, min(100, score))

        # 预警级别
        if week_over or month_over or year_over:
            warning_level = "超支"
        elif week_ratio > 0.8 or month_ratio > 0.8 or year_ratio > 0.8:
            warning_level = "预警"
        else:
            warning_level = "正常"

        suggestions = []
        if week_over:
            suggestions.append(f"本周已超预算 ¥{week_spent - week_budget:,.0f}")
        if month_over:
            suggestions.append(f"本月已超预算 ¥{month_spent - month_budget:,.0f}，建议暂停购彩")
        elif month_ratio > 0.8:
            suggestions.append(f"月预算已用 {month_ratio * 100:.0f}%，请注意控制")
        if year_over:
            suggestions.append("年度预算已超额，建议大幅缩减后续投入")
        if loss_rate < -0.5:
            suggestions.append(f"累计亏损率 {loss_rate * 100:.0f}%，彩票为负期望游戏，建议控制投入")
        if not suggestions:
            suggestions.append("预算控制良好，请保持")

        return BudgetHealthReport(
            week_budget=week_budget, month_budget=month_budget, year_budget=year_budget,
            week_spent=week_spent, month_spent=month_spent, year_spent=year_spent,
            week_ratio=week_ratio, month_ratio=month_ratio, year_ratio=year_ratio,
            week_over=week_over, month_over=month_over, year_over=year_over,
            exceed_amount=exceed, loss_rate=loss_rate, warning_level=warning_level,
            health_score=score, suggestions=suggestions,
        )

    def evaluate_tickets(self, tickets: List[dict]) -> BudgetHealthReport:
        """从票据评估（含亏损率）。"""
        week, month, year = self.spent_from_tickets(tickets)
        loss_rate = 0.0
        try:
            from engine.personal_review import PersonalReviewEngine
            rv = PersonalReviewEngine.review(tickets)
            loss_rate = rv.roi
        except Exception:
            pass
        return self.evaluate(week, month, year,
                             self.week_budget, self.month_budget, self.year_budget,
                             loss_rate=loss_rate)

    # ---------- v4.1.1 Phase 4：预算/连续购买提醒 ----------
    @staticmethod
    def consecutive_weeks(tickets: List[dict]) -> int:
        """连续购买周数（按票据日期所在 ISO 周往前数）。"""
        weeks = set()
        for t in tickets:
            d = BudgetPlanner._parse_date(t.get("buy_date") or t.get("saved_at", "")[:10])
            if d:
                iso = d.isocalendar()
                weeks.add((iso[0], iso[1]))
        if not weeks:
            return 0
        today_iso = date.today().isocalendar()
        cur = (today_iso[0], today_iso[1])
        streak = 0
        while cur in weeks:
            streak += 1
            # 上一周
            from datetime import date as _d
            from datetime import timedelta
            anchor = _d.fromisocalendar(cur[0], cur[1], 1) - timedelta(days=7)
            a = anchor.isocalendar()
            cur = (a[0], a[1])
        return streak

    @classmethod
    def reminders(cls, tickets: List[dict]) -> List[str]:
        """预算提醒文案（v4.1.1 Phase 4）。"""
        r = cls().evaluate_tickets(tickets)
        tips = []
        if r.week_ratio >= 0.8:
            tips.append(f"本周投入已达到预算 {r.week_ratio * 100:.0f}%")
        weeks = cls.consecutive_weeks(tickets)
        if weeks >= 2:
            tips.append(f"已连续购买 {weeks} 周，建议关注投入节奏")
        if r.month_over:
            tips.append(f"本月已超预算 ¥{r.month_spent - r.month_budget:,.0f}")
        return tips
