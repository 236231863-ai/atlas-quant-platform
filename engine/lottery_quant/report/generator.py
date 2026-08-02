"""report - 量化报告生成器（v3.9.0 Phase 8）。

生成 Lottery Quant Report（Markdown），并可导出 MD / PDF / PNG。
所有报告含免责声明：本报告基于历史统计，不能预测未来开奖。
"""
from __future__ import annotations

from typing import List, Optional

from engine.export.markdown import MarkdownExporter
from engine.export.pdf import PDFExporter

DISCLAIMER = "本报告基于历史统计，不能预测未来开奖。彩票开奖结果具有随机性。"


class QuantReportGenerator:
    """量化报告生成器。"""

    def __init__(self, tickets: List[dict], lottery: str = "dlt",
                 sim_trials: int = 20_000):
        self.tickets = tickets
        self.lottery = lottery
        self.sim_trials = sim_trials
        self._data = None

    def _collect(self) -> dict:
        """收集各引擎数据。"""
        if self._data is not None:
            return self._data
        from engine.lottery_quant.quant_director import QuantDirector
        data = QuantDirector.full_report(self.tickets, self.lottery,
                                         sim_trials=self.sim_trials)
        from engine.lottery_quant.structure import StructureAnalyzer
        from engine.lottery_quant.probability import dlt_probabilities, ssq_probabilities
        from engine.lottery_quant.simulation import SimulationEngine
        from engine.lottery_quant.portfolio import PortfolioAnalyzer
        from engine.lottery_quant.risk import RiskEngine
        from engine.lottery_quant.backtest import StrategyBacktester

        structure = StructureAnalyzer.analyze(self.tickets, self.lottery)
        prob = (dlt_probabilities() if self.lottery == "dlt" else ssq_probabilities())
        sim = SimulationEngine.simulate(self.tickets, self.lottery, trials=self.sim_trials, seed=42)
        portfolio = PortfolioAnalyzer.analyze(self.tickets, self.lottery)
        risk = RiskEngine.analyze(cost_per_note=2.0, notes_per_draw=len(self.tickets),
                                  draws_per_week=3, weeks=52, lottery=self.lottery,
                                  tickets=self.tickets, n_years=60, seed=42)
        bt = StrategyBacktester.run(periods=120)
        self._data = {
            "full": data, "structure": structure, "prob": prob, "sim": sim,
            "portfolio": portfolio, "risk": risk, "backtest": bt,
        }
        return self._data

    def to_markdown(self) -> str:
        """生成 Markdown 报告内容。"""
        d = self._collect()
        name = "大乐透" if self.lottery == "dlt" else "双色球"
        lines = [f"# Atlas 彩票量化分析报告（{name}）", ""]
        lines.append(f"> 报告日期：2026-08-02")
        lines.append(f"> 投注注数：{len(self.tickets)}")
        lines.append("")

        lines.append("## 免责声明")
        lines.append(f"> {DISCLAIMER}")
        lines.append("")

        lines.append("## 组合评分")
        s = d["structure"]
        lines.append(f"- 评分：**{s.total_score}/100**（{s.assessment}）")
        lines.append(f"- 奇偶比：{s.metrics.odd_even_ratio} / 大小比：{s.metrics.big_small_ratio}")
        lines.append(f"- 三区分布：{s.metrics.zone_distribution} / 和值：{s.metrics.front_sum} / 跨度：{s.metrics.span}")
        lines.append("")

        lines.append("## 概率模型")
        p = d["prob"]
        lines.append(f"- 一等奖概率：约 1/{p.first_prize_one_in:,.0f}")
        lines.append(f"- 总中奖率：{p.total_win_probability * 100:.2f}%")
        lines.append("")

        lines.append("## 蒙特卡洛模拟")
        sim = d["sim"]
        lines.append(f"- 模拟次数：{sim.trials:,}")
        lines.append(f"- 覆盖率：{sim.coverage_rate * 100:.2f}%")
        lines.append(f"- 期望奖金：¥{sim.expected_return:.2f}/期")
        lines.append("")

        lines.append("## 组合分析")
        pf = d["portfolio"]
        lines.append(f"- 重复率：{pf.duplicate_ratio * 100:.0f}% / 相关性：{pf.correlation * 100:.0f}%")
        lines.append(f"- 覆盖范围：{pf.coverage * 100:.0f}% / 集中风险：{pf.risk_assessment}")
        lines.append("")

        lines.append("## 资金风险")
        rk = d["risk"]
        lines.append(f"- 年度投入：¥{rk.annual_investment:,.0f}")
        lines.append(f"- 预计回报：¥{rk.expected_return:,.0f} / 亏损概率：{rk.lose_probability * 100:.1f}%")
        lines.append(f"- 风险等级：{rk.risk_level}")
        lines.append("")

        lines.append("## 策略回测（最近 120 期）")
        bt = d["backtest"]
        for m, perf in bt.strategies.items():
            label = {"hot": "热号", "cold": "冷号", "balanced": "均衡", "random": "随机"}.get(m, m)
            lines.append(f"- {label}策略：ROI {perf.roi_total:+.1f}% / 命中率 {perf.win_rate * 100:.1f}%")
        lines.append("")
        lines.append("## 汇总")
        lines.append(f"> {DISCLAIMER}")
        return "\n".join(lines)

    def export_markdown(self, path: str) -> str:
        """导出 Markdown。"""
        return MarkdownExporter.export(self.to_markdown(), path)

    def export_pdf(self, path: str) -> str:
        """导出 PDF。"""
        md = self.to_markdown()
        text_lines = [ln for ln in md.splitlines() if not ln.startswith("#")]
        return PDFExporter.export_report("Atlas 彩票量化分析报告", text_lines, path)

    def export_png(self, path: str) -> str:
        """导出 PNG 图表（评分/覆盖率/风险概览）。"""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # 中文字体（Windows 微软雅黑）
        for font in ("Microsoft YaHei", "SimHei", "SimSun"):
            try:
                plt.rcParams["font.sans-serif"] = [font]
                break
            except Exception:
                continue
        plt.rcParams["axes.unicode_minus"] = False
        d = self._collect()

        fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
        s, sim, rk = d["structure"], d["sim"], d["risk"]

        # 评分条
        ax = axes[0]
        ax.bar(["组合评分"], [s.total_score], color="#2a6df4")
        ax.set_ylim(0, 100)
        ax.set_title("组合评分")
        ax.text(0, s.total_score + 3, f"{s.total_score}", ha="center")

        # 覆盖率
        ax = axes[1]
        ax.bar(["覆盖率"], [sim.coverage_rate * 100], color="#6a4df4")
        ax.set_ylim(0, 100)
        ax.set_title("模拟覆盖率")
        ax.text(0, sim.coverage_rate * 100 + 3, f"{sim.coverage_rate * 100:.1f}%", ha="center")

        # 风险等级
        ax = axes[2]
        ax.bar(["风险等级"], [{"A": 1, "B": 2, "C": 3, "D": 4}[rk.risk_level]], color="#e58e2a")
        ax.set_ylim(0, 5)
        ax.set_title(f"资金风险等级 {rk.risk_level}")

        fig.suptitle("Atlas 彩票量化分析概览", fontsize=13)
        fig.tight_layout()
        from engine.export.png import PNGExporter
        return PNGExporter.export_figure(fig, path)


def generate_quant_report(tickets: List[dict], lottery: str = "dlt",
                          fmt: str = "md", path: Optional[str] = None) -> str:
    """便捷函数：生成并导出量化报告。

    fmt: md / pdf / png
    """
    gen = QuantReportGenerator(tickets, lottery)
    out = path or f"atlas_quant_report.{fmt}"
    if fmt == "pdf":
        return gen.export_pdf(out)
    if fmt == "png":
        return gen.export_png(out)
    return gen.export_markdown(out)
