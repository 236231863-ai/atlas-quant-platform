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

        header = QLabel("📊 数据看板")
        header.setStyleSheet("font-size:22px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

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
