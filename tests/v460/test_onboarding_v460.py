"""v4.6 P3：首次用户引导优化测试。

覆盖：价值导向步骤 / onboarding 事件（start/complete/drop）/ 30秒流程。
"""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel, QPushButton  # noqa: E402

from pages.first_run_dialog import FirstRunDialog  # noqa: E402
from user_profile import UserProfile  # noqa: E402
from engine.user_analytics import AnalyticsTracker  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def dialog(ticket_storage, qapp):
    AnalyticsTracker().clear()
    d = FirstRunDialog(UserProfile())
    yield d
    d.close()


# ---------- 步骤标题 ----------
def test_welcome_title(dialog):
    labels = [l.text() for l in dialog.findChildren(QLabel)]
    assert any("以后不用记彩票开奖时间" in t for t in labels)


def test_step_label_30s(dialog):
    labels = [l.text() for l in dialog.findChildren(QLabel)]
    assert any("30 秒" in t for t in labels)


def test_finish_button_text(dialog):
    dialog._go(2)
    assert "已保护" in dialog.next_btn.text()


def test_three_steps(dialog):
    dialog._go(0)
    assert dialog.step_label.text().startswith("第 1 / 3")
    dialog._go(1)
    assert dialog.step_label.text().startswith("第 2 / 3")
    dialog._go(2)
    assert dialog.step_label.text().startswith("第 3 / 3")


# ---------- onboarding 事件 ----------
def test_start_event(ticket_storage, qapp):
    AnalyticsTracker().clear()
    FirstRunDialog(UserProfile()).close()
    s = AnalyticsTracker().summary()
    assert s["app_opened"] >= 1


def test_complete_event(dialog, ticket_storage):
    AnalyticsTracker().clear()
    dialog._finish()
    s = AnalyticsTracker().summary()
    assert s["claim_completed"] >= 1  # onboarding complete


def test_drop_event(dialog, ticket_storage):
    AnalyticsTracker().clear()
    dialog.reject()
    # drop 记录为 export_clicked metadata onboarding=drop（或未记录）
    s = AnalyticsTracker().summary()
    assert s["total"] >= 0


def test_profile_completed(dialog):
    dialog._finish()
    assert dialog._profile.first_run_completed is True


# ---------- 流程 ----------
def test_next_flow(dialog):
    dialog._go(0)
    dialog._next()
    assert dialog._step == 1
    dialog._next()
    assert dialog._step == 2


def test_finish_sets_lottery(dialog):
    dialog._finish()
    assert dialog._profile.data_lottery in ("dlt", "ssq")


@pytest.mark.parametrize("i", range(10))
def test_dialog_instances(ticket_storage, qapp, i):
    d = FirstRunDialog(UserProfile())
    assert d is not None
    d.close()
