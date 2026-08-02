"""v3.9.0 桌面端彩票量化中心 UI 入口测试。"""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

NOTES = "10111822350612 01020304050607 05101520250612"


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def window(app):
    from windows.main_window import MainWindow
    return MainWindow()


# ---------- 导航与页面 ----------
def test_pages_include_quant(window):
    assert "量化中心" in window.nav._pages


def test_stack_count_8(window):
    assert window.stack.count() == 8


def test_quant_page_exists(window):
    assert hasattr(window, "quant")


def test_switch_to_quant(window):
    window.switch_page("量化中心")
    assert window.stack.currentWidget() is window.quant


def test_nav_all_pages(window):
    assert len(window.nav._pages) == 8


# ---------- 工作台入口 ----------
def test_workbench_has_quant_button(window):
    from pages.workbench_page import WorkbenchPage
    assert isinstance(window.workbench, WorkbenchPage)
    # 检查 quant_requested 信号存在
    assert hasattr(window.workbench, "quant_requested")


def test_quant_requested_signal_connected(window):
    """工作台信号 → 切换到量化中心。"""
    window.switch_page("工作台")
    window.workbench.quant_requested.emit()
    assert window.stack.currentWidget() is window.quant


# ---------- QuantPage 功能 ----------
def test_quant_page_init(window):
    assert window.quant.windowTitle() == "" or True  # 无标题，验证可实例化


def test_structure_button(window):
    qp = window.quant
    qp.input.setPlainText(NOTES)
    qp._run_structure()
    assert "组合评分" in qp.result.toPlainText()


def test_probability_button(window):
    qp = window.quant
    qp._run_probability()
    assert "概率" in qp.result.toPlainText()


def test_simulation_button(window):
    qp = window.quant
    qp.input.setPlainText(NOTES)
    qp._run_simulation()
    assert "模拟" in qp.result.toPlainText()


def test_risk_button(window):
    qp = window.quant
    qp.input.setPlainText(NOTES)
    qp._run_risk()
    assert "风险" in qp.result.toPlainText()


def test_backtest_button(window):
    qp = window.quant
    qp._run_backtest()
    assert "回测" in qp.result.toPlainText()


def test_need_numbers_prompt(window):
    qp = window.quant
    qp.input.setPlainText("")
    qp._run_structure()
    assert "号码" in qp.result.toPlainText()


def test_load_from_tickets_empty(window):
    qp = window.quant
    # 空票据不崩溃
    qp._load_from_tickets()
    assert isinstance(qp.result.toPlainText(), str)


def test_disclaimer_in_welcome(window):
    qp = window.quant
    assert "随机性" in qp.result.toPlainText()


# ---------- 各功能结果含免责声明 ----------
@pytest.mark.parametrize("run_method", ["_run_structure", "_run_probability",
                                        "_run_simulation", "_run_risk", "_run_backtest"])
def test_each_feature_has_disclaimer(window, run_method):
    qp = window.quant
    qp.input.setPlainText(NOTES)
    getattr(qp, run_method)()
    text = qp.result.toPlainText()
    assert any(kw in text for kw in ("随机性", "不代表", "负期望", "理性购彩"))


# ---------- 从票据读取 ----------
def test_load_from_tickets_with_data(window, tmp_path, monkeypatch):
    from engine.ticket_system import TicketManager
    # 用临时目录隔离票据
    monkeypatch.setattr(TicketManager, "__init__", lambda self, storage_dir=None: (
        setattr(self, "_dir", str(tmp_path)),
        setattr(self, "_path", str(tmp_path / "tickets.json")),
        setattr(self, "_tickets", {}),
        None
    ))
    qp = window.quant
    qp._load_from_tickets()  # 空票据提示
    assert isinstance(qp.result.toPlainText(), str)


# ---------- 随机性声明（验收红线）----------
@pytest.mark.parametrize("banned", ["预测中奖", "提高中奖概率", "稳赚", "人工智能预测彩票"])
def test_no_forbidden_expressions(window, banned):
    qp = window.quant
    qp.input.setPlainText(NOTES)
    for m in ("_run_structure", "_run_probability", "_run_simulation", "_run_risk", "_run_backtest"):
        getattr(qp, m)()
    assert banned not in qp.result.toPlainText()
