"""v4.2 Phase 4：年度报告（数据导出）测试。"""
from __future__ import annotations

import os
import random
from datetime import date

import pytest

from engine.annual_report import AnnualReport, AnnualReportEngine, annual_report

# 已知开奖：2026-08-01 大乐透 = [10,11,18,22,35] + [6,12]
JACKPOT_FRONT = [10, 11, 18, 22, 35]
JACKPOT_BACK = [6, 12]
JACKPOT_DRAW = "2026-08-01"


def _tk(lottery="dlt", front=None, back=None, buy="", draw="", cost=2.0):
    return {
        "lottery": lottery,
        "front": front or [1, 2, 3, 4, 5],
        "back": back or [6, 7],
        "buy_date": buy,
        "draw_date": draw,
        "cost": cost,
    }


# ---------- 年度筛选 ----------
def test_year_filter_only_that_year():
    tickets = [
        _tk(buy="2026-08-01"),
        _tk(buy="2025-08-01"),
        _tk(buy="2026-07-01"),
    ]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.ticket_count == 2
    assert r.year == 2026


def test_empty_year():
    r = AnnualReportEngine.build([_tk(buy="2025-01-01")], 2026)
    assert r.ticket_count == 0
    assert r.total_investment == 0


def test_default_year():
    r = AnnualReportEngine.build([_tk(buy=date.today().isoformat())])
    assert r.ticket_count == 1
    assert r.year == date.today().year


@pytest.mark.parametrize("year", [2024, 2025, 2026])
def test_year_matrix(year):
    tickets = [_tk(buy=f"{year}-06-15") for _ in range(3)]
    r = AnnualReportEngine.build(tickets, year)
    assert r.ticket_count == 3


# ---------- 统计计算 ----------
def test_investment():
    tickets = [_tk(buy="2026-08-01", cost=10.0), _tk(buy="2026-08-02", cost=5.5)]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.total_investment == 15.5


def test_win_stats():
    tickets = [_tk(front=JACKPOT_FRONT, back=JACKPOT_BACK, buy="2026-07-31", draw=JACKPOT_DRAW)]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.win_count == 1
    assert r.total_winnings == 5_000_000
    assert r.max_win == 5_000_000


def test_mixed_win():
    tickets = [
        _tk(front=JACKPOT_FRONT, back=JACKPOT_BACK, buy="2026-07-31", draw=JACKPOT_DRAW),
        _tk(buy="2026-08-02", draw=JACKPOT_DRAW),
    ]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.win_count == 1
    assert r.total_winnings == 5_000_000


@pytest.mark.parametrize("wins", [1, 2, 3, 4])
def test_win_count_matrix(wins):
    tickets = [_tk(front=JACKPOT_FRONT, back=JACKPOT_BACK, buy="2026-07-31",
                   draw=JACKPOT_DRAW) for _ in range(wins)]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.win_count == wins


# ---------- 活跃天数 / 周期 ----------
def test_purchase_days():
    tickets = [_tk(buy="2026-08-01"), _tk(buy="2026-08-01"), _tk(buy="2026-08-02")]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.purchase_days == 2


def test_first_last_dates():
    tickets = [_tk(buy="2026-08-03"), _tk(buy="2026-08-01")]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.first_ticket_date == "2026-08-01"
    assert r.last_ticket_date == "2026-08-03"


# ---------- 月度趋势 / 常购彩种 ----------
def test_monthly_trend():
    tickets = [_tk(buy="2026-01-01", cost=10.0), _tk(buy="2026-01-15", cost=5.0),
               _tk(buy="2026-07-01", cost=20.0)]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.monthly_trend["01"] == 15.0
    assert r.monthly_trend["07"] == 20.0


def test_favorite_lotteries():
    tickets = [_tk(lottery="dlt", buy="2026-08-01") for _ in range(3)]
    tickets += [_tk(lottery="ssq", buy="2026-08-01")]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.favorite_lotteries[0] == "大乐透"


# ---------- 输出 ----------
def test_summary_text_content():
    tickets = [_tk(buy="2026-08-01", cost=10.0),
               _tk(front=JACKPOT_FRONT, back=JACKPOT_BACK, buy="2026-07-31", draw=JACKPOT_DRAW)]
    r = AnnualReportEngine.build(tickets, 2026)
    s = r.summary_text()
    assert "年度总结" in s
    assert "2 次" in s
    assert "中奖次数：1 次" in s
    assert "最高奖金" in s


