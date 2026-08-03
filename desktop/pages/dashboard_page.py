"""Dashboard 数据看板页面"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)

from data_loader import load_draws, get_data_source, get_data_quality
from stats import front_frequency, hot_numbers, cold_numbers, front_sums
from engine.data_center_v2 import DrawRecord


def _card(title, value, subtitle=""):
    card = QFrame()
    card.setObjectName("metricCard")
    card.setStyleSheet(
        "QFrame#metricCard{background:white;border-radius:10px;border:1px solid #e8ecf2;}"
        "QLabel{background:transparent;}"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(2)
    t = QLabel(title)
    t.setStyleSheet("color:#8a94a6;font-size:12px;")
    v = QLabel(value)
    v.setStyleSheet("color:#1a1a2e;font-size:24px;font-weight:bold;")
    s = QLabel(subtitle)
    s.setStyleSheet("color:#aab3c0;font-size:12px;")
    lay.addWidget(t)
    lay.addWidget(v)
    lay.addWidget(s)
    return card


class DashboardPage(QWidget):
    """数据看板：指标卡片 + 最新开奖 + 冷热号。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draws = load_draws()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        header = QLabel("🎯 我的彩票")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        # v4.1 阶段1：我的彩票价值面板（3 秒看懂：票据/开奖/待兑/投入/中奖/ROI/预算）
        try:
            root.addWidget(self._value_panel())
        except Exception:
            pass

        # v4.1 阶段2：今日提醒（开奖/兑奖/未兑奖/追号）
        try:
            reminder_label = QLabel(self._today_reminder_text())
            reminder_label.setWordWrap(True)
            reminder_label.setStyleSheet(
                "background:#f0f7ff;border:1px solid #cfe4ff;border-radius:8px;"
                "padding:10px 12px;color:#1e3a8a;font-size:12px;line-height:1.7;")
            root.addWidget(reminder_label)
        except Exception:
            pass

        src = get_data_source("dlt")
        quality = get_data_quality("dlt")

        # 数据来源 + 可信等级（数据不足时高亮警告）
        if quality["sufficient"]:
            src_label = QLabel(f"数据来源：{src.note}（{quality['total']} 期 · {quality['date_from']} ~ {quality['date_to']}）")
            src_label.setStyleSheet("color:#8a94a6;font-size:12px;")
            trust_label = QLabel(f"✅ 数据可信等级 {quality['trust_level']}（{quality['trust_label']}）")
            trust_label.setStyleSheet("color:#2e9e5b;font-size:12px;font-weight:bold;")
        else:
            src_label = QLabel(f"数据来源：{src.note}（{quality['total']} 期）")
            src_label.setStyleSheet("color:#8a94a6;font-size:12px;")
            trust_label = QLabel(quality["message"])
            trust_label.setStyleSheet("color:#e34d3d;font-size:12px;font-weight:bold;")
        root.addWidget(src_label)
        root.addWidget(trust_label)

        # 每日智能摘要（v3.7.0 Phase 2）
        try:
            daily = self._daily_summary_text()
            if daily:
                daily_label = QLabel(daily)
                daily_label.setWordWrap(True)
                daily_label.setStyleSheet(
                    "background:#f8f9fd;border:1px solid #e8ecf2;border-radius:8px;"
                    "padding:10px 12px;color:#445;font-size:12px;line-height:1.6;"
                )
                root.addWidget(daily_label)
        except Exception:
            pass

        # 个人中心（v3.8.0 Phase 7）：价值分/研究等级/AI 建议/历史
        try:
            personal = self._personal_panel_text()
            if personal:
                p_label = QLabel(personal)
                p_label.setWordWrap(True)
                p_label.setStyleSheet(
                    "background:#eef4ff;border:1px solid #d8e4ff;border-radius:8px;"
                    "padding:10px 12px;color:#1e3a8a;font-size:12px;line-height:1.6;"
                )
                root.addWidget(p_label)
        except Exception:
            pass

        if not self.draws:
            tip = QLabel("暂无数据：请确认 data/raw/dlt_history.csv 或 dlt_2024_sample.csv 存在")
            tip.setStyleSheet("color:#888;font-size:14px;")
            root.addWidget(tip)
            return

        last = self.draws[-1]
        freq = front_frequency(self.draws)
        hot = hot_numbers(self.draws, 8)
        cold = cold_numbers(self.draws, 8)
        sums = front_sums(self.draws)

        # 指标卡片行
        grid = QHBoxLayout()
        grid.setSpacing(12)
        grid.addWidget(_card("总期数", str(len(self.draws)), "大乐透样本"))
        grid.addWidget(_card("最新期号", last.number, last.draw_date))
        grid.addWidget(_card("最新奖池", last.format_pool(), "滚存"))
        grid.addWidget(_card("平均和值", f"{sum(sums) / len(sums):.0f}", f"最新和值 {last.front_sum}"))
        grid.addWidget(_card("最高频号码", f"{hot[0][0]:02d}", f"出现 {hot[0][1]} 次"))
        root.addLayout(grid)

        # 最新开奖 + 冷热号
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(self._recent_table(), 3)
        row.addWidget(self._hotcold_panel(hot, cold), 2)
        root.addLayout(row, 1)

    # ---------- v4.1 阶段1：我的彩票价值面板 ----------
    def _value_metrics(self):
        """计算 7 个价值指标（票据/开奖/待兑/投入/中奖/ROI/预算）。"""
        from engine.ticket_system import TicketManager
        from engine.personal_review import PersonalReviewEngine
        from engine.budget_manager import BudgetPlanner
        from engine.ticket_system.schedule import LotterySchedule
        from datetime import date

        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        rv = PersonalReviewEngine.review(tickets)
        bp = BudgetPlanner()
        budget = bp.evaluate_tickets(tickets)

        today = date.today().isoformat()
        dlt_draw = LotterySchedule.is_draw_day("dlt", today)
        ssq_draw = LotterySchedule.is_draw_day("ssq", today)
        if dlt_draw and ssq_draw:
            draw_txt = "大乐透+双色球"
        elif dlt_draw:
            draw_txt = "大乐透"
        elif ssq_draw:
            draw_txt = "双色球"
        else:
            draw_txt = "无"

        # 待兑奖：draw_date 在今天或之后（尚未开奖）
        pending = 0
        for t in tickets:
            d = t.get("draw_date") or t.get("buy_date", "")
            if d and d >= today:
                pending += 1

        roi = f"{rv.roi * 100:+.0f}%" if rv.total_investment else "—"
        return [
            ("我的票据", f"{len(tickets)} 张"),
            ("今日开奖", draw_txt),
            ("待兑奖", f"{pending} 张"),
            ("累计投入", f"¥{rv.total_investment:,.0f}"),
            ("累计中奖", f"¥{rv.total_winnings:,.0f}"),
            ("ROI", roi),
            ("本月预算", f"{budget.month_ratio * 100:.0f}%"),
        ]

    def _value_headline(self, metrics, rv, budget):
        """价值面板顶部话术（动态）。

        优先级：无票据欢迎 > 开奖日 > 预算超支 > 预算预警 > 默认。
        """
        draw_txt = metrics[1][1]
        if rv.total_tickets == 0:
            return "👋 欢迎！输入你的第一注彩票，我来帮你管"
        if draw_txt != "无":
            return f"🎯 今天是开奖日（{draw_txt}），快去查你的彩票中没中！"
        if budget.month_over:
            return f"⚠️ 本月已超预算 ¥{budget.exceed_amount:,.0f}，建议控制投入"
        if budget.month_ratio > 0.8:
            return f"💳 本月预算已用 {budget.month_ratio * 100:.0f}%，请注意控制"
        return "📋 你的彩票管家：中奖早知道 · 花钱有数 · 行为有复盘"

    def _value_panel(self):
        """我的彩票价值面板（3 秒看懂个人价值）。"""
        from engine.ticket_system import TicketManager
        from engine.personal_review import PersonalReviewEngine
        from engine.budget_manager import BudgetPlanner

        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        rv = PersonalReviewEngine.review(tickets)
        bp = BudgetPlanner()
        budget = bp.evaluate_tickets(tickets)
        metrics = self._value_metrics()

        frame = QFrame()
        frame.setStyleSheet(
            "QFrame{background:#1e3a8a;border-radius:12px;}"
            "QLabel{background:transparent;color:white;}"
        )
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        headline = QLabel(self._value_headline(metrics, rv, budget))
        headline.setStyleSheet(
            "font-size:16px;font-weight:bold;color:white;background:transparent;")
        lay.addWidget(headline)

        row = QHBoxLayout()
        row.setSpacing(10)
        for title, value in metrics:
            c = QFrame()
            c.setStyleSheet(
                "QFrame{background:rgba(255,255,255,0.12);border-radius:8px;}"
                "QLabel{background:transparent;color:white;}")
            v = QVBoxLayout(c)
            v.setContentsMargins(12, 10, 12, 10)
            v.setSpacing(2)
            t = QLabel(title)
            t.setStyleSheet("color:rgba(255,255,255,0.8);font-size:11px;background:transparent;")
            vv = QLabel(value)
            vv.setStyleSheet("font-size:20px;font-weight:bold;background:transparent;")
            v.addWidget(t)
            v.addWidget(vv)
            row.addWidget(c)
        lay.addLayout(row)
        return frame

    def _today_reminder_text(self) -> str:
        """今日提醒（v4.1 阶段2）：开奖/兑奖/未兑奖/追号。"""
        from engine.ticket_system import TicketManager
        from engine.reminder_center import today_reminders
        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        r = today_reminders(tickets)
        return r.summary_text()

    def _personal_panel_text(self) -> str:
        """个人中心：价值分 / 研究等级 / AI 建议 / 历史（v3.8.0）。"""
        import os
        try:
            from engine.user_intelligence.v3 import UserIntelligenceV3, build_behavior_summary
            from engine.value_score import compute_value_score

            ui = UserIntelligenceV3()
            summary = build_behavior_summary(ui)
            score = compute_value_score(
                total_events=summary.total_events,
                active_days=summary.active_days,
                analysis_runs=summary.by_event.get("ANALYSIS_RUN", 0),
                backtest_runs=summary.by_event.get("BACKTEST_RUN", 0),
                exports=summary.by_event.get("REPORT_EXPORT", 0),
                feedback_count=summary.by_event.get("FEEDBACK_SEND", 0),
                strategy_saves=summary.by_event.get("STRATEGY_SAVE", 0),
            )
            # AI 建议（基于行为）
            suggestions = []
            if summary.by_event.get("BACKTEST_RUN", 0) == 0:
                suggestions.append("建议去回测中心体验一次策略回测")
            if summary.by_event.get("REPORT_EXPORT", 0) == 0:
                suggestions.append("试试导出第一份报告（MD/PDF）")
            if summary.by_event.get("ANALYSIS_RUN", 0) < 3:
                suggestions.append("多看几次数据分析，掌握冷热号分布")
            if not suggestions:
                suggestions.append("使用熟练！可尝试更多策略对比")
            # 历史
            hist_dir = os.path.join(os.path.expanduser("~"), ".atlas", "history")
            hist_count = len([f for f in os.listdir(hist_dir) if f.endswith(".json")]) if os.path.isdir(hist_dir) else 0
            lines = [
                f"👤 个人中心 · 价值分 {score.total:.0f}/100 · 研究等级：{score.level}",
                f"· 使用 {score.usage_score:.0f} · 留存 {score.retention_score:.0f} · 研究 {score.research_score:.0f} · "
                f"产出 {score.export_score:.0f} · 反馈 {score.feedback_score:.0f}",
                f"· 历史报告 {hist_count} 份",
            ]
            for s in suggestions:
                lines.append(f"· 💡 {s}")
            return "\n".join(lines)
        except Exception:
            return ""

    def _daily_summary_text(self) -> str:
        """每日智能摘要：对比上次快照与当前数据。"""
        import json
        import os
        from datetime import datetime
        from engine.daily_intelligence import build_summary

        snap_dir = os.path.join(os.path.expanduser("~"), ".atlas")
        snap_path = os.path.join(snap_dir, "daily_snapshot.json")
        prev_draws = []
        if os.path.exists(snap_path):
            try:
                with open(snap_path, encoding="utf-8") as f:
                    prev = json.load(f)
                prev_draws = [
                    DrawRecord(str(d.get("number", "")), d.get("date", ""),
                               d.get("front", []), d.get("back", []), 0)
                    for d in prev if d.get("number")
                ]
            except (json.JSONDecodeError, OSError):
                prev_draws = []
        s = build_summary(prev_draws, self.draws, datetime.now().strftime("%Y-%m-%d"))
        # 更新快照（保留最近 30 期作为对比基线）
        try:
            os.makedirs(snap_dir, exist_ok=True)
            with open(snap_path, "w", encoding="utf-8") as f:
                json.dump([
                    {"number": d.number, "date": d.draw_date, "front": d.front, "back": d.back}
                    for d in self.draws[-30:]
                ], f, ensure_ascii=False)
        except OSError:
            pass
        return s.to_text()

    def _recent_table(self):
        box = QFrame()
        box.setStyleSheet("QFrame{background:white;border-radius:10px;border:1px solid #e8ecf2;}")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        title = QLabel("最近开奖")
        title.setStyleSheet("font-size:15px;font-weight:bold;color:#1a1a2e;")
        lay.addWidget(title)

        recent = self.draws[-6:]
        table = QTableWidget(len(recent), 5)
        table.setHorizontalHeaderLabels(["期号", "日期", "前区", "后区", "奖池"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        h = table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QHeaderView.Stretch)
        h.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        for i, d in enumerate(recent):
            for j, val in enumerate([d.number, d.draw_date, d.format_front(), d.format_back(), d.format_pool()]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(0x0004 | 0x0080)  # AlignHCenter | AlignVCenter
                table.setItem(i, j, item)
        table.setStyleSheet(
            "QTableWidget{font-size:13px;border:none;}"
            "QHeaderView::section{background:#f4f6fa;border:none;padding:6px;font-weight:bold;}"
        )
        lay.addWidget(table)
        return box

    def _hotcold_panel(self, hot, cold):
        box = QFrame()
        box.setStyleSheet("QFrame{background:white;border-radius:10px;border:1px solid #e8ecf2;}")
        lay = QVBoxLayout(box)
        lay.setContentsMargins(14, 12, 14, 12)
        title = QLabel("冷热号 TOP8")
        title.setStyleSheet("font-size:15px;font-weight:bold;color:#1a1a2e;")
        lay.addWidget(title)

        hot_txt = "  ".join(f"{n:02d}" for n, _ in hot)
        cold_txt = "  ".join(f"{n:02d}" for n, _ in cold)
        h1 = QLabel("🔥 热号"); h1.setStyleSheet("color:#e34d3d;font-weight:bold;font-size:13px;")
        hv = QLabel(hot_txt); hv.setStyleSheet("font-size:15px;letter-spacing:2px;")
        c1 = QLabel("🧊 冷号"); c1.setStyleSheet("color:#2a6df4;font-weight:bold;font-size:13px;")
        cv = QLabel(cold_txt); cv.setStyleSheet("font-size:15px;letter-spacing:2px;")
        note = QLabel("基于前区号码出现频率统计")
        note.setStyleSheet("color:#aab3c0;font-size:12px;")
        for w in (h1, hv, c1, cv):
            lay.addWidget(w)
        lay.addStretch()
        lay.addWidget(note)
        return box
