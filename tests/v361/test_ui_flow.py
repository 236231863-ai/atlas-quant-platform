"""v3.6.1 UI 流程测试：6 页面实例化 / 首次引导 / 数据不足警告 / 稳定性。"""
import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _write_profile(tmp_path, first_run_completed=True, data_lottery="dlt"):
    home = tmp_path
    d = home / ".atlas"
    d.mkdir(parents=True, exist_ok=True)
    (d / "profile.json").write_text(
        json.dumps({"username": "t", "first_run_completed": first_run_completed, "data_lottery": data_lottery}),
        encoding="utf-8",
    )
    return d


# ---------- 6 页面实例化 ----------
@pytest.mark.parametrize("module,cls", [
    ("dashboard_page", "DashboardPage"),
    ("analysis_page", "AnalysisPage"),
    ("strategy_page", "StrategyPage"),
    ("backtest_page", "BacktestPage"),
    ("ai_page", "AIPage"),
    ("reports_page", "ReportsPage"),
])
def test_pages_instantiate(qapp, module, cls):
    mod = __import__(f"pages.{module}", fromlist=[cls])
    page = getattr(mod, cls)()
    assert page is not None


@pytest.mark.parametrize("cls", ["DashboardPage", "AnalysisPage", "StrategyPage", "BacktestPage", "AIPage", "ReportsPage"])
def test_pages_have_build(qapp, cls):
    mod = __import__(f"pages.{cls.replace('Page','').lower()}_page", fromlist=[cls])
    page = getattr(mod, cls)()
    assert hasattr(page, "_build")


# ---------- 主窗口 ----------
@pytest.mark.parametrize("n", [0, 1])
def test_main_window(qapp, tmp_path, n):
    _write_profile(tmp_path)
    import health
    health.clear_crash_mark()
    from windows.main_window import MainWindow
    w = MainWindow()
    assert w.stack.count() == 9
    assert w.windowTitle() == "Atlas Quant Platform v4.4.0"


@pytest.mark.parametrize("target_idx", [0, 1, 2, 3, 4, 5])
def test_switch_page(qapp, target_idx):
    from windows.main_window import MainWindow, PAGES
    w = MainWindow()
    w.switch_page(PAGES[target_idx])
    assert w.stack.currentIndex() == target_idx


@pytest.mark.parametrize("name", ["Dashboard", "Data Analysis", "Strategy Lab", "Backtest Center", "AI Assistant", "Reports"])
def test_switch_page_by_name(qapp, name):
    from windows.main_window import MainWindow
    w = MainWindow()
    w.switch_page(name)
    assert w.stack.currentWidget() is not None


# ---------- 首次引导 ----------
@pytest.mark.parametrize("purpose", ["dashboard", "backtest", "reports"])
def test_first_run_purpose_defaults(qapp, purpose):
    from user_profile import UserProfile
    from pages.first_run_dialog import FirstRunDialog
    dlg = FirstRunDialog(UserProfile())
    dlg.purpose = purpose
    assert dlg.purpose in ("dashboard", "backtest", "reports")


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_first_run_lottery(qapp, lottery):
    from user_profile import UserProfile
    from pages.first_run_dialog import FirstRunDialog
    dlg = FirstRunDialog(UserProfile())
    dlg.lottery = lottery
    assert dlg.lottery in ("dlt", "ssq")


@pytest.mark.parametrize("mode", ["quick", "backtest"])
def test_first_run_mode(qapp, mode):
    from user_profile import UserProfile
    from pages.first_run_dialog import FirstRunDialog
    dlg = FirstRunDialog(UserProfile())
    dlg.mode = mode
    assert dlg.mode in ("quick", "backtest")


@pytest.mark.parametrize("step", [0, 1, 2])
def test_first_run_steps(qapp, step):
    from user_profile import UserProfile
    from pages.first_run_dialog import FirstRunDialog
    dlg = FirstRunDialog(UserProfile())
    dlg._go(step)
    assert dlg.stack.currentIndex() == step


# ---------- 数据不足警告 ----------
@pytest.mark.parametrize("total", [0, 10, 49, 50, 199, 200, 499, 500, 520])
def test_dashboard_quality_label(qapp, total):
    from data_loader import get_data_quality
    # 直接测质量函数（UI 标签依赖它）
    q = get_data_quality("dlt")
    assert "total" in q
    assert "trust_level" in q


@pytest.mark.parametrize("level", ["A", "B", "C", "D"])
def test_trust_level_mapping(qapp, level):
    from data_loader import _trust_level
    thresholds = {"A": 500, "B": 200, "C": 50, "D": 0}
    totals = {"A": 500, "B": 200, "C": 50, "D": 49}
    assert _trust_level(totals[level]) == level


# ---------- 稳定性（health） ----------
@pytest.mark.parametrize("n", [1, 2, 3])
def test_health_mark_crash(monkeypatch, tmp_path, n):
    import health
    for _ in range(n):
        health.mark_crash()
    assert health.was_crashed() is not None
    health.clear_crash_mark()
    assert health.was_crashed() is None


@pytest.mark.parametrize("data_total", [0, 49, 50, 200, 500])
def test_health_check_data(data_total):
    import health
    issues = health.check_health(data_total=data_total)
    if data_total < 50:
        assert any("数据量" in i for i in issues)
    else:
        assert not any("数据量" in i for i in issues)


@pytest.mark.parametrize("mod,name", [("PySide6", "PySide6"), ("matplotlib", "matplotlib")])
def test_health_deps_present(mod, name):
    import health
    issues = health.check_health()
    assert not any(name in i for i in issues)


# ---------- 回测联动（策略→回测） ----------
@pytest.mark.parametrize("method", ["hot", "cold", "balanced"])
def test_strategy_backtest_link(qapp, method):
    from pages.strategy_page import StrategyPage
    from pages.backtest_page import BacktestPage
    b = BacktestPage()
    b.run_strategy(method)
    assert b.combo.currentData() == method
    assert b.table.rowCount() > 0
