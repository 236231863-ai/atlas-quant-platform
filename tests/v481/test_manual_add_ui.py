"""v4.8.1 手动添加彩票功能 UI 测试。

覆盖：控件存在 / 大乐透添加成功 / 双色球 / 空输入 / 非法号码 / 日期 / 表格刷新。
"""
from __future__ import annotations

import pytest

from engine.ticket_system import TicketManager


def _clear(ticket_storage):
    TicketManager().clear()


# ---------- 控件存在 ----------
def test_manual_add_widgets_exist(window):
    wb = window.workbench
    for attr in ("lottery_combo", "date_edit", "input_edit", "add_btn", "add_result"):
        assert hasattr(wb, attr), f"缺少控件 {attr}"
    assert wb.lottery_combo.count() == 2  # 大乐透 + 双色球


def test_add_btn_connected(window):
    wb = window.workbench
    assert wb.add_btn.isEnabled()


# ---------- 大乐透添加 ----------
def test_add_success_dlt(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.lottery_combo.setCurrentIndex(0)  # 大乐透
    wb.input_edit.setPlainText("01 05 12 23 30 + 06 08\n02 08 15 22 33 + 01 09")
    wb._manual_add()
    assert TicketManager().count() == 2
    assert "导入完成" in wb.add_result.text()
    assert "成功导入" in wb.add_result.text()
    _clear(ticket_storage)


def test_add_success_ticket_values(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.input_edit.setPlainText("06 16 21 30 34 + 06 12")
    wb._manual_add()
    t = TicketManager().list_all()[0]
    assert t.front == [6, 16, 21, 30, 34]
    assert t.back == [6, 12]
    assert t.lottery == "dlt"
    _clear(ticket_storage)


def test_add_refreshes_table(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.input_edit.setPlainText("01 05 12 23 30 + 06 08")
    wb._manual_add()
    assert wb.ticket_table.rowCount() == 1
    _clear(ticket_storage)


def test_add_clears_input(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.input_edit.setPlainText("01 05 12 23 30 + 06 08")
    wb._manual_add()
    assert wb.input_edit.toPlainText().strip() == ""
    _clear(ticket_storage)


# ---------- 空输入 ----------
def test_add_empty_input(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.input_edit.setPlainText("")
    wb._manual_add()
    assert "请输入号码" in wb.add_result.text()
    assert TicketManager().count() == 0
    _clear(ticket_storage)


# ---------- 非法号码 ----------
def test_add_invalid_number(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.input_edit.setPlainText("99 100 101 102 103 + 99 99")  # 超出范围
    wb._manual_add()
    assert TicketManager().count() == 0
    assert "没有成功添加" in wb.add_result.text()
    _clear(ticket_storage)


def test_add_mixed_valid_invalid(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.input_edit.setPlainText("01 05 12 23 30 + 06 08\nnot a valid line")
    wb._manual_add()
    assert TicketManager().count() == 1
    _clear(ticket_storage)


# ---------- 双色球 ----------
def test_add_ssq(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.lottery_combo.setCurrentIndex(1)  # 双色球
    wb.input_edit.setPlainText("01 05 12 23 30 33 + 06")  # 前6后1
    wb._manual_add()
    assert TicketManager().count() == 1
    t = TicketManager().list_all()[0]
    assert t.lottery == "ssq"
    assert len(t.front) == 6 and len(t.back) == 1
    _clear(ticket_storage)


# ---------- 购买日期 ----------
def test_add_with_buy_date(window, ticket_storage):
    _clear(ticket_storage)
    wb = window.workbench
    wb.date_edit.setText("2026-07-29")
    wb.input_edit.setPlainText("01 05 12 23 30 + 06 08")
    wb._manual_add()
    t = TicketManager().list_all()[0]
    assert t.buy_date == "2026-07-29"
    _clear(ticket_storage)


# ---------- 参数化矩阵 ----------
@pytest.mark.parametrize("n", [1, 2, 5])
def test_add_multiple_lines(window, ticket_storage, n):
    _clear(ticket_storage)
    wb = window.workbench
    lines = "\n".join(f"{i:02d} {i+1:02d} {i+2:02d} {i+3:02d} {i+4:02d} + 0{i % 9 + 1:02d} 0{i % 8 + 1:02d}"
                      for i in range(1, n + 1))
    wb.input_edit.setPlainText(lines)
    wb._manual_add()
    assert TicketManager().count() == n
    _clear(ticket_storage)


@pytest.mark.parametrize("seed", range(5))
def test_add_random_valid(window, ticket_storage, seed):
    import random
    rng = random.Random(seed)
    _clear(ticket_storage)
    wb = window.workbench
    lines = "\n".join(
        " ".join(f"{x:02d}" for x in sorted(rng.sample(range(1, 36), 5)))
        + " + "
        + " ".join(f"{x:02d}" for x in sorted(rng.sample(range(1, 13), 2)))
        for _ in range(3))
    wb.input_edit.setPlainText(lines)
    wb._manual_add()
    assert TicketManager().count() == 3
    _clear(ticket_storage)
