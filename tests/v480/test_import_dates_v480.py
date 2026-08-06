"""v4.8.2 回归：手动添加彩票后购买/开奖日期应自动补全（fill_dates）。

用户反馈：工作台输入号码后，购买时间与开奖时间没有实时更新（显示 "-"）。
根因：TextImporter 添加票据时 draw_date 固定传空，且 buy_date 留空时也传空。
修复：fill_dates() 统一补全 —— 购买日期空→今天；开奖日期=购买日后最近开奖日。
"""
import os
import pytest

from engine.import_center.imports import (
    CSVImporter,
    TextImporter,
    fill_dates,
)


# ---- fill_dates 单元 ----
def test_fill_dates_empty_buy_date_dlt(ticket_storage):
    """空购买日期 → 今天 + 最近大乐透开奖日。"""
    from datetime import date
    bd, dd = fill_dates("", "dlt")
    assert bd == date.today().isoformat()
    assert dd >= bd  # 开奖日不早于购买日


def test_fill_dates_empty_buy_date_ssq(ticket_storage):
    from datetime import date
    bd, dd = fill_dates("", "ssq")
    assert bd == date.today().isoformat()
    assert dd >= bd


def test_fill_dates_draw_is_draw_day(ticket_storage):
    """开奖日期必须是该彩种开奖日。"""
    from engine.ticket_system.schedule import LotterySchedule
    for lottery in ("dlt", "ssq"):
        for buy in ("2026-08-01", "2026-08-05", "2026-08-06"):
            _, dd = fill_dates(buy, lottery)
            if dd:
                assert LotterySchedule.is_draw_day(lottery, dd)


def test_fill_dates_draw_not_before_buy(ticket_storage):
    """开奖日 >= 购买日（含当日开奖）。"""
    for lottery in ("dlt", "ssq"):
        for buy in ("2026-08-01", "2026-08-03", "2026-08-06"):
            _, dd = fill_dates(buy, lottery)
            assert dd >= buy


@pytest.mark.parametrize("buy,lottery,expect", [
    ("2026-08-05", "dlt", "2026-08-05"),   # 周三 大乐透开奖日
    ("2026-08-06", "dlt", "2026-08-08"),   # 周四 → 周六
    ("2026-08-06", "ssq", "2026-08-06"),   # 周四 双色球开奖日
    ("2026-08-07", "ssq", "2026-08-09"),   # 周五 → 周日
])
def test_fill_dates_known_draws(ticket_storage, buy, lottery, expect):
    bd, dd = fill_dates(buy, lottery)
    assert bd == buy
    assert dd == expect


def test_fill_dates_draw_date_dlt_next_day(ticket_storage):
    """周一(2026-08-03)买大乐透 → 当日开奖。"""
    _, dd = fill_dates("2026-08-03", "dlt")
    assert dd == "2026-08-03"


def test_fill_dates_ssq_after_draw_day(ticket_storage):
    """周日(2026-08-09)买双色球 → 当日开奖。"""
    _, dd = fill_dates("2026-08-09", "ssq")
    assert dd == "2026-08-09"


# ---- TextImporter 集成 ----
def test_import_text_defaults_dates(ticket_storage):
    """文本导入（留空日期）→ 自动补今天 + 开奖日。"""
    rep = TextImporter.import_text("13 21 23 26 33 + 01 12", lottery="dlt", buy_date="")
    assert rep.total_imported == 1
    t = rep.tickets[0]
    assert t["buy_date"]  # 非空
    assert t["draw_date"]  # 非空
    assert t["draw_date"] >= t["buy_date"]


def test_import_text_specified_buy_date(ticket_storage):
    rep = TextImporter.import_text("05 19 23 32 34 + 02 11",
                                   lottery="dlt", buy_date="2026-08-05")
    t = rep.tickets[0]
    assert t["buy_date"] == "2026-08-05"
    assert t["draw_date"] == "2026-08-05"  # 周三大乐透开奖


def test_import_text_draw_after_buy(ticket_storage):
    rep = TextImporter.import_text("03 18 24 30 33 + 05 12",
                                   lottery="dlt", buy_date="2026-08-06")
    t = rep.tickets[0]
    assert t["draw_date"] == "2026-08-08"


def test_import_text_multiple_lines_dates(ticket_storage):
    text = "13 21 23 26 33 + 01 12\n05 19 23 32 34 + 02 11"
    rep = TextImporter.import_text(text, lottery="dlt", buy_date="2026-08-06")
    assert rep.total_imported == 2
    assert all(t["draw_date"] for t in rep.tickets)


def test_import_text_ssq_dates(ticket_storage):
    rep = TextImporter.import_text("01 02 03 04 05 06 + 07", lottery="ssq",
                                   buy_date="2026-08-06")
    t = rep.tickets[0]
    assert t["buy_date"] == "2026-08-06"
    assert t["draw_date"] == "2026-08-06"  # 周四周双色球


def test_import_text_ticket_manager_persists_dates(ticket_storage):
    """写入 TicketManager 后日期可读回。"""
    from engine.ticket_system import TicketManager
    TextImporter.import_text("13 21 23 26 33 + 01 12", lottery="dlt",
                             buy_date="2026-08-06")
    tm = TicketManager()
    t = tm.list_all()[0]
    assert t.buy_date == "2026-08-06"
    assert t.draw_date == "2026-08-08"


# ---- CSVImporter 集成 ----
def _csv(tmp_path, content):
    p = os.path.join(str(tmp_path), "t.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


def test_import_csv_empty_date_defaults_today(ticket_storage, tmp_path):
    p = _csv(tmp_path, "date,lottery,numbers,cost\n,dlt,01 05 12 23 30 + 06 08,2\n")
    rep = CSVImporter.import_csv(p)
    assert rep.total_imported == 1
    t = rep.tickets[0]
    from datetime import date
    assert t["buy_date"] == date.today().isoformat()
    assert t["draw_date"]


def test_import_csv_with_date(ticket_storage, tmp_path):
    p = _csv(tmp_path, "date,lottery,numbers,cost\n2026-08-05,dlt,01 05 12 23 30 + 06 08,2\n")
    rep = CSVImporter.import_csv(p)
    t = rep.tickets[0]
    assert t["buy_date"] == "2026-08-05"
    assert t["draw_date"] == "2026-08-05"


def test_import_csv_ssq_dates(ticket_storage, tmp_path):
    p = _csv(tmp_path, "date,lottery,numbers,cost\n2026-08-07,ssq,01 02 03 04 05 06 + 07,2\n")
    rep = CSVImporter.import_csv(p)
    t = rep.tickets[0]
    assert t["draw_date"] == "2026-08-09"


def test_import_csv_workbench_flow(ticket_storage, tmp_path):
    """模拟工作台手动添加：用户只粘贴号码、留空日期 → 日期自动补全。"""
    rep = TextImporter.import_text("09 13 23 26 32 + 11 12",
                                   lottery="dlt", buy_date="")
    assert rep.total_imported == 1
    t = rep.tickets[0]
    assert t["buy_date"] and t["draw_date"]