def test_summary_empty():
    r = AnnualReportEngine.build([], 2026)
    s = r.summary_text()
    assert "0 次" in s


def test_to_dict_keys():
    r = AnnualReportEngine.build([_tk(buy="2026-08-01")], 2026)
    d = r.to_dict()
    assert set(d) >= {"year", "ticket_count", "total_investment", "total_winnings",
                      "win_count", "max_win", "favorite_lotteries", "monthly_trend",
                      "purchase_days", "disclaimer"}


def test_no_induction():
    r = AnnualReportEngine.build([_tk(buy="2026-08-01", cost=100.0)], 2026)
    s = r.summary_text()
    for bad in ("稳赚", "必中", "保证", "预测", "推荐号码", "提高中奖"):
        assert bad not in s


def test_negative_net_honest():
    tickets = [_tk(buy="2026-08-01", cost=50.0)]
    r = AnnualReportEngine.build(tickets, 2026)
    s = r.summary_text()
    assert "负期望" in s  # 诚实提示


# ---------- PDF 导出 ----------
def test_export_pdf(tmp_path):
    r = AnnualReportEngine.build([_tk(buy="2026-08-01", cost=10.0)], 2026)
    out = os.path.join(str(tmp_path), "report.pdf")
    p = r.export_pdf(out)
    assert os.path.exists(p)
    with open(p, "rb") as f:
        head = f.read(5)
    assert head == b"%PDF-"


def test_export_pdf_auto_ext(tmp_path):
    r = AnnualReportEngine.build([_tk(buy="2026-08-01")], 2026)
    p = r.export_pdf(os.path.join(str(tmp_path), "my"))
    assert p.endswith(".pdf")
    assert os.path.exists(p)


def test_export_pdf_empty(tmp_path):
    r = AnnualReportEngine.build([], 2026)
    p = r.export_pdf(os.path.join(str(tmp_path), "empty.pdf"))
    assert os.path.exists(p)


# ---------- 便捷函数 ----------
def test_annual_report_func():
    r = annual_report([_tk(buy="2026-08-01")], 2026)
    assert isinstance(r, AnnualReport)


# ---------- 参数化矩阵 ----------
@pytest.mark.parametrize("seed", range(40))
def test_annual_random_matrix(seed):
    rng = random.Random(seed)
    tickets = []
    for _ in range(rng.randint(0, 12)):
        year = rng.choice([2025, 2026])
        win = rng.random() < 0.25
        if win:
            tickets.append(_tk(front=JACKPOT_FRONT, back=JACKPOT_BACK,
                               buy=f"{year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                               draw=JACKPOT_DRAW, cost=rng.randint(2, 20)))
        else:
            tickets.append(_tk(buy=f"{year}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                               draw="", cost=rng.randint(2, 20)))
    r = AnnualReportEngine.build(tickets, 2026)
    expected = sum(1 for t in tickets if t["buy_date"].startswith("2026-"))
    assert r.ticket_count == expected
    assert r.win_count <= expected
    assert r.total_investment >= 0
    assert r.max_win >= 0
    assert r.purchase_days <= expected
    s = r.summary_text()
    assert isinstance(s, str) and len(s) > 5


@pytest.mark.parametrize("seed", range(15))
def test_annual_pdf_roundtrip(seed, tmp_path):
    rng = random.Random(1000 + seed)
    tickets = [_tk(buy="2026-08-01", cost=rng.randint(2, 50)) for _ in range(rng.randint(1, 6))]
    r = AnnualReportEngine.build(tickets, 2026)
    p = r.export_pdf(os.path.join(str(tmp_path), f"r{seed}.pdf"))
    assert os.path.exists(p)
    with open(p, "rb") as f:
        assert f.read(5) == b"%PDF-"


@pytest.mark.parametrize("seed", range(15))
def test_annual_full_flow(seed, ticket_storage):
    """全流程：保存→年度报告→PDF。"""
    from engine.ticket_system import TicketManager
    rng = random.Random(2000 + seed)
    mgr = TicketManager()
    mgr.clear()
    for _ in range(rng.randint(1, 5)):
        mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-08-01", cost=2.0)
    tickets = [t.__dict__ for t in mgr.list_all()]
    r = AnnualReportEngine.build(tickets, 2026)
    assert r.ticket_count == len(tickets)
    assert "年度总结" in r.summary_text()
    mgr.clear()
