"""Atlas 首次使用引导对话框。

三步极简引导（目标：30 秒完成第一次分析）：
  1. 用途选择  → 你想用 Atlas 做什么？
  2. 数据选择  → 关注哪个彩种？（展示当前数据量）
  3. 分析模式  → 立即开始哪种分析？

完成后保存档案，并携带选择结果（purpose / lottery / mode）
供主窗口跳转到对应页面。
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
    QStackedWidget, QWidget,
)

from user_profile import UserProfile, save_profile
from data_loader import get_data_quality


class _OptionCard(QPushButton):
    """可选中的选项卡片按钮。"""

    def __init__(self, title: str, desc: str = ""):
        super().__init__()
        self.setCheckable(True)
        self.setCursor(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.PointingHandCursor)
        text = title
        if desc:
            text += f"\n{desc}"
        self.setText(text)
        self.setStyleSheet(
            "QPushButton{background:white;border:2px solid #e8ecf2;border-radius:10px;"
            "padding:12px 14px;text-align:left;font-size:13px;color:#333;}"
            "QPushButton:hover{border-color:#2a6df4;}"
            "QPushButton:checked{background:#eef4ff;border-color:#2a6df4;color:#1e56c8;font-weight:bold;}"
        )


class FirstRunDialog(QDialog):
    """首次运行三步引导向导。"""

    def __init__(self, profile: UserProfile, parent=None):
        super().__init__(parent)
        self._profile = profile
        self.purpose = "dashboard"    # dashboard / backtest / reports
        self.lottery = "dlt"          # dlt / ssq
        self.mode = "quick"           # quick / backtest
        self._completed = False
        self.setWindowTitle("欢迎使用 Atlas Quant Platform")
        self.setFixedSize(560, 460)
        # v4.6 P3：onboarding_start 事件
        try:
            from engine.user_analytics import AnalyticsTracker
            AnalyticsTracker().record("app_opened", metadata={"onboarding": "start"})
        except Exception:
            pass
        self._build()
        self._go(0)

    def reject(self):
        """用户关闭引导（未完成）→ onboarding_drop。"""
        if not self._completed:
            try:
                from engine.user_analytics import AnalyticsTracker
                AnalyticsTracker().record("export_clicked", metadata={"onboarding": "drop"})
            except Exception:
                pass
        super().reject()

    # ---- 界面构建 ----
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(12)

        self.step_label = QLabel()
        self.step_label.setStyleSheet("color:#8a94a6;font-size:12px;")
        root.addWidget(self.step_label)

        self.title = QLabel()
        self.title.setStyleSheet("font-size:20px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(self.title)

        # 步骤内容容器
        self.stack = QStackedWidget()
        self.stack.addWidget(self._step_purpose())
        self.stack.addWidget(self._step_lottery())
        self.stack.addWidget(self._step_mode())
        root.addWidget(self.stack, 1)

        # 底部导航
        nav = QHBoxLayout()
        nav.setSpacing(10)
        self.prev_btn = QPushButton("← 上一步")
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(lambda: self._go(self._step - 1))
        self.next_btn = QPushButton("下一步 →")
        self.next_btn.clicked.connect(self._next)
        for b in (self.prev_btn, self.next_btn):
            b.setStyleSheet(
                "QPushButton{background:#2a6df4;color:white;border:none;padding:9px 18px;"
                "border-radius:8px;font-size:13px;font-weight:bold;}"
                "QPushButton:hover{background:#1e56c8;}"
                "QPushButton:disabled{background:#c7cfdd;}"
            )
        self.next_btn.setMinimumWidth(120)
        nav.addWidget(self.prev_btn)
        nav.addStretch()
        nav.addWidget(self.next_btn)
        root.addLayout(nav)

    def _make_group(self, options: list) -> QButtonGroup:
        group = QButtonGroup(self)
        group.setExclusive(True)
        for key, title, desc in options:
            card = _OptionCard(title, desc)
            card.clicked.connect(lambda _=False, k=key: setattr(self, "_last_key", k))
            group.addButton(card)
            group.setId(card, len(options) and 0)  # placeholder
        return group

    def _step_purpose(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        lay.addWidget(QLabel("你想用 Atlas 做什么？"))
        self._purpose_group = self._make_group([
            ("dashboard", "📊 快速看数据", "频率 / 冷热号 / 和值走势"),
            ("backtest", "📉 回测验证策略", "历史数据上检验策略表现"),
            ("reports", "📄 生成研究报告", "一键统计报告与推荐"),
        ])
        for b in self._purpose_group.buttons():
            lay.addWidget(b)
        lay.addStretch()
        return w

    def _step_lottery(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        lay.addWidget(QLabel("关注哪个彩种？"))
        self._lottery_group = self._make_group([
            ("dlt", "🎯 大乐透", self._lottery_hint("dlt")),
            ("ssq", "🔴 双色球", self._lottery_hint("ssq")),
        ])
        for b in self._lottery_group.buttons():
            lay.addWidget(b)
        lay.addStretch()
        return w

    def _step_mode(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        lay.addWidget(QLabel("立即开始哪种分析？"))
        self._mode_group = self._make_group([
            ("quick", "⚡ 快速分析", "打开看板，马上看到数据概况"),
            ("backtest", "🧪 深度回测", "直接进入回测中心验证策略"),
        ])
        for b in self._mode_group.buttons():
            lay.addWidget(b)
        lay.addStretch()
        return w

    def _lottery_hint(self, lottery: str) -> str:
        q = get_data_quality(lottery)
        if q["total"] > 0:
            return f"内置 {q['total']} 期真实历史数据（{q['date_from']} ~ {q['date_to']}）"
        return "暂无数据，可使用导入工具添加"

    # ---- 导航逻辑 ----
    def _go(self, idx: int):
        self._step = idx
        self.stack.setCurrentIndex(idx)
        self.prev_btn.setEnabled(idx > 0)
        # v4.6 P3：价值导向步骤
        titles = ["以后不用记彩票开奖时间", "选择你常买的彩种", "选择你的分析模式"]
        self.step_label.setText(f"第 {idx + 1} / 3 步 · 30 秒开始")
        self.title.setText(titles[idx])
        if idx == 2:
            self.next_btn.setText("✓ 完成，我的彩票已保护")
        else:
            self.next_btn.setText("下一步 →")
        # 默认选中第一个
        group = [self._purpose_group, self._lottery_group, self._mode_group][idx]
        if not any(b.isChecked() for b in group.buttons()):
            group.buttons()[0].setChecked(True)
            self._last_key = ["dashboard", "dlt", "quick"][idx]

    def _next(self):
        # 读取当前步骤选择
        if self._step == 0:
            self.purpose = self._checked_key(self._purpose_group, "dashboard")
        elif self._step == 1:
            self.lottery = self._checked_key(self._lottery_group, "dlt")
        else:
            self.mode = self._checked_key(self._mode_group, "quick")
        if self._step < 2:
            self._go(self._step + 1)
        else:
            self._finish()

    def _checked_key(self, group: QButtonGroup, default: str) -> str:
        for i, b in enumerate(group.buttons()):
            if b.isChecked():
                keys = {
                    self._purpose_group: ["dashboard", "backtest", "reports"],
                    self._lottery_group: ["dlt", "ssq"],
                    self._mode_group: ["quick", "backtest"],
                }
                mapping = keys.get(group, [])
                if i < len(mapping):
                    return mapping[i]
        return default

    def _finish(self):
        p = self._profile
        p.first_run_completed = True
        p.data_lottery = self.lottery
        save_profile(p)
        # v4.6 P3：onboarding_complete 事件
        self._completed = True
        try:
            from engine.user_analytics import AnalyticsTracker
            AnalyticsTracker().record("claim_completed", metadata={"onboarding": "complete"})
        except Exception:
            pass
        self.accept()
