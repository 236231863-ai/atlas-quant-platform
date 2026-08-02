"""user_behavior - 投注行为分析器（v4.0.0 Phase 1）。

BetBehaviorAnalyzer：基于票据数据分析用户投注行为。
  - 投注次数 / 总注数 / 总投入
  - 月均投入 / 年投入外推 / 平均单期金额
  - 追号次数（相同号码组合重复购买）
  - 高频购买周期（投入最高月份/星期）
  - 停止率（间隔 > 14 天的停歇比例）

输出 UserBehaviorReport + 行为风险等级 A-D + 建议。

声明：行为分析帮助用户了解投注习惯并管理风险，不涉及预测。
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional

DISCLAIMER = "行为分析帮助你了解自己的投注习惯并管理风险。彩票开奖结果具有随机性。"

GAP_DAYS = 14  # 停止判定间隔（天）


@dataclass
class UserBehaviorReport:
    """用户行为报告。"""

    total_bets: int = 0            # 投注期数（不同购买日期）
    total_notes: int = 0           # 总注数
    total_spent: float = 0.0       # 总投入
    monthly_avg: float = 0.0       # 月均投入
    annual_projection: float = 0.0  # 年投入外推
    avg_per_draw: float = 0.0      # 平均单期金额
    chase_count: int = 0           # 追号次数
    peak_month: str = ""           # 高频月份（YYYY-MM）
    peak_weekday: str = ""         # 高频星期
    stop_rate: float = 0.0         # 停止率 0-1
    risk_level: str = "A"          # A-D
    suggestions: List[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict:
        return {
            "total_bets": self.total_bets, "total_notes": self.total_notes,
            "total_spent": round(self.total_spent, 2),
            "monthly_avg": round(self.monthly_avg, 2),
            "annual_projection": round(self.annual_projection, 2),
            "avg_per_draw": round(self.avg_per_draw, 2),
            "chase_count": self.chase_count,
            "peak_month": self.peak_month, "peak_weekday": self.peak_weekday,
            "stop_rate": round(self.stop_rate, 4),
            "risk_level": self.risk_level, "suggestions": list(self.suggestions),
            "disclaimer": self.disclaimer,
        }

    def summary_text(self) -> str:
        lines = ["📊 你的投注行为分析"]
        lines.append(f"· 投注期数：{self.total_bets} 期 / 共 {self.total_notes} 注")
        lines.append(f"· 总投入：¥{self.total_spent:,.0f}")
        lines.append(f"· 月均投入：¥{self.monthly_avg:,.0f} / 年投入外推：¥{self.annual_projection:,.0f}")
        lines.append(f"· 平均单期金额：¥{self.avg_per_draw:.0f}")
        lines.append(f"· 追号次数：{self.chase_count} 次")
        if self.peak_month:
            lines.append(f"· 高频月份：{self.peak_month} / 高频星期：{self.peak_weekday or '—'}")
        lines.append(f"· 停止率：{self.stop_rate * 100:.0f}%")
        lines.append(f"· 行为风险等级：{self.risk_level}")
        if self.suggestions:
            lines.append("· 建议：")
            for s in self.suggestions:
                lines.append(f"  - {s}")
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class BetBehaviorAnalyzer:
    """投注行为分析器（基于票据数据）。"""

    # ---------- 工具 ----------
    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """解析 YYYY-MM-DD 或 MM-DD → date。"""
        if not date_str:
            return None
        try:
            if len(date_str) == 10:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            if len(date_str) == 5:
                return datetime.strptime(f"{date.today().year}-{date_str}", "%Y-%m-%d").date()
        except ValueError:
            return None
        return None

    @staticmethod
    def _risk_level(monthly: float, chase: int, stop_rate: float) -> str:
        if monthly > 1000 or chase >= 10:
            return "D"
        if monthly > 500 or chase >= 5 or stop_rate > 0.3:
            return "C"
        if monthly > 100 or chase >= 2:
            return "B"
        return "A"

    @staticmethod
    def _suggestions(monthly: float, chase: int, stop_rate: float,
                     budget_ratio: float = 0.0) -> List[str]:
        tips = []
        if monthly > 500:
            tips.append("月投入偏高，建议设定月预算并控制追号")
        elif monthly > 100:
            tips.append("建议设置月预算，跟踪投入趋势")
        if chase >= 3:
            tips.append(f"追号次数较多（{chase} 次），建议评估追号是否必要")
        if stop_rate > 0.3:
            tips.append("存在明显停歇-回归模式，建议规律化投注节奏")
        if not tips:
            tips.append("投注行为较理性，请继续保持并关注预算")
        return tips

    # ---------- 分析 ----------
    @classmethod
    def analyze(cls, tickets: List[dict]) -> UserBehaviorReport:
        """分析投注行为。

        tickets: 票据数据，每项含 buy_date/cost/front/back。
        """
        report = UserBehaviorReport()
        if not tickets:
            report.suggestions = ["暂无投注数据，保存票据后可分析行为。"]
            return report

        # 有效票据
        valid = [t for t in tickets if t.get("buy_date") or t.get("saved_at")]
        dates = []
        spent = 0.0
        notes = 0
        for t in valid:
            cost = float(t.get("cost", 2.0))
            spent += cost
            notes += 1
            d = cls._parse_date(t.get("buy_date") or t.get("saved_at", "")[:10])
            if d:
                dates.append(d)

        report.total_notes = notes
        report.total_spent = spent
        report.total_bets = len(set(dates)) if dates else len(valid)

        # 月/年投入
        if dates:
            months = {(d.year, d.month) for d in dates}
            n_months = max(1, len(months))
            report.monthly_avg = spent / n_months
            report.annual_projection = report.monthly_avg * 12
        else:
            report.monthly_avg = spent / 12
            report.annual_projection = spent

        report.avg_per_draw = spent / report.total_bets if report.total_bets else 0

        # 追号：相同 front+back 组合在不同日期重复
        combo_dates = {}
        for t in valid:
            key = (tuple(sorted(t.get("front", []))), tuple(sorted(t.get("back", []))))
            combo_dates.setdefault(key, []).append(t.get("buy_date") or "")
        chase = 0
        for key, ds in combo_dates.items():
            uniq = {d for d in ds if d}
            if len(uniq) >= 2:
                chase += len(uniq) - 1
        report.chase_count = chase

        # 高频月份/星期
        if dates:
            month_counter = Counter(f"{d.year}-{d.month:02d}" for d in dates)
            report.peak_month = month_counter.most_common(1)[0][0]
            wd_counter = Counter("一二三四五六日"[d.weekday()] for d in dates)
            report.peak_weekday = wd_counter.most_common(1)[0][0]

        # 停止率
        if len(dates) >= 2:
            sorted_dates = sorted(dates)
            gaps = [(b - a).days for a, b in zip(sorted_dates, sorted_dates[1:])]
            stop = sum(1 for g in gaps if g > GAP_DAYS)
            report.stop_rate = stop / len(gaps) if gaps else 0

        report.risk_level = cls._risk_level(report.monthly_avg, chase, report.stop_rate)
        report.suggestions = cls._suggestions(report.monthly_avg, chase, report.stop_rate)
        return report

    @classmethod
    def analyze_from_manager(cls, ticket_manager=None) -> UserBehaviorReport:
        """从 TicketManager 读取票据并分析。"""
        if ticket_manager is None:
            from engine.ticket_system import TicketManager
            ticket_manager = TicketManager()
        tickets = [t.__dict__ for t in ticket_manager.list_all()]
        return cls.analyze(tickets)


def analyze_behavior(tickets: List[dict]) -> UserBehaviorReport:
    """便捷函数：投注行为分析。"""
    return BetBehaviorAnalyzer.analyze(tickets)
