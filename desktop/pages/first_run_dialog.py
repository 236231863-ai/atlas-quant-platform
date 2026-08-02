"""Atlas 首次使用引导对话框。

首次启动显示：欢迎 + 用户名设置 + 数据来源说明。
完成后保存用户档案，下次不再显示。
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
)

from user_profile import UserProfile, save_profile


class FirstRunDialog(QDialog):
    """首次运行欢迎与设置向导。"""

    def __init__(self, profile: UserProfile, parent=None):
        super().__init__(parent)
        self._profile = profile
        self.setWindowTitle("欢迎使用 Atlas Quant Platform")
        self.setFixedSize(480, 380)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        title = QLabel("🎉 欢迎使用 Atlas Quant Platform")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(title)

        sub = QLabel("您的量化研究平台。6 大功能模块，开箱即用。")
        sub.setStyleSheet("color:#8a94a6;font-size:13px;")
        root.addWidget(sub)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("您的称呼："))
        self.name_edit = QLineEdit(self._profile.username)
        self.name_edit.setPlaceholderText("输入您的称呼")
        self.name_edit.setStyleSheet("QLineEdit{padding:8px;border:1px solid #d8dee8;border-radius:6px;}")
        name_row.addWidget(self.name_edit, 1)
        root.addLayout(name_row)

        info = QLabel(
            "📦 内置演示数据可直接体验。\n"
            "📥 导入真实数据：将开奖 CSV 放入 data/raw/，或使用导入工具。\n"
            "🔒 您的设置仅保存在本机（~/.atlas/profile.json）。"
        )
        info.setStyleSheet(
            "background:#f4f6fa;border-radius:8px;padding:14px;color:#555;font-size:13px;line-height:1.7;"
        )
        info.setWordWrap(True)
        root.addWidget(info)

        root.addStretch()

        btn = QPushButton("开始使用")
        btn.setStyleSheet(
            "QPushButton{background:#1E3A8A;color:white;border:none;padding:10px;border-radius:8px;"
            "font-size:14px;font-weight:bold;}QPushButton:hover{background:#152C6B;}"
        )
        btn.clicked.connect(self._finish)
        root.addWidget(btn)

    def _finish(self):
        self._profile.username = self.name_edit.text().strip() or "量化研究者"
        self._profile.first_run_completed = True
        save_profile(self._profile)
        self.accept()
