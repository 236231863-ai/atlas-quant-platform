"""v4.1 阶段4：个人成长中心测试。"""
from __future__ import annotations

import random
from datetime import date, timedelta

import pytest

from engine.personal_growth import PersonalGrowthEngine, GrowthReport, growth_report


def _tk(front, back, buy=None, draw="", cost=2.0):
    return {"front": front, "back": back,
            "buy_date": buy or (date.today() - timedelta(days=1)).isoformat(),
            "draw_date": draw, "cost": cost}


TODAY = date.today()


# ---------- 购彩历史 ----------
def test_empty():
    r = growth_report([])
    assert r.total_days == 0
    assert r.current_streak == 0


def test_total_days():
    t1 = _tk([1, 2, 3, 4, 5], [6, 7], buy=TODAY.isoformat())
    t2 = _tk([1, 2, 3, 4, 5], [6, 7], buy=(TODAY - timedelta(days=1)).isoformat())
    t3 = _tk([1, 2, 3, 4, 5], [6, 7], buy=(TODAY - timedelta(days=1)).isoformat())
    r = growth_report([t1, t2, t3])
    assert r.total_days == 2


@pytest.mark.parametrize("n", [1, 3, 5, 8])
def test_total_days_count(n):
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=(TODAY - timedelta(days=i)).isoformat()) for i in range(n)]
    r = growth_report(tickets)
    assert r.total_days == n


# ---------- 连续购买 ----------
def test_streak_consecutive():
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=(TODAY - timedelta(days=i)).isoformat()) for i in range(3)]
    r = growth_report(tickets)
    assert r.current_streak == 3
    assert r.max_streak == 3


def test_streak_broken():
    t1 = _tk([1, 2, 3, 4, 5], [6, 7], buy=TODAY.isoformat())
    t2 = _tk([1, 2, 3, 4, 5], [6, 7], buy=(TODAY - timedelta(days=5)).isoformat())
    r = growth_report([t1, t2])
    assert r.current_streak == 1
    assert r.max_streak == 1


def test_streak_max():
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=(TODAY - timedelta(days=i)).isoformat()) for i in range(4)]
    r = growth_report(tickets)
    assert r.max_streak == 4


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_streak_matrix(n):
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=(TODAY - timedelta(days=i)).isoformat()) for i in range(n)]
    r = growth_report(tickets)
    assert r.current_streak == n
    assert r.max_streak == n


# ---------- 连续中奖 ----------
def test_consecutive_win():
    t = _tk([10, 11, 18, 22, 35], [6, 12], buy=(TODAY - timedelta(days=2)).isoformat(),
            draw="2026-08-01")
    r = growth_report([t])
    assert r.consecutive_wins >= 1


def test_no_win():
    t = _tk([1, 2, 3, 4, 5], [6, 7])
    r = growth_report([t])
    assert r.consecutive_wins == 0


# ---------- 月度/年度汇总 ----------
def test_monthly_summary():
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=(TODAY - timedelta(days=i)).isoformat(), cost=4.0) for i in range(2)]
    r = growth_report(tickets)
    mkey = f"{TODAY.year}-{TODAY.month:02d}"
    assert mkey in r.monthly_summary
    assert r.monthly_summary[mkey]["spent"] == pytest.approx(8.0)


def test_annual_summary():
    t = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-07-01", cost=2.0)
    r = growth_report([t])
    assert "2026" in r.annual_summary
    assert r.annual_summary["2026"]["spent"] == pytest.approx(2.0)


def test_annual_roi():
    t = _tk([10, 11, 18, 22, 35], [6, 12], buy="2026-07-31", draw="2026-08-01")
    r = growth_report([t])
    assert r.annual_summary["2026"]["roi"] > 0


# ---------- 年度报告文本 ----------
def test_annual_report_text():
    r = growth_report([])
    t = r.annual_report_text()
    assert "年度购彩报告" in t
    assert "随机性" in t


def test_annual_report_with_data():
    t = _tk([1, 2, 3, 4, 5], [6, 7], buy="2026-07-01", cost=2.0)
    r = growth_report([t])
    t = r.annual_report_text(2026)
    assert "累计投入" in t


# ---------- 报告结构 ----------
def test_report_type():
    r = growth_report([])
    assert isinstance(r, GrowthReport)


@pytest.mark.parametrize("f", ["total_days", "current_streak", "max_streak",
                               "consecutive_wins", "monthly_summary", "annual_summary"])
def test_report_fields(f):
    r = growth_report([])
    assert hasattr(r, f)


@pytest.mark.parametrize("f", ["total_days", "current_streak", "max_streak",
                               "consecutive_wins", "monthly_summary"])
def test_report_dict_keys(f):
    r = growth_report([])
    assert f in r.to_dict()


def test_summary_fields():
    r = growth_report([])
    t = r.summary_text()
    for kw in ("购彩记录", "连续购买", "连续中奖"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer():
    r = growth_report([])
    assert "随机性" in r.disclaimer
    assert "预测" not in r.disclaimer


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(30))
def test_growth_matrix(seed):
    rng = random.Random(seed)
    tickets = []
    for _ in range(rng.randint(1, 10)):
        offset = rng.randint(0, 30)
        tickets.append(_tk([1, 2, 3, 4, 5], [6, 7],
                           buy=(TODAY - timedelta(days=offset)).isoformat()))
    r = growth_report(tickets)
    assert r.total_days >= 1
    assert r.current_streak >= 0
    assert r.max_streak >= 1


@pytest.mark.parametrize("seed", range(30))
def test_growth_win_matrix(seed):
    rng = random.Random(1000 + seed)
    tickets = []
    for _ in range(rng.randint(1, 5)):
        if rng.random() < 0.5:
            tickets.append(_tk([10, 11, 18, 22, 35], [6, 12],
                               buy=(TODAY - timedelta(days=2)).isoformat(),
                               draw="2026-08-01"))
        else:
            tickets.append(_tk([1, 2, 3, 4, 5], [6, 7]))
    r = growth_report(tickets)
    assert r.consecutive_wins >= 0


@pytest.mark.parametrize("seed", range(20))
def test_annual_matrix(seed):
    rng = random.Random(2000 + seed)
    tickets = [_tk([1, 2, 3, 4, 5], [6, 7],
                   buy=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}") for _ in range(5)]
    r = growth_report(tickets)
    assert isinstance(r.annual_report_text(), str)
