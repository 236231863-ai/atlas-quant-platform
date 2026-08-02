"""lottery_quant - 量化分析总控制器（v3.9.0 Phase 7）。

综合各引擎，为用户的投注组合生成完整量化分析：
  结构评分 → 概率报告 → 模拟覆盖 → 组合分析 → 风险分析 → 量化报告

重要：所有输出含随机性声明，只提供统计分析与风险管理。
"""
from __future__ import annotations

import random
from typing import List, Optional

from .structure.analyzer import StructureAnalyzer
from .probability.model import dlt_probabilities, ssq_probabilities
from .simulation.monte_carlo import SimulationEngine
from .portfolio.analyzer import PortfolioAnalyzer
from .risk.engine import RiskEngine

DEFAULT_SIM_TRIALS = 20_000


def _lottery_name(lottery: str) -> str:
    return "大乐透" if lottery == "dlt" else "双色球"


class QuantDirector:
    """量化分析总控制器。"""

    @staticmethod
    def _build_tickets(tickets: List[dict], lottery: str) -> List[dict]:
        """规范化票据（过滤无效注）。"""
        params = {"dlt": (5, 2), "ssq": (6, 1)}
        fn, bn = params.get(lottery, (5, 2))
        out = []
        for t in tickets:
            front = list(t.get("front", []))
            back = list(t.get("back", []))
            if len(front) == fn and len(back) == bn:
                out.append({"front": front, "back": back})
        return out

    @classmethod
    def full_report(cls, tickets: List[dict], lottery: str = "dlt",
                    sim_trials: int = DEFAULT_SIM_TRIALS, seed: Optional[int] = None) -> dict:
        """综合量化报告。"""
        tickets = cls._build_tickets(tickets, lottery)
        name = _lottery_name(lottery)

        if not tickets:
            return {"is_quant": True, "report_text": "未解析到有效号码，请提供前区+后区号码。"}

        # 1. 结构评分
        structure = StructureAnalyzer.analyze(tickets, lottery)

        # 2. 概率报告（理论）
        prob = (dlt_probabilities() if lottery == "dlt" else ssq_probabilities())

        # 3. 模拟覆盖
        sim = SimulationEngine.simulate(tickets, lottery, trials=sim_trials, seed=seed)

        # 4. 组合分析
        portfolio = PortfolioAnalyzer.analyze(tickets, lottery)

        # 5. 风险分析
        risk = RiskEngine.analyze(cost_per_note=2.0, notes_per_draw=len(tickets),
                                  draws_per_week=3, weeks=52, lottery=lottery,
                                  tickets=tickets, n_years=60, seed=seed or 42)

        lines = [f"📊 {name}量化分析报告"]
        lines.append("")
        lines.append(f"🎯 组合评分：{structure.total_score}/100（{structure.assessment}）")
        lines.append(f"· {structure.disclaimer}")
        lines.append("")
        lines.append("🎲 概率模型")
        lines.append(f"· 一等奖概率：约 1/{prob.first_prize_one_in:,.0f}")
        lines.append(f"· 总中奖率：{prob.total_win_probability * 100:.2f}%")
        lines.append(f"· {prob.disclaimer}")
        lines.append("")
        lines.append("🎰 蒙特卡洛模拟")
        lines.append(f"· 模拟次数：{sim.trials:,} 次（{sim.note_count} 注）")
        lines.append(f"· 覆盖率：{sim.coverage_rate * 100:.2f}%")
        lines.append(f"· 期望奖金：¥{sim.expected_return:.2f}/期")
        lines.append(f"· {sim.disclaimer}")
        lines.append("")
        lines.append("🧩 组合分析")
        lines.append(f"· 重复率：{portfolio.duplicate_ratio * 100:.0f}%")
        lines.append(f"· 相关性：{portfolio.correlation * 100:.0f}% | 覆盖率：{portfolio.coverage * 100:.0f}%")
        lines.append(f"· 集中风险：{portfolio.risk_assessment}")
        lines.append(f"· {portfolio.disclaimer}")
        lines.append("")
        lines.append("💰 资金风险")
        lines.append(f"· 年度投入（每周3期×52周）：¥{risk.annual_investment:,.0f}")
        lines.append(f"· 亏损概率：{risk.lose_probability * 100:.1f}% | 风险等级：{risk.risk_level}")
        lines.append(f"· {risk.disclaimer}")
        lines.append("")
        lines.append("📌 汇总")
        lines.append("· 本报告仅提供统计分析、概率计算与风险管理。")
        lines.append("· 彩票开奖结果具有随机性，任何号码组合中奖概率相同。")

        return {
            "is_quant": True,
            "lottery": lottery,
            "tickets": len(tickets),
            "score": structure.total_score,
            "coverage_rate": sim.coverage_rate,
            "risk_level": risk.risk_level,
            "report_text": "\n".join(lines),
        }

    @classmethod
    def structure_report(cls, tickets: List[dict], lottery: str = "dlt") -> dict:
        """仅结构分析。"""
        tickets = cls._build_tickets(tickets, lottery)
        if not tickets:
            return {"is_quant": True, "report_text": "未解析到有效号码。"}
        s = StructureAnalyzer.analyze(tickets, lottery)
        return {
            "is_quant": True, "lottery": lottery, "tickets": len(tickets),
            "report_text": (f"🎯 组合评分：{s.total_score}/100（{s.assessment}）\n"
                            f"· 奇偶比：{s.metrics.odd_even_ratio} 大小比：{s.metrics.big_small_ratio}\n"
                            f"· 三区分布：{s.metrics.zone_distribution} 和值：{s.metrics.front_sum} 跨度：{s.metrics.span}\n"
                            f"· {s.disclaimer}"),
        }

    @classmethod
    def risk_report(cls, tickets: List[dict], lottery: str = "dlt") -> dict:
        """仅风险分析。"""
        tickets = cls._build_tickets(tickets, lottery)
        risk = RiskEngine.analyze(cost_per_note=2.0, notes_per_draw=len(tickets) or 1,
                                  draws_per_week=3, weeks=52, lottery=lottery,
                                  tickets=tickets or None, n_years=60, seed=42)
        return {
            "is_quant": True, "lottery": lottery, "tickets": len(tickets),
            "report_text": risk.summary_text(),
        }

    @classmethod
    def simulation_report(cls, tickets: List[dict], lottery: str = "dlt",
                          trials: int = DEFAULT_SIM_TRIALS) -> dict:
        """仅模拟覆盖。"""
        tickets = cls._build_tickets(tickets, lottery)
        if not tickets:
            return {"is_quant": True, "report_text": "未解析到有效号码。"}
        sim = SimulationEngine.simulate(tickets, lottery, trials=trials, seed=42)
        return {"is_quant": True, "lottery": lottery, "tickets": len(tickets),
                "report_text": sim.summary_text()}

    @classmethod
    def portfolio_report(cls, tickets: List[dict], lottery: str = "dlt") -> dict:
        """仅组合分析。"""
        tickets = cls._build_tickets(tickets, lottery)
        if not tickets:
            return {"is_quant": True, "report_text": "未解析到有效号码。"}
        p = PortfolioAnalyzer.analyze(tickets, lottery)
        return {"is_quant": True, "lottery": lottery, "tickets": len(tickets),
                "report_text": p.summary_text()}

    @classmethod
    def probability_report(cls, lottery: str = "dlt") -> dict:
        """仅概率模型。"""
        prob = (dlt_probabilities() if lottery == "dlt" else ssq_probabilities())
        return {"is_quant": True, "lottery": lottery,
                "report_text": prob.summary_text()}


def quant_full_report(tickets: List[dict], lottery: str = "dlt",
                      sim_trials: int = DEFAULT_SIM_TRIALS) -> dict:
    """便捷函数：完整量化报告。"""
    return QuantDirector.full_report(tickets, lottery, sim_trials=sim_trials)
