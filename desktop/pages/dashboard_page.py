"""Dashboard 数据看板页面"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea,
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
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._build()

    def refresh(self) -> None:
        """重新加载数据并重建看板（新增票据 / 切换页面时调用，保证数据实时）。"""
        try:
            self.draws = load_draws()
        except Exception:
            pass
        while self._outer.count():
            item = self._outer.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._build()

    def _build(self):
        # v4.2 UI 优化：可滚动容器，内容多时滚动查看，避免拥挤
        outer = self._outer
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{width:8px;background:#f0f2f5;border-radius:4px;}"
            "QScrollBar::handle:vertical{background:#c3cbd6;border-radius:4px;min-height:30px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}"
        )
        container = QWidget()
        container.setStyleSheet("background:transparent;")
        outer.addWidget(scroll)
        scroll.setWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

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

        # v4.3 P2：我的待兑奖列表（4 状态机：等待开奖/已开奖待查看/已查看/已兑奖）
        try:
            from engine.claim_center import ClaimCenter
            from engine.ticket_system import TicketManager
            tks = [t.__dict__ for t in TicketManager().list_all()]
            pending = ClaimCenter.pending_text(tks)
            if tks:
                p_label = QLabel("🧾 " + pending)
                p_label.setWordWrap(True)
                p_label.setStyleSheet(
                    "background:#fff8ec;border:1px solid #ffe0b2;border-radius:8px;"
                    "padding:10px 12px;color:#7a4a00;font-size:12px;line-height:1.7;")
                root.addWidget(p_label)
        except Exception:
            pass

        # v4.4 P5：开奖状态卡片（距离下一开奖 / 最新开奖 / 数据可信 / 待兑奖票据）
        try:
            status_card = self._draw_status_card()
            if status_card:
                root.addWidget(status_card)
        except Exception:
            pass

        # v4.6 P4：自动兑奖汇总卡片（待开奖/已中奖/待领取，点击进报告）
        try:
            summary = self._claim_summary()
            if summary:
                root.addWidget(self._claim_summary_card(summary))
        except Exception:
            pass

        # v4.1.1 Phase 3：首次引导（无票据时）
        try:
            from engine.ticket_system import TicketManager
            if TicketManager().count() == 0:
                guide = QLabel(
                    "🆕 首次使用引导（30 秒完成价值体验）：\n"
                    "① 在 AI 助手输入你的彩票号码，或到「工作台」保存第一张彩票\n"
                    "② 开奖后 Atlas 会主动提醒你，自动帮你算中没中\n"
                    "③ 保存越多，预算/复盘/年度报告越准\n\n"
                    "💡 无需任何配置，直接开始即可。")
                guide.setWordWrap(True)
                guide.setStyleSheet(
                    "background:#e8f5e9;border:1px solid #c8e6c9;border-radius:8px;"
                    "padding:12px 14px;color:#2e7d32;font-size:13px;line-height:1.7;")
                root.addWidget(guide)
        except Exception:
            pass

        src = get_data_source("dlt")
        quality = get_data_quality("dlt")

        # 数据来源 + 可信等级（合并一行，减少垂直占用）
        src_row = QHBoxLayout()
        src_row.setSpacing(8)
        if quality["sufficient"]:
            src_label = QLabel(f"数据：{src.note} · {quality['total']} 期（{quality['date_from']}~{quality['date_to']}）")
            src_label.setStyleSheet("color:#8a94a6;font-size:11px;")
            trust_label = QLabel(f"✅ 可信 {quality['trust_level']} {quality['trust_label']}")
            trust_label.setStyleSheet("color:#2e9e5b;font-size:11px;font-weight:bold;")
        else:
            src_label = QLabel(f"数据：{src.note} · {quality['total']} 期")
            src_label.setStyleSheet("color:#8a94a6;font-size:11px;")
            trust_label = QLabel(quality["message"])
            trust_label.setStyleSheet("color:#e34d3d;font-size:11px;font-weight:bold;")
        src_row.addWidget(src_label)
        src_row.addWidget(trust_label)
        src_row.addStretch()
        root.addLayout(src_row)

        # v4.3 P5：每日智能摘要（含平均和值/奇偶比等研究指标）已从首页移除，移至「数据分析」研究中心

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

        # 数据概览（3 秒价值已由上方「我的彩票」价值面板承载；此处仅保留开奖数据源透明）
        grid = QHBoxLayout()
        grid.setSpacing(12)
        grid.addWidget(_card("总期数", str(len(self.draws)), "大乐透样本"))
        grid.addWidget(_card("最新期号", last.number, last.draw_date))
        grid.addWidget(_card("最新奖池", last.format_pool(), "滚存"))
        root.addLayout(grid)

        # v4.3 P5：首页重构第二版 —— 最近开奖表保留，研究指标（平均和值/奇偶/冷热）移入「数据分析」页
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(self._recent_table(), 3)
        study = QLabel("📊 研究分析\n（号码频率 · 分布统计 · 区间规律）\n请到「数据分析」页查看")
        study.setWordWrap(True)
        study.setStyleSheet(
            "background:#f4f6fa;border:1px dashed #d8dee9;border-radius:8px;"
            "padding:12px;color:#8a94a6;font-size:12px;line-height:1.7;")
        row.addWidget(study, 2)
        root.addLayout(row, 1)

    # ---------- v4.1.1 Phase 2：我的彩票价值面板（6 项个人价值）----------
    def _value_metrics(self):
        """计算价值指标（v4.1.1：票/最近开奖/待兑奖/本月投入/本月结果/状态）。"""
        from engine.ticket_system import TicketManager
        from engine.personal_review import PersonalReviewEngine
        from engine.budget_manager import BudgetPlanner
        from engine.reminder_center import today_reminders
        from datetime import date

        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        rv = PersonalReviewEngine.review(tickets)
        bp = BudgetPlanner()
        budget = bp.evaluate_tickets(tickets)
        reminder = today_reminders(tickets)

        # 最近开奖（今晚）
        draw_txt = "今晚" + ("、".join(reminder.draw_today)) if reminder.draw_today else "无"

        # 待兑奖：状态机 ready_claim + 今日可兑
        ready = reminder.ticket_status["ready_claim"] + reminder.prize_due

        # 本月投入/中奖（budget 本月 + 本月中奖估算）
        month_spent = budget.month_spent
        month_won = 0.0
        today = date.today()
        for t in tickets:
            d = t.get("draw_date") or ""
            if d.startswith(f"{today.year}-{today.month:02d}"):
                try:
                    from engine.lottery_intent.draw_matcher import DrawResultMatcher
                    from engine.lottery_intent.prize_calculator import PrizeCalculator
                    match = DrawResultMatcher().match(t.get("front", []), t.get("back", []),
                                                     lottery=t.get("lottery", "dlt"),
                                                     draw_date=d)
                    if match.draw:
                        pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, t.get("lottery", "dlt"))
                        month_won += pr.amount
                except Exception:
                    pass

        # 我的状态
        if budget.warning_level == "超支" or reminder.chase_notes:
            state = "需关注"
        elif budget.warning_level == "预警":
            state = "理性购彩"
        else:
            state = "理性购彩"

        return [
            ("🎫 我的票", f"{len(tickets)} 张"),
            ("⏰ 最近开奖", draw_txt),
            ("💰 待兑奖", f"{ready} 张"),
            ("📊 本月投入", f"¥{month_spent:,.0f}"),
            ("📈 本月结果", f"中奖 ¥{month_won:,.0f}"),
            ("🎯 我的状态", state),
        ]

    def _value_headline(self, metrics, rv, budget):
        """价值面板顶部话术（v4.1.1：动态，含 30 天中奖/上月对比）。"""
        from datetime import date, timedelta
        from engine.ticket_system import TicketManager
        from engine.personal_review import PersonalReviewEngine

        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        if not tickets:
            return "👋 欢迎！输入你的第一注彩票，我来帮你管"

        draw_txt = metrics[1][1]
        # 动态话术库
        dynamic = []
        # 待兑奖
        ready = int(metrics[2][1].split()[0])
        if ready > 0:
            dynamic.append(f"你有 {ready} 张彩票等待开奖/兑奖")
        # 本月投入对比上月
        today = date.today()
        last_month = (today.replace(day=1) - timedelta(days=1))
        last_key = f"{last_month.year}-{last_month.month:02d}"
        cur_key = f"{today.year}-{today.month:02d}"
        cur_spent = sum(t.get("cost", 2.0) for t in tickets
                        if (t.get("buy_date") or "").startswith(cur_key))
        last_spent = sum(t.get("cost", 2.0) for t in tickets
                         if (t.get("buy_date") or "").startswith(last_key))
        if last_spent > 0 and cur_spent < last_spent:
            pct = int((1 - cur_spent / last_spent) * 100)
            dynamic.append(f"本月投入比上月减少 {pct}%")
        elif last_spent > 0 and cur_spent > last_spent:
            pct = int((cur_spent / last_spent - 1) * 100)
            dynamic.append(f"本月投入比上月增加 {pct}%，请注意")
        # 30 天中奖次数
        win30 = 0
        cutoff = (today - timedelta(days=30)).isoformat()
        for t in tickets:
            d = t.get("draw_date") or ""
            if d and d >= cutoff:
                try:
                    from engine.lottery_intent.draw_matcher import DrawResultMatcher
                    from engine.lottery_intent.prize_calculator import PrizeCalculator
                    match = DrawResultMatcher().match(t.get("front", []), t.get("back", []),
                                                     lottery=t.get("lottery", "dlt"), draw_date=d)
                    if match.draw and PrizeCalculator.calculate(match.front_hits, match.back_hits, t.get("lottery", "dlt")).won:
                        win30 += 1
                except Exception:
                    pass
        if win30 > 0:
            dynamic.append(f"过去 30 天中奖 {win30} 次")

        if dynamic:
            return " · ".join(dynamic[:2])

        if draw_txt.startswith("今晚"):
            return f"🎯 {draw_txt}开奖，快去查你的彩票中没中！"
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

    def _claim_summary(self) -> dict:
        """v4.6 P4：自动兑奖汇总（待开奖/已中奖/待领取金额）。"""
        from engine.ticket_system import TicketManager
        from engine.claim_center import ClaimCenter
        from datetime import date

        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        today = date.today().isoformat()

        items = ClaimCenter.build_items(tickets)
        waiting = sum(1 for it in items if it.status == "waiting_draw")
        # 已中奖：已开奖票据匹配中奖
        won_count = 0
        pending_amount = 0.0
        for it in items:
            if it.status in ("settled_unviewed", "viewed"):
                try:
                    from engine.lottery_intent.draw_matcher import DrawResultMatcher
                    from engine.lottery_intent.prize_calculator import PrizeCalculator
                    match = DrawResultMatcher().match(it.front, it.back,
                                                     lottery=it.lottery,
                                                     draw_date=it.draw_date)
                    if match.draw:
                        pr = PrizeCalculator.calculate(match.front_hits, match.back_hits, it.lottery)
                        if pr.won:
                            won_count += 1
                            if it.status == "settled_unviewed":
                                pending_amount += pr.amount
                except Exception:
                    pass
        return {"waiting": waiting, "won": won_count,
                "pending_amount": pending_amount}

    def _claim_summary_card(self, summary: dict):
        """v4.6 P4：兑奖汇总卡片（待开奖/已中奖/待领取）。"""
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame{background:#e8f5e9;border:1px solid #c8e6c9;border-radius:10px;}"
            "QLabel{background:transparent;}")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)
        title = QLabel("🎯 今日兑奖")
        title.setStyleSheet("font-size:14px;font-weight:bold;color:#1a1a2e;")
        lay.addWidget(title)
        for line in (
            f"🎫 待开奖：{summary['waiting']} 张",
            f"🎉 已中奖：{summary['won']} 张",
            f"💰 待领取：¥{summary['pending_amount']:,.0f}",
        ):
            lbl = QLabel(line)
            lbl.setStyleSheet("color:#2e7d32;font-size:13px;line-height:1.6;")
            lay.addWidget(lbl)
        return frame

    def _today_reminder_text(self) -> str:
        """今日提醒（v4.1 阶段2）：开奖/兑奖/未兑奖/追号。"""
        from engine.ticket_system import TicketManager
        from engine.reminder_center import today_reminders
        tm = TicketManager()
        tickets = [t.__dict__ for t in tm.list_all()]
        r = today_reminders(tickets)
        return r.summary_text()

    def _draw_status_card(self):
        """v4.4 P5：开奖状态卡片（距离下一开奖 / 最新开奖 / 数据可信 / 待兑奖）。"""
        from datetime import date
        from engine.ticket_system.schedule import LotterySchedule
        from engine.live_draw.health import DataHealthCenter
        from engine.claim_center import ClaimCenter
        from engine.ticket_system import TicketManager

        today = date.today().isoformat()
        # 下一开奖
        next_dlt = LotterySchedule.next_draw_date("dlt", today)
        next_ssq = LotterySchedule.next_draw_date("ssq", today)
        # 数据可信（v4.9 P2：明确 🟢/🟡 状态 + 更新时间 + 来源 + 失败原因，不伪装实时）
        try:
            h = DataHealthCenter.check("dlt")
            status_icon = "🟢" if h.level == "A" else ("🟡" if h.level in ("B", "C") else "🔴")
            if h.level == "D":
                health_txt = (f"{status_icon} 数据可信 D 级：数据异常（暂未更新）· 最后可信数据：{h.draw_date or '—'}"
                              f" · 原因：{h.message}")
            else:
                health_txt = (f"{status_icon} 数据可信 {h.level} 级 {h.message} · 最新期 {h.latest_issue}（{h.draw_date}）"
                              f" · 更新时间 {h.updated_at or '—'} · 来源 {h.source}")
        except Exception:
            health_txt = "🟡 数据可信：状态未知"
        # 待兑奖
        tm = TicketManager()
        tks = [t.__dict__ for t in tm.list_all()]
        try:
            pending = ClaimCenter.pending_list(tks)
            pending_txt = f"待兑奖 {len(pending)} 张"
        except Exception:
            pending_txt = "待兑奖 0 张"

        frame = QFrame()
        frame.setStyleSheet(
            "QFrame{background:#f4f8ff;border:1px solid #d6e4ff;border-radius:10px;}"
            "QLabel{background:transparent;}")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)
        title = QLabel("📡 开奖状态")
        title.setStyleSheet("font-size:14px;font-weight:bold;color:#1a1a2e;")
        lay.addWidget(title)

        # v4.9.1 修复：最新开奖号码醒目展示（彩色球 + 大字号）
        try:
            if self.draws:
                latest = self.draws[-1]
                front_html = "".join(
                    f'<span style="background:#2b6cb0;color:#fff;border-radius:50%;'
                    f'padding:5px 10px;margin:2px;font-size:16px;font-weight:bold;'
                    f'display:inline-block;">{n:02d}</span>' for n in latest.front)
                back_html = "".join(
                    f'<span style="background:#e53e3e;color:#fff;border-radius:50%;'
                    f'padding:5px 10px;margin:2px;font-size:16px;font-weight:bold;'
                    f'display:inline-block;">{n:02d}</span>' for n in latest.back)
                latest_label = QLabel(
                    f'<div style="text-align:center;padding:4px;">'
                    f'<span style="font-size:12px;color:#666;">🎯 最新开奖 '
                    f'{getattr(latest, "number", "")}（{getattr(latest, "draw_date", "")}）</span><br>'
                    f'{front_html} <span style="color:#999;font-size:16px;">+</span> {back_html}</div>')
                latest_label.setStyleSheet(
                    "background:#ffffff;border:1px solid #d6e4ff;border-radius:10px;padding:8px;")
                lay.addWidget(latest_label)
        except Exception:
            pass

        for line in (
            f"⏳ 距离下一开奖：大乐透 {next_dlt or '—'} · 双色球 {next_ssq or '—'}",
            f"🩺 {health_txt}",
            f"🎯 {pending_txt}",
        ):
            lbl = QLabel(line)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color:#445;font-size:12px;line-height:1.6;")
            lay.addWidget(lbl)
        return frame

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
