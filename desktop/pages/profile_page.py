"""个人中心页面（v4.0.0 Phase 6）。

展示：我的票据 / 我的投入 / 我的中奖 / 我的风险 / 我的报告 / 我的趋势。
桌面必须可见。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox,
)

from data_loader import load_draws


class ProfilePage(QWidget):
    """个人中心：个人决策智能面板。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        header = QLabel("👤 个人中心")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        sub = QLabel("我的票据 · 投入 · 中奖 · 风险 · 报告 · 趋势")
        sub.setStyleSheet("color:#666;font-size:12px;")
        root.addWidget(sub)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        refresh = QPushButton("🔄 刷新")
        refresh.setStyleSheet(
            "QPushButton{background:#2a6df4;color:white;border:none;padding:8px 16px;border-radius:6px;}"
        )
        refresh.clicked.connect(self._refresh)
        btn_row.addWidget(refresh)

        # v4.2 Phase 4：导出年度报告 PDF
        export_btn = QPushButton("📄 导出年度报告")
        export_btn.setStyleSheet(
            "QPushButton{background:#e8f5e9;color:#2e7d32;border:1px solid #a5d6a7;"
            "padding:8px 16px;border-radius:6px;}"
        )
        export_btn.clicked.connect(self._export_annual)
        btn_row.addWidget(export_btn)
        root.addLayout(btn_row)

        # 统计卡片区（我的票据/投入/中奖/风险）
        cards = QHBoxLayout()
        cards.setSpacing(10)
        self.ticket_card = self._card("我的票据")
        self.spend_card = self._card("我的投入")
        self.win_card = self._card("我的中奖")
        self.risk_card = self._card("我的风险")
        for c in (self.ticket_card, self.spend_card, self.win_card, self.risk_card):
            cards.addWidget(c)
        root.addLayout(cards)

        # v4.2 Phase 1：我的彩票档案（累计购买/中奖/次数/最高奖金/周期/常购彩种）
        self.archive_area = QLabel("档案加载中…")
        self.archive_area.setWordWrap(True)
        self.archive_area.setStyleSheet(
            "background:#f0f7ff;border:1px solid #cfe4ff;border-radius:8px;"
            "padding:10px 12px;color:#1e3a8a;font-size:12px;line-height:1.7;")
        root.addWidget(self.archive_area)

        # v4.3 P3：彩票资产中心（累计购买/中奖/净收益/中奖率/风险等级 + 风险提示）
        self.asset_area = QLabel("资产加载中…")
        self.asset_area.setWordWrap(True)
        self.asset_area.setStyleSheet(
            "background:#fff3f0;border:1px solid #ffd0c4;border-radius:8px;"
            "padding:10px 12px;color:#7a1f0d;font-size:12px;line-height:1.7;")
        root.addWidget(self.asset_area)

        # v4.2 Phase 5：Atlas Premium 会员状态
        self.premium_area = QLabel("会员加载中…")
        self.premium_area.setWordWrap(True)
        self.premium_area.setStyleSheet(
            "background:#fdf3e7;border:1px solid #f0d9b8;border-radius:8px;"
            "padding:10px 12px;color:#7a4a12;font-size:12px;line-height:1.7;")
        root.addWidget(self.premium_area)

        # 我的报告 + 趋势
        row = QHBoxLayout()
        row.setSpacing(10)
        self.report_area = QLabel("报告加载中…")
        self.report_area.setWordWrap(True)
        self.report_area.setStyleSheet(
            "background:white;border-radius:8px;border:1px solid #e8ecf2;padding:10px;color:#445;font-size:12px;")
        row.addWidget(self.report_area, 1)

        self.trend_area = QLabel("趋势加载中…")
        self.trend_area.setWordWrap(True)
        self.trend_area.setStyleSheet(
            "background:white;border-radius:8px;border:1px solid #e8ecf2;padding:10px;color:#445;font-size:12px;")
        row.addWidget(self.trend_area, 1)
        root.addLayout(row, 1)

        # 个人成长（v4.1 阶段4）
        self.growth_area = QLabel("成长加载中…")
        self.growth_area.setWordWrap(True)
        self.growth_area.setStyleSheet(
            "background:#f4f8ff;border:1px solid #d8e4ff;border-radius:8px;padding:10px;color:#1e3a8a;font-size:12px;")
        root.addWidget(self.growth_area)

        self.disclaimer = QLabel("⚠️ 彩票开奖结果具有随机性。本中心帮助你了解投注行为并管理风险，不涉及预测。")
        self.disclaimer.setWordWrap(True)
        self.disclaimer.setStyleSheet("color:#8a6d1a;font-size:11px;")
        root.addWidget(self.disclaimer)

        self._refresh()

    def _card(self, title):
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame{background:white;border-radius:8px;border:1px solid #e8ecf2;padding:8px;}")
        v = QVBoxLayout(frame)
        v.setContentsMargins(8, 8, 8, 8)
        label = QLabel(title)
        label.setStyleSheet("font-weight:bold;font-size:12px;color:#1a1a2e;")
        value = QLabel("—")
        value.setStyleSheet("font-size:18px;font-weight:bold;color:#2a6df4;")
        v.addWidget(label)
        v.addWidget(value)
        frame.value_label = value
        return frame

    def _export_annual(self) -> None:
        """v4.2 Phase 4：导出年度报告 PDF。"""
        try:
            from engine.annual_report import AnnualReportEngine
            from datetime import date
            year = date.today().year
            rep = AnnualReportEngine.build_from_manager(year)
            if rep.ticket_count == 0:
                QMessageBox.information(self, "导出年度报告", f"{year} 年暂无购彩记录，先保存几注彩票吧。")
                return
            default = f"Atlas_{year}_年度报告.pdf"
            path, _ = QFileDialog.getSaveFileName(self, "保存年度报告", default, "PDF 文件 (*.pdf)")
            if not path:
                return
            out = rep.export_pdf(path)
            QMessageBox.information(self, "导出成功", f"年度报告已保存：\n{out}")
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "导出失败", f"{e}")

    def _refresh(self):
        """刷新个人数据。"""
        try:
            from engine.ticket_system import TicketManager
            from engine.user_behavior import analyze_behavior
            from engine.personal_review import PersonalReviewEngine
            from engine.budget_manager import BudgetPlanner
            from engine.user_archive import UserArchiveEngine

            tm = TicketManager()
            tickets = [t.__dict__ for t in tm.list_all()]

            # 我的票据
            self.ticket_card.value_label.setText(str(len(tickets)))

            # v4.2 Phase 1：我的彩票档案
            try:
                arch = UserArchiveEngine.build_from_manager(tm)
                self.archive_area.setText(arch.summary_text())
            except Exception:
                self.archive_area.setText("档案加载中…")

            # v4.3 P3：彩票资产中心（含风险提示）
            try:
                from engine.asset_center import AssetCenter
                rep = AssetCenter.build(tickets)
                txt = rep.summary_text()
                if tickets:
                    txt += "\n" + AssetCenter.risk_line(rep)
                self.asset_area.setText(txt)
            except Exception:
                self.asset_area.setText("资产加载中…")

            # v4.2 Phase 5：Atlas Premium 会员状态
            try:
                from engine.premium import PremiumManager, PremiumPlan
                pm = PremiumManager()
                tier = pm.get_tier()
                tier_name = PremiumPlan.tier_name(tier)
                if pm.is_premium():
                    prem_txt = f"👑 {tier_name} · 已解锁：自动提醒/无限历史/年度报告/高级复盘"
                else:
                    locked = [f.name for f in PremiumPlan.features_for("premium")]
                    prem_txt = (f"💎 {tier_name} · 会员可解锁：{'、'.join(locked)}\n"
                                f"（会员只解锁数据服务，不包含任何预测功能）")
                self.premium_area.setText(prem_txt)
            except Exception:
                pass

            if not tickets:
                self.spend_card.value_label.setText("¥0")
                self.win_card.value_label.setText("¥0")
                self.risk_card.value_label.setText("—")
                self.report_area.setText("暂无投注数据。请到「工作台」添加票据后查看个人分析。")
                self.trend_area.setText("暂无趋势数据。")
                return

            # 我的投入 / 行为
            bh = analyze_behavior(tickets)
            self.spend_card.value_label.setText(f"¥{bh.total_spent:,.0f}")
            self.risk_card.value_label.setText(bh.risk_level)

            # 我的中奖 / 复盘
            rv = PersonalReviewEngine.review(tickets)
            self.win_card.value_label.setText(f"¥{rv.total_winnings:,.0f}")

            # 我的报告
            self.report_area.setText(
                f"📋 复盘报告\n"
                f"· 总投入：¥{rv.total_investment:,.0f}\n"
                f"· 总中奖：¥{rv.total_winnings:,.0f}\n"
                f"· 净收益：¥{rv.net_profit:,.0f}\n"
                f"· 中奖率：{rv.win_rate * 100:.1f}%\n"
                f"· 最高投入：{rv.peak_month or '—'}"
            )

            # 我的趋势
            trend = "📈 月度投入趋势\n"
            if bh.monthly_avg:
                trend += f"· 月均投入：¥{bh.monthly_avg:,.0f}\n"
                trend += f"· 年投入外推：¥{bh.annual_projection:,.0f}\n"
                trend += f"· 追号次数：{bh.chase_count}\n"
                trend += f"· 高频月份：{bh.peak_month}\n"
                trend += f"· 行为风险等级：{bh.risk_level}"
            else:
                trend += "· 暂无足够日期数据"
            self.trend_area.setText(trend)

            # 预算健康
            try:
                bp = BudgetPlanner()
                b = bp.evaluate_tickets(tickets)
                self.report_area.setText(self.report_area.text() + f"\n· 预算健康度：{b.health_score}/100")
            except Exception:
                pass

            # 个人成长（v4.1 阶段4）+ v4.2 Phase 3 购彩健康指数
            try:
                from engine.personal_growth import growth_report
                g = growth_report(tickets)
                lines = [f"🌱 个人成长\n· 购彩记录：{g.total_days} 天"
                         f"\n· 当前连续购买：{g.current_streak} 天 / 最长 {g.max_streak} 天"
                         f"\n· 连续中奖：{g.consecutive_wins} 期"]
                try:
                    from engine.growth_health import GrowthHealthEngine
                    h = GrowthHealthEngine.evaluate(tickets)
                    lines.append(f"\n· 购彩健康指数：{h.level_text}（{h.overall_score}/100）")
                    for d in h.dimensions:
                        lines.append(f"  - {d.name}：{d.score}/100")
                except Exception:
                    pass
                # v4.3 P4：Atlas 使用成长（真实事件驱动）
                try:
                    from engine.growth_system import GrowthEngine
                    g2 = GrowthEngine.build()
                    lines.append(
                        f"\n· Atlas 使用：保存 {g2.tickets_saved} 次 · 兑奖 {g2.claims_completed} 次 · "
                        f"报告 {g2.reports_viewed} 次\n"
                        f"· 连续使用 {g2.streak_weeks} 周 · 成长等级 {g2.level}")
                except Exception:
                    pass
                self.growth_area.setText("\n".join(lines))
            except Exception:
                pass
        except Exception as e:  # noqa: BLE001
            self.report_area.setText(f"加载失败：{e}")
