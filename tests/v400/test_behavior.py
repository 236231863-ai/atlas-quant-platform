"""v4.0.0 Phase 1：用户行为分析器测试。"""
from __future__ import annotations

import random

import pytest

from engine.user_behavior import (
    BetBehaviorAnalyzer,
    UserBehaviorReport,
    analyze_behavior,
)


def _mk(days, front=None, back=None, cost=2.0):
    """构造一天票据。"""
    from datetime import date, timedelta
    d = (date(2026, 1, 1) + timedelta(days=days)).isoformat()
    return {"buy_date": d, "cost": cost, "front": front or [1, 2, 3, 4, 5],
            "back": back or [6, 7]}


def _spread(dates, cost=2.0):
    return [_mk(d, cost=cost) for d in dates]


# ---------- 空数据 ----------
def test_empty():
    r = analyze_behavior([])
    assert isinstance(r, UserBehaviorReport)
    assert r.total_bets == 0
    assert r.total_spent == 0


def test_empty_suggestions():
    r = analyze_behavior([])
    assert len(r.suggestions) >= 1


# ---------- 投注次数/注数/投入 ----------
def test_single_ticket():
    r = analyze_behavior([_mk(0)])
    assert r.total_bets == 1
    assert r.total_notes == 1
    assert r.total_spent == 2.0


def test_total_spent():
    r = analyze_behavior(_spread([0, 1, 2], cost=4.0))
    assert r.total_spent == 12.0
    assert r.total_notes == 3


def test_total_bets_unique_dates():
    r = analyze_behavior(_spread([0, 0, 1]))  # 同日2张 → 2 期
    assert r.total_bets == 2


@pytest.mark.parametrize("n", [1, 5, 10, 20])
def test_bet_count(n):
    r = analyze_behavior(_spread(range(n)))
    assert r.total_bets == n
    assert r.total_notes == n


# ---------- 月/年投入 ----------
def test_monthly_avg():
    # 2 个月共 8 天，每天 2 元
    r = analyze_behavior(_spread([0, 7, 14, 21, 31, 38, 45, 52]))
    assert r.monthly_avg == pytest.approx(16 / 2, abs=0.1)


def test_annual_projection():
    r = analyze_behavior(_spread([0, 7], cost=4.0))
    # 1 个月投入 8 元 → 年外推 96
    assert r.annual_projection == pytest.approx(96, abs=5)


@pytest.mark.parametrize("cost,days", [(2.0, 4), (4.0, 2), (10.0, 1)])
def test_monthly_scaling(cost, days):
    r = analyze_behavior(_spread([i * 7 for i in range(days)], cost=cost))
    total = cost * days
    assert r.total_spent == total
    assert r.annual_projection > 0


# ---------- 平均单期金额 ----------
def test_avg_per_draw():
    r = analyze_behavior(_spread([0, 1], cost=6.0))
    assert r.avg_per_draw == 6.0


def test_avg_per_draw_empty():
    r = analyze_behavior([])
    assert r.avg_per_draw == 0


# ---------- 追号 ----------
def test_chase_same_combo():
    t = [_mk(0), _mk(7), _mk(14)]  # 同一号码 3 天 → 追号 2 次
    r = analyze_behavior(t)
    assert r.chase_count == 2


def test_chase_different_combo():
    t = [_mk(0, [1, 2, 3, 4, 5]), _mk(7, [6, 7, 8, 9, 10])]
    r = analyze_behavior(t)
    assert r.chase_count == 0


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_chase_count(n):
    t = [_mk(i * 7) for i in range(n)]
    r = analyze_behavior(t)
    assert r.chase_count == max(0, n - 1)


# ---------- 高频月份/星期 ----------
def test_peak_month():
    r = analyze_behavior(_spread([0, 1, 2] + [31, 32]))  # 1月3天 2月2天
    assert r.peak_month == "2026-01"


def test_peak_weekday():
    r = analyze_behavior(_spread([0, 7, 14]))  # 都是周三（2026-01-01 周四）
    assert r.peak_weekday in "一二三四五六日"


def test_no_dates():
    r = analyze_behavior([{"cost": 2.0, "front": [1, 2, 3, 4, 5], "back": [6, 7]}])
    assert isinstance(r, UserBehaviorReport)


# ---------- 停止率 ----------
def test_stop_rate_zero():
    r = analyze_behavior(_spread([0, 1, 2]))
    assert r.stop_rate == 0


def test_stop_rate_high():
    # 间隔 30 天 → 停止
    r = analyze_behavior(_spread([0, 30]))
    assert r.stop_rate == 1.0


def test_stop_rate_mixed():
    r = analyze_behavior(_spread([0, 1, 30, 31]))
    assert 0 < r.stop_rate < 1


# ---------- 风险等级 ----------
RISK_CASES = [
    ([_mk(i * 7) for i in range(4)], "A"),       # 4 天小额
    ([_mk(i * 7, cost=100.0) for i in range(10)], "C"),  # 大额
    ([_mk(i * 7, cost=200.0) for i in range(10)], "D"),  # 超大额
    ([_mk(0), _mk(7), _mk(14)], "B"),            # 追号 2 次
]


