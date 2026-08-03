"""asset_center - 彩票资产中心（v4.3 P3）。

我的彩票资产（必须展示风险，不是鼓励购彩）：
  累计购买 / 累计中奖 / 中奖率 / 投入金额 / 净收益 / 最大单次中奖 / 年度报告

复用 user_archive（LotteryArchive 基础统计）+ 增加风险维度。
红线：只陈述已发生事实与风险，不预测、不诱导购彩。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

DISCLAIMER = "资产数据仅反映你的历史购彩与中奖，彩票开奖结果具有随机性，请理性购彩。"

LOTTERY_NAMES = {"dlt": "大乐透", "ssq": "双色球"}


@dataclass
class AnnualSummary:
    """某年度资产总结。"""

    year: int
    tickets: int = 0
    investment: float = 0.0
    winnings: float = 0.0
    win_count: int = 0
    max_win: float = 0.0
    active_months: int = 0
    favorite_lottery: str = ""

    @property
    def net(self) -> float:
        return self.winnings - self.investment

    def to_dict(self) -> dict:
        return {"year": self.year, "tickets": self.tickets,
                "investment": round(self.investment, 2),
                "winnings": round(self.winnings, 2),
                "win_count": self.win_count, "max_win": round(self.max_win, 2),
                "active_months": self.active_months,
                "favorite_lottery": self.favorite_lottery,
                "net": round(self.net, 2)}


@dataclass
class AssetReport:
    """彩票资产中心报告。"""

    lottery: str = "all"
    total_tickets: int = 0
    total_investment: float = 0.0      # 累计购买
    total_winnings: float = 0.0        # 累计中奖
    win_count: int = 0                 # 中奖次数
    max_win: float = 0.0               # 最大单次中奖
    purchase_months: int = 0
    favorite_lotteries: List[str] = field(default_factory=list)
    annual: List[AnnualSummary] = field(default_factory=list)
    disclaimer: str = DISCLAIMER

    @property
    def win_rate(self) -> float:
        """中奖率 = 中奖张数 / 总张数。"""
        if self.total_tickets == 0:
            return 0.0
        return self.win_count / self.total_tickets

    @property
    def net(self) -> float:
        """净收益 = 累计中奖 - 累计购买。"""
        return self.total_winnings - self.total_investment

    @property
    def loss_rate(self) -> float:
        """亏损率 = max(0, -净收益) / 累计购买。"""
        if self.total_investment <= 0:
            return 0.0
        return max(0.0, -self.net) / self.total_investment

    @property
    def risk_level(self) -> str:
        """风险等级 A/B/C/D（基于亏损率，A 最理性）。"""
        if self.total_investment <= 0:
            return "A"
        if self.net >= 0:
            return "A"
        if self.loss_rate < 0.60:
            return "B"
        if self.loss_rate < 0.85:
            return "C"
        return "D"

    @property
    def risk_text(self) -> str:
        mapping = {
            "A": "理性：投入与回报较平衡，或暂无明显亏损",
            "B": "较理性：存在一定亏损，建议控制投入节奏",
            "C": "需关注：亏损比例偏高，建议设置预算上限",
            "D": "高风险：亏损比例很高，强烈建议停止投入并复盘",
        }
        return mapping.get(self.risk_level, "")

    def to_dict(self) -> dict:
        return {"lottery": self.lottery,
                "total_tickets": self.total_tickets,
                "total_investment": round(self.total_investment, 2),
                "total_winnings": round(self.total_winnings, 2),
                "win_count": self.win_count,
                "max_win": round(self.max_win, 2),
                "win_rate": round(self.win_rate, 4),
                "net": round(self.net, 2),
                "loss_rate": round(self.loss_rate, 4),
                "risk_level": self.risk_level,
                "purchase_months": self.purchase_months,
                "favorite_lotteries": list(self.favorite_lotteries),
                "annual": [a.to_dict() for a in self.annual],
                "disclaimer": self.disclaimer}

    def summary_text(self) -> str:
        lines = ["💎 我的彩票资产"]
        lines.append(f"· 累计购买：¥{self.total_investment:,.0f}")
        lines.append(f"· 累计中奖：¥{self.total_winnings:,.0f}")
        lines.append(f"· 净收益：¥{self.net:,.0f}")
        lines.append(f"· 中奖率：{self.win_rate * 100:.1f}%（{self.win_count}/{self.total_tickets} 张）")
        lines.append(f"· 最大单次中奖：¥{self.max_win:,.0f}")
        lines.append(f"· 风险等级：{self.risk_level}（{self.risk_text}）")
        if self.favorite_lotteries:
            lines.append("· 常购彩种：" + " / ".join(self.favorite_lotteries))
        lines.append(f"· {self.disclaimer}")
        return "\n".join(lines)


class AssetCenter:
    """彩票资产中心引擎。"""

    @classmethod
    def _name(cls, lottery: str) -> str:
        return LOTTERY_NAMES.get(lottery, lottery)

    @classmethod
    def _win_of(cls, t: dict) -> float:
        """单张票据中奖金额（复用 PrizeCalculator）。"""
        from engine.lottery_intent.draw_matcher import DrawResultMatcher
        from engine.lottery_intent.prize_calculator import PrizeCalculator
        try:
            match = DrawResultMatcher().match(
                list(t.get("front", [])), list(t.get("back", [])),
                lottery=t.get("lottery", "dlt"), draw_date=t.get("draw_date", ""))
            if not match.draw:
                return 0.0
            pr = PrizeCalculator.calculate(match.front_hits, match.back_hits,
                                           t.get("lottery", "dlt"))
            return pr.amount if pr.won else 0.0
        except Exception:
            return 0.0

    @classmethod
    def build(cls, tickets: List[dict], lottery: Optional[str] = None) -> AssetReport:
        """从票据列表构建资产报告。lottery=None 表示全部彩种。"""
        rep = AssetReport(lottery=lottery or "all")
        if not tickets:
            return rep

        # 复用 user_archive 基础统计
        from engine.user_archive import build_archive
        arch = build_archive(tickets)
        rep.total_tickets = arch.total_tickets
        rep.total_investment = arch.total_investment
        rep.total_winnings = arch.total_winnings
        rep.win_count = arch.win_count
        rep.max_win = arch.max_win
        rep.purchase_months = arch.purchase_months
        rep.favorite_lotteries = list(arch.favorite_lotteries)

        # 年度汇总
        years = sorted({(t.get("buy_date") or t.get("saved_at", "") or "")[:4]
                        for t in tickets if (t.get("buy_date") or t.get("saved_at", ""))})
        for y in years:
            if not y.isdigit():
                continue
            rep.annual.append(cls.annual_report(tickets, int(y)))
        return rep

    @classmethod
    def annual_report(cls, tickets: List[dict], year: int) -> AnnualSummary:
        """某年度总结。"""
        ys = str(year)
        year_tickets = [t for t in tickets
                        if (t.get("buy_date") or t.get("saved_at", ""))[:4] == ys]
        a = AnnualSummary(year=year)
        if not year_tickets:
            return a
        a.tickets = len(year_tickets)
        a.investment = sum(float(t.get("cost", 2.0)) for t in year_tickets)
        win_amounts = []
        for t in year_tickets:
            amt = cls._win_of(t)
            if amt > 0:
                a.win_count += 1
                a.winnings += amt
                win_amounts.append(amt)
        if win_amounts:
            a.max_win = max(win_amounts)
        months = {(t.get("buy_date") or t.get("saved_at", ""))[:7]
                  for t in year_tickets
                  if (t.get("buy_date") or t.get("saved_at", ""))[:7]}
        a.active_months = len(months)
        # 常购彩种
        from collections import Counter
        cnt = Counter(t.get("lottery", "dlt") for t in year_tickets)
        if cnt:
            a.favorite_lottery = cls._name(cnt.most_common(1)[0][0])
        return a

    @classmethod
    def risk_line(cls, rep: AssetReport) -> str:
        """风险提示行（必须展示风险）。"""
        return f"⚠️ 风险提示：累计投入 ¥{rep.total_investment:,.0f}，累计回报 ¥{rep.total_winnings:,.0f}，" \
               f"净收益 ¥{rep.net:,.0f}（亏损率 {rep.loss_rate * 100:.0f}%）。{rep.risk_text}"


def build_asset_report(tickets: List[dict], lottery: Optional[str] = None) -> AssetReport:
    """便捷函数。"""
    return AssetCenter.build(tickets, lottery=lottery)
