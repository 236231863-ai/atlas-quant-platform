"""v4.8 P1：彩票数据导入中心测试。

覆盖：文本导入 / CSV 批量 / 历史票据 / ImportReport。
"""
from __future__ import annotations

import csv
import os

import pytest

from engine.import_center import (
    CSVImporter, HistoricalImporter, ImportReport, TextImporter,
    import_csv, import_text,
)


# ---------- 文本解析 ----------
def test_parse_single():
    t = TextImporter.parse("01 05 12 23 30 + 06 08")
    assert t["front"] == [1, 5, 12, 23, 30]
    assert t["back"] == [6, 8]


def test_parse_space_only():
    t = TextImporter.parse("01 05 12 23 30 06 08")
    assert t["front"] == [1, 5, 12, 23, 30]
    assert t["back"] == [6, 8]


def test_parse_comma_pipe():
    t = TextImporter.parse("01,05,12,23,30|06,08")
    assert t["front"] == [1, 5, 12, 23, 30]


def test_parse_ssq():
    t = TextImporter.parse("01 02 03 04 05 06 07", lottery="ssq")
    assert len(t["front"]) == 6
    assert t["back"] == [7]


def test_parse_empty():
    assert TextImporter.parse("") is None
    assert TextImporter.parse("   ") is None


def test_parse_invalid():
    assert TextImporter.parse("abc def") is None


# ---------- 文本导入 ----------
def test_import_text(ticket_storage):
    rep = import_text("01 05 12 23 30 + 06 08\n03 09 16 23 26 + 08 12")
    assert rep.total_imported == 2
    assert rep.skipped == 0


def test_import_text_empty(ticket_storage):
    rep = import_text("")
    assert rep.skipped >= 1


def test_import_text_mixed(ticket_storage):
    rep = import_text("01 05 12 23 30 + 06 08\nbad line")
    assert rep.total_imported == 1
    assert rep.skipped == 1


def test_import_persists(ticket_storage):
    import_text("01 05 12 23 30 + 06 08")
    from engine.ticket_system import TicketManager
    assert TicketManager().count() == 1


# ---------- CSV 导入 ----------
@pytest.fixture()
def csv_file(tmp_path):
    p = os.path.join(str(tmp_path), "tickets.csv")
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "lottery", "numbers", "cost"])
        w.writerow(["2026-08-01", "dlt", "01 02 03 04 05 06 07", "2"])
        w.writerow(["2026-08-02", "dlt", "11 12 13 14 15 01 02", "4"])
    return p


def test_import_csv(ticket_storage, csv_file):
    rep = import_csv(csv_file)
    assert rep.total_imported == 2


def test_import_csv_cost(ticket_storage, csv_file):
    import_csv(csv_file)
    from engine.ticket_system import TicketManager
    tickets = TicketManager().list_all()
    costs = sorted(t.cost for t in tickets)
    assert costs == [2.0, 4.0]


def test_import_csv_missing(ticket_storage):
    rep = import_csv("/nonexistent/x.csv")
    assert rep.total_imported == 0
    assert rep.errors


# ---------- 历史导入 ----------
def test_import_existing(ticket_storage):
    import_text("01 05 12 23 30 + 06 08")
    rep = HistoricalImporter.import_existing()
    assert rep.total_imported == 1


# ---------- 报告 ----------
def test_report_summary():
    rep = ImportReport(total_imported=2, duplicates=1, skipped=1)
    assert "成功导入：2" in rep.summary_text()
    assert "重复跳过：1" in rep.summary_text()


def test_report_to_dict():
    rep = ImportReport(total_imported=3)
    d = rep.to_dict()
    assert d["total_imported"] == 3


def test_report_total_processed():
    rep = ImportReport(total_imported=2, duplicates=1, skipped=1, errors=["x"])
    assert rep.total_processed == 5


# ---------- 矩阵 ----------
@pytest.mark.parametrize("n", [1, 3, 5, 10])
def test_import_text_scale(ticket_storage, n):
    lines = "\n".join(f"0{i} 05 12 23 30 + 06 08" for i in range(1, n + 1))
    rep = import_text(lines)
    assert rep.total_imported == n


@pytest.mark.parametrize("lottery", ["dlt", "ssq"])
def test_import_lottery(ticket_storage, lottery):
    if lottery == "dlt":
        rep = import_text("01 05 12 23 30 + 06 08", lottery="dlt")
    else:
        rep = import_text("01 02 03 04 05 06 07", lottery="ssq")
    assert rep.total_imported == 1