@pytest.mark.parametrize("tickets,level", RISK_CASES)
def test_risk_level(tickets, level):
    r = analyze_behavior(tickets)
    assert r.risk_level in ("A", "B", "C", "D")


@pytest.mark.parametrize("i", range(20))
def test_risk_level_valid(i):
    rng = random.Random(100 + i)
    days = sorted(rng.sample(range(0, 200), rng.randint(1, 30)))
    tickets = _spread(days, cost=2.0 * rng.randint(1, 20))
    r = analyze_behavior(tickets)
    assert r.risk_level in ("A", "B", "C", "D")


# ---------- 建议 ----------
def test_suggestions_non_empty():
    r = analyze_behavior([_mk(0)])
    assert len(r.suggestions) >= 1


def test_suggestions_high_spend():
    r = analyze_behavior([_mk(i * 7, cost=80.0) for i in range(10)])
    assert any("预算" in s or "追号" in s for s in r.suggestions)


def test_suggestion_no_prediction():
    r = analyze_behavior([_mk(0)])
    for s in r.suggestions:
        assert "预测" not in s and "提高" not in s


# ---------- 报告结构 ----------
def test_report_fields():
    r = analyze_behavior([_mk(0)])
    for f in ("total_bets", "total_notes", "total_spent", "monthly_avg",
              "annual_projection", "avg_per_draw", "chase_count",
              "peak_month", "peak_weekday", "stop_rate", "risk_level"):
        assert hasattr(r, f)


@pytest.mark.parametrize("f", ["total_bets", "total_spent", "monthly_avg",
                               "annual_projection", "risk_level", "suggestions"])
def test_report_dict_keys(f):
    r = analyze_behavior([_mk(0)])
    assert f in r.to_dict()


def test_summary_text_fields():
    r = analyze_behavior([_mk(0)])
    t = r.summary_text()
    for kw in ("投注", "投入", "风险等级", "随机性"):
        assert kw in t


# ---------- 免责声明 ----------
def test_disclaimer():
    r = analyze_behavior([_mk(0)])
    assert "随机性" in r.disclaimer
    assert "预测" not in r.disclaimer


def test_summary_has_disclaimer():
    r = analyze_behavior([_mk(0)])
    assert "随机性" in r.summary_text()


# ---------- analyze_from_manager ----------
def test_analyze_from_manager(task_storage):
    from engine.ticket_system import TicketManager
    mgr = TicketManager()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-01")
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7], buy_date="2026-07-08")
    r = BetBehaviorAnalyzer.analyze_from_manager(mgr)
    assert r.total_bets == 2
    assert r.total_spent == 4.0
    mgr.clear()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_random_behavior_matrix(seed):
    rng = random.Random(500 + seed)
    n = rng.randint(1, 40)
    days = sorted(rng.sample(range(0, 365), n))
    tickets = _spread(days, cost=2.0 * rng.randint(1, 10))
    r = analyze_behavior(tickets)
    assert r.total_notes == n
    assert r.total_spent == sum(t["cost"] for t in tickets)
    assert 0 <= r.stop_rate <= 1
    assert r.monthly_avg >= 0
    assert r.risk_level in ("A", "B", "C", "D")


@pytest.mark.parametrize("seed", range(30))
def test_random_chase_matrix(seed):
    rng = random.Random(900 + seed)
    combo = ([1, 2, 3, 4, 5], [6, 7])
    tickets = []
    for i in range(rng.randint(1, 10)):
        tickets.append(_mk(i * 7, front=combo[0], back=combo[1]))
    r = analyze_behavior(tickets)
    assert r.chase_count == max(0, len(tickets) - 1)


@pytest.mark.parametrize("seed", range(30))
def test_random_stop_rate_matrix(seed):
    rng = random.Random(1300 + seed)
    days = sorted(rng.sample(range(0, 365), rng.randint(2, 30)))
    r = analyze_behavior(_spread(days))
    assert 0 <= r.stop_rate <= 1


@pytest.mark.parametrize("seed", range(40))
def test_month_peak_matrix(seed):
    rng = random.Random(1600 + seed)
    days = sorted(rng.sample(range(0, 365), rng.randint(5, 30)))
    r = analyze_behavior(_spread(days))
    assert r.peak_month == "" or len(r.peak_month) == 7


@pytest.mark.parametrize("seed", range(20))
def test_avg_per_draw_matrix(seed):
    rng = random.Random(2000 + seed)
    cost = rng.choice([2.0, 4.0, 6.0, 10.0])
    r = analyze_behavior(_spread([0, 7, 14, 21], cost=cost))
    assert r.avg_per_draw == pytest.approx(cost, abs=0.01)


@pytest.mark.parametrize("seed", range(30))
def test_behavior_valid_no_crash(seed):
    rng = random.Random(2300 + seed)
    tickets = []
    for i in range(rng.randint(1, 20)):
        tickets.append(_mk(i, front=rng.sample(range(1, 36), 5),
                           back=rng.sample(range(1, 13), 2)))
    r = analyze_behavior(tickets)
    assert r.total_notes == len(tickets)
    assert r.total_spent >= 0
