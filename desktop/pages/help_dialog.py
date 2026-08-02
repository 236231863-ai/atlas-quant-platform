"""帮助中心对话框（v3.7.1 Phase 5）。

整合：版本信息 / 更新说明 / 安装指南 / FAQ / 反馈入口。
让首次用户遇到问题时能自助解决。
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTextEdit, QLineEdit, QTextBrowser, QMessageBox,
)

from release_center import ReleaseCenter


class HelpDialog(QDialog):
    """帮助中心：FAQ + 更新说明 + 安装指南 + 反馈。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Atlas 帮助中心")
        self.setFixedSize(680, 520)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)

        header = QLabel("🆘 Atlas 帮助中心")
        header.setStyleSheet("font-size:20px;font-weight:bold;color:#1a1a2e;")
        root.addWidget(header)

        rc = ReleaseCenter()
        ver = QLabel(f"当前版本：{rc.current_version} · {rc.release_notes()['date']}")
        ver.setStyleSheet("color:#8a94a6;font-size:12px;")
        root.addWidget(ver)

        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane{border:1px solid #e8ecf2;border-radius:8px;}"
                           "QTabBar::tab{padding:8px 16px;}")
        # FAQ
        faq_view = QTextBrowser()
        faq_text = "\n\n".join(f"**Q：{f['q']}**\nA：{f['a']}" for f in rc.faq())
        faq_view.setMarkdown(faq_text)
        tabs.addTab(faq_view, "常见问题")
        # 更新说明
        notes_view = QTextBrowser()
        notes_view.setMarkdown("\n".join(f"- {n}" for n in rc.update_notes()))
        tabs.addTab(notes_view, "更新说明")
        # 安装指南
        guide_view = QTextBrowser()
        guide_view.setMarkdown("\n".join(rc.install_guide()))
        tabs.addTab(guide_view, "安装指南")
        root.addWidget(tabs, 1)

        # 反馈区
        fb_row = QHBoxLayout()
        fb_row.addWidget(QLabel("反馈/建议："))
        self.fb_input = QLineEdit()
        self.fb_input.setPlaceholderText("告诉我们遇到的问题或建议…")
        self.fb_input.setStyleSheet("QLineEdit{padding:8px;border:1px solid #d8dee8;border-radius:6px;}")
        fb_row.addWidget(self.fb_input, 1)
        send_btn = QPushButton("提交")
        send_btn.setStyleSheet("QPushButton{background:#2a6df4;color:white;border:none;padding:8px 16px;border-radius:6px;}")
        send_btn.clicked.connect(self._submit_feedback)
        fb_row.addWidget(send_btn)
        root.addLayout(fb_row)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        root.addWidget(close_btn)

    def _submit_feedback(self):
        """提交反馈到本地反馈中心。"""
        content = self.fb_input.text().strip()
        if not content:
            QMessageBox.information(self, "提示", "请输入反馈内容。")
            return
        try:
            from backend.feedback import FeedbackManager
            FeedbackManager().add_feedback(content)
            QMessageBox.information(self, "已提交", "感谢反馈！你的意见将帮助我们改进。")
            self.fb_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "提交失败", f"反馈提交失败：{e}")
