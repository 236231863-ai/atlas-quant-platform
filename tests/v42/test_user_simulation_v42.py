"""v4.2 Phase 6：用户留存模拟测试（50 用户）。"""
from __future__ import annotations

import pytest

from engine.user_simulation import (
    DEFAULT_USERS,
    SIM_DAYS,
    SimulatedUser,
    UserSimulation,
)


# ---------- 生成 ----------
def test_generate_default_50():
    users = UserSimulation.generate()
    assert len(users) == DEFAULT_USERS == 50


@pytest.mark.parametrize("n", [1, 10, 50, 100])
def test_generate_n(n):
    users = UserSimulation.generate(n=n)
    assert len(users) == n


def test_deterministic_same_seed():
    a = UserSimulation.generate(seed=42)
    b = UserSimulation.generate(seed=42)
    assert [u.to_dict() for u in a] == [u.to_dict() for u in b]


def test_different_seed():
    a = UserSimulation.generate(seed=1)
    b = UserSimulation.generate(seed=2)
    assert a[0].to_dict() != b[0].to_dict()


def test_user_type():
    u = UserSimulation.generate(n=1)[0]
    assert isinstance(u, SimulatedUser)


def test_days_range():
    users = UserSimulation.generate(n=10)
    for u in users:
        assert max(u.open_days) <= SIM_DAYS
        assert all(0 <= d <= SIM_DAYS for d in u.open_days)


# ---------- 轨迹完整性 ----------
def test_first_opened_day0():
    users = UserSimulation.generate(n=50)
    for u in users:
        assert u.first_opened_day == 0
        assert 0 in u.open_days


def test_funnel_chain():
    """保存→提醒→兑奖→复盘 链条单调。"""
    users = UserSimulation.generate(n=50)
    for u in users:
        if u.reviewed:
            assert u.claimed
        if u.claimed:
            assert u.reminded
        if u.reminded:
            assert u.saved
        if u.saved:
            assert u.first_saved_day >= 0


def test_order_days():
    users = UserSimulation.generate(n=50)
    for u in users:
        if u.reviewed:
            assert u.first_claimed_day <= u.first_reviewed_day  # 兑奖当天可复盘
        if u.claimed:
            assert u.first_reminded_day <= u.first_claimed_day  # 提醒当天可兑奖
        if u.reminded:
            assert u.first_saved_day < u.first_reminded_day  # 提醒严格在保存后


# ---------- 汇总统计 ----------
def test_stats_total():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    assert stats["total"] == 50


def test_stats_first_open_100():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    assert stats["first_open"] == 1.0


def test_stats_empty():
    stats = UserSimulation.cohort_stats([])
    assert stats["total"] == 0


def test_stats_rates_range():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    for k in ("save_rate", "remind_rate", "claim_rate", "review_rate",
              "retention_d7", "retention_d30"):
        assert 0 <= stats[k] <= 1


def test_stats_funnel_monotone():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    f = stats["funnel"]
    assert f["opened"] >= f["saved"] >= f["reminded"] >= f["claimed"] >= f["reviewed"]


def test_retention_decay():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    assert stats["retention_d30"] <= stats["retention_d7"] <= 1.0


@pytest.mark.parametrize("seed", range(10))
def test_stats_seed_stable(seed):
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50, seed=seed))
    # 保存率应在合理区间（0.2~0.9）
    assert 0.2 <= stats["save_rate"] <= 0.95
    # 漏斗单调
    f = stats["funnel"]
    assert f["opened"] >= f["saved"] >= f["reminded"] >= f["claimed"] >= f["reviewed"]
    # 30 天留存应在合理区间
    assert 0.02 <= stats["retention_d30"] <= 0.9


@pytest.mark.parametrize("seed", range(10))
def test_stats_larger_sample(seed):
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=200, seed=seed))
    assert 0.2 <= stats["save_rate"] <= 0.95


# ---------- 输出 ----------
def test_user_to_dict():
    u = UserSimulation.generate(n=1)[0]
    d = u.to_dict()
    assert set(d) >= {"user_id", "first_opened_day", "first_saved_day",
                      "first_reminded_day", "first_claimed_day", "first_reviewed_day",
                      "open_days", "saved_count", "claimed_count"}
    assert isinstance(d["open_days"], list)


def test_funnel_text():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    t = UserSimulation.funnel_text(stats)
    assert "总用户：50" in t
    assert "第一次保存" in t
    assert "D7 留存" in t
    assert "D30 留存" in t


def test_funnel_text_percent():
    stats = UserSimulation.cohort_stats(UserSimulation.generate(n=50))
    t = UserSimulation.funnel_text(stats)
    assert "%" in t


# ---------- 属性 ----------
def test_user_properties():
    u = SimulatedUser(user_id=0, first_saved_day=2, first_reminded_day=3,
                      first_claimed_day=4, first_reviewed_day=5)
    assert u.saved and u.reminded and u.claimed and u.reviewed


def test_user_properties_false():
    u = SimulatedUser(user_id=0)
    assert not u.saved
    assert not u.reminded
    assert not u.claimed
    assert not u.reviewed


def test_user_retention_props():
    u = SimulatedUser(user_id=0, open_days=[0, 7, 30])
    assert u.opened_at_d7
    assert u.opened_at_d30


def test_user_retention_props_false():
    u = SimulatedUser(user_id=0, open_days=[0, 1])
    assert not u.opened_at_d7
    assert not u.opened_at_d30


@pytest.mark.parametrize("seed", range(10))
def test_save_then_remind(seed):
    """保存用户中大多数收到提醒（80% 期望，抽样阈值 0.4）。"""
    users = UserSimulation.generate(n=100, seed=seed)
    saved_users = [u for u in users if u.saved]
    if saved_users:
        reminded = sum(1 for u in saved_users if u.reminded)
        assert reminded / len(saved_users) > 0.4


@pytest.mark.parametrize("seed", range(10))
def test_remind_then_claim(seed):
    """提醒用户中大多数完成兑奖（60% 期望，抽样阈值 0.4）。"""
    users = UserSimulation.generate(n=100, seed=seed)
    reminded_users = [u for u in users if u.reminded]
    if reminded_users:
        claimed = sum(1 for u in reminded_users if u.claimed)
        assert claimed / len(reminded_users) > 0.4


# ---------- 红线：不诱导 ----------
def test_simulation_no_induction():
    users = UserSimulation.generate(n=50)
    for u in users:
        d = u.to_dict()
        assert isinstance(d["open_days"], list)
    # 模拟仅统计行为，无任何预测/诱导字段
    keys = set(SimulatedUser(user_id=0).to_dict())
    for bad in ("prediction", "win_guarantee", "hot_number", "recommend"):
        assert bad not in keys
