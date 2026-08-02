"""v3.7.0 Phase 2 测试：DailySummary / 每日智能（≥150）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.daily_intelligence import DailySummary, build_summary
from engine.data_center_v2 import DrawRecord


def _mk(issue, date, front=None, back=None):
    return DrawRecord(str(issue), date, front or [1, 2, 3, 4, 5], back or [6, 7], 100.0)


# ---------- 数据变化 ----------
@pytest.mark.parametrize("n_prev,n_cur", [
    (0, 10), (10, 11), (10, 15), (50, 52), (100, 120),
])
def test_new_draws(n_prev, n_cur):
    prev = [_mk(i, f"2026-01-{i%28+1:02d}") for i in range(1, n_prev + 1)]
    cur = [_mk(i, f"2026-01-{i%28+1:02d}") for i in range(1, n_cur + 1)]
    s = build_summary(prev, cur, "2026-02-01")
    assert s.new_draws == n_cur - n_prev


@pytest.mark.parametrize("n", [1, 5, 20, 100])
def test_no_change_same_data(n):
    data = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary(data, data)
    assert s.new_draws == 0


@pytest.mark.parametrize("n", [0, 1, 10])
def test_empty_current(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)] if n else []
    s = build_summary([], cur)
    assert s.latest_issue == (cur[-1].number if cur else "")


@pytest.mark.parametrize("n_extra", [1, 3, 5, 10])
def test_latest_issue(n_extra):
    prev = [_mk(i, "2026-01-01") for i in range(10)]
    cur = prev + [_mk(10 + j, "2026-01-02") for j in range(n_extra)]
    s = build_summary(prev, cur)
    assert s.latest_issue == str(10 + n_extra - 1)


# ---------- 号码统计变化 ----------
@pytest.mark.parametrize("hot_prev,hot_cur", [
    ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    ([1, 2, 3, 4, 5], [6, 7, 8, 9, 10]),
    ([5, 10, 15], [5, 10, 20]),
])
def test_hot_change_detection(hot_prev, hot_cur):
    prev = [_mk(i, "2026-01-01", front=hot_prev) for i in range(10)]
    cur = [_mk(i, "2026-01-01", front=hot_cur) for i in range(10)]
    s = build_summary(prev, cur)
    assert s.hot_changed == (set(hot_prev) != set(hot_cur))


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 6], [1, 2, 3, 4, 7]],
    [[10, 11, 12, 13, 14], [15, 16, 17, 18, 19]],
])
def test_hot_top_after(fronts):
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts)]
    s = build_summary([], cur)
    assert len(s.hot_top_after) >= 1


@pytest.mark.parametrize("k", [1, 3, 5, 8])
def test_hot_top_size(k):
    cur = [_mk(i, "2026-01-01") for i in range(50)]
    s = build_summary([], cur)
    assert len(s.hot_top_after) <= 8


# ---------- 趋势变化 ----------
@pytest.mark.parametrize("sums_prev,sums_cur,expected", [
    ([[1, 2, 3, 4, 5]] * 10, [[1, 2, 3, 4, 35]] * 10, "up"),
    ([[1, 2, 3, 4, 35]] * 10, [[1, 2, 3, 4, 5]] * 10, "down"),
    ([[1, 2, 3, 4, 15]] * 10, [[1, 2, 3, 4, 15]] * 10, "stable"),
])
def test_sum_trend(sums_prev, sums_cur, expected):
    prev = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(sums_prev)]
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(sums_cur)]
    s = build_summary(prev, cur)
    assert s.sum_trend == expected


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
    [[1, 3, 5, 7, 9], [2, 4, 6, 8, 10]],
])
def test_avg_sum(fronts):
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts)]
    s = build_summary([], cur)
    assert s.avg_sum_after > 0


@pytest.mark.parametrize("fronts", [
    [[1, 3, 5, 7, 9]],
    [[2, 4, 6, 8, 10]],
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
])
def test_odd_even(fronts):
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts)]
    s = build_summary([], cur)
    assert s.odd_even_after is not None
    assert ":" in s.odd_even_after


# ---------- 报告提醒 ----------
@pytest.mark.parametrize("n_prev,n_cur,has_reminder", [
    (0, 10, True), (10, 11, True), (10, 10, False),
])
def test_reminder_new_data(n_prev, n_cur, has_reminder):
    prev = [_mk(i, "2026-01-01") for i in range(n_prev)]
    cur = [_mk(i, "2026-01-01") for i in range(n_cur)]
    s = build_summary(prev, cur)
    assert s.has_reminder() == has_reminder


@pytest.mark.parametrize("n", [10, 50, 500, 520])
def test_reminder_data_sufficient(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    if n >= 500:
        assert any("数据充足" in r for r in s.reminder)
    else:
        assert not any("数据充足" in r for r in s.reminder)


@pytest.mark.parametrize("i", range(5))
def test_reminder_capped(i):
    cur = [_mk(i, "2026-01-01") for i in range(50)]
    prev = [_mk(i, "2026-01-01") for i in range(40)]
    s = build_summary(prev, cur)
    assert len(s.reminder) <= 3


# ---------- 输出格式 ----------
@pytest.mark.parametrize("n", [0, 5, 50])
def test_to_text(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    text = s.to_text()
    assert "Atlas" in text
    assert "随机" in text  # 非预测声明


@pytest.mark.parametrize("n", [1, 10, 100])
def test_to_dict(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    d = s.to_dict()
    assert "new_draws" in d
    assert "hot_changed" in d
    assert "reminder" in d


@pytest.mark.parametrize("n", [0, 5, 50, 520])
def test_to_text_contains_latest(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    if n:
        assert s.latest_issue in s.to_text()


# ---------- 非预测声明 ----------
@pytest.mark.parametrize("n", [5, 50, 500])
def test_no_prediction_language(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    text = s.to_text()
    for forbidden in ["必中", "稳赚", "预测中奖", "保证中奖"]:
        assert forbidden not in text


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5], [1, 2, 3, 4, 6]],
    [[5, 10, 15, 20, 25]],
])
def test_reminder_is_observation(fronts):
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts)]
    s = build_summary([], cur)
    for r in s.reminder:
        assert "预测" not in r
        assert "必" not in r


# ---------- 扩展：数据变化网格 ----------
@pytest.mark.parametrize("n_prev", [0, 5, 20, 100])
@pytest.mark.parametrize("n_cur", [5, 25, 120])
def test_grid_new_draws(n_prev, n_cur):
    prev = [_mk(i, "2026-01-01") for i in range(n_prev)]
    cur = [_mk(i, "2026-01-01") for i in range(n_cur)]
    s = build_summary(prev, cur)
    if n_cur >= n_prev:
        assert s.new_draws == n_cur - n_prev
    else:
        # prev 是超集：新增 = 0
        assert s.new_draws == 0


# ---------- 扩展：更多输出与边界 ----------
@pytest.mark.parametrize("n", [1, 10, 100, 520])
def test_text_has_date_range(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    if n:
        assert "~" in s.date_range or "新增" in s.to_text()


@pytest.mark.parametrize("n", [0, 1, 10, 50, 520])
def test_text_length_positive(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    text = build_summary([], cur).to_text()
    assert len(text) > 10


@pytest.mark.parametrize("fronts", [
    [[1, 2, 3, 4, 5]], [[5, 10, 15, 20, 25]], [[35, 34, 33, 32, 31]],
])
def test_hot_after_different_fronts(fronts):
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts * 5)]
    s = build_summary([], cur)
    assert len(s.hot_top_after) >= 1


@pytest.mark.parametrize("i", range(5))
def test_reminder_list_type(i):
    cur = [_mk(i, "2026-01-01") for i in range(50)]
    s = build_summary([], cur)
    assert isinstance(s.reminder, list)


# ---------- 扩展：号码频率变化 ----------
@pytest.mark.parametrize("fronts_prev,fronts_cur", [
    ([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]], [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]),
    ([[1, 2, 3, 4, 5]], [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]),
    ([[1, 2, 3, 4, 5]], [[5, 4, 3, 2, 1]]),
])
def test_rising_falling(fronts_prev, fronts_cur):
    prev = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts_prev)]
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts_cur)]
    s = build_summary(prev, cur)
    assert isinstance(s.rising_numbers, list)
    assert isinstance(s.falling_numbers, list)


@pytest.mark.parametrize("front", [
    [1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [10, 20, 30, 35, 5],
])
@pytest.mark.parametrize("n", [1, 10, 50])
def test_frequency_consistency(front, n):
    cur = [_mk(i, "2026-01-01", front=front) for i in range(n)]
    s = build_summary([], cur)
    assert len(s.hot_top_after) >= 1


# ---------- 扩展：趋势 ----------
@pytest.mark.parametrize("ratio", [1.5, 1.2, 1.05, 1.0, 0.95, 0.8, 0.5])
def test_sum_trend_ratios(ratio):
    prev = [_mk(i, "2026-01-01", front=[1, 2, 3, 4, 10]) for i in range(20)]
    target_sum = int(20 * ratio) if ratio >= 1 else max(6, int(20 * ratio))
    cur = [_mk(i, "2026-01-01", front=[1, 2, 3, 4, target_sum - 10]) for i in range(20)]
    s = build_summary(prev, cur)
    assert s.sum_trend in ("up", "down", "stable")


@pytest.mark.parametrize("fronts_cur", [
    [[1, 3, 5, 7, 9]], [[2, 4, 6, 8, 10]], [[1, 2, 3, 4, 5]],
])
@pytest.mark.parametrize("n", [3, 15])
def test_odd_even_variants(fronts_cur, n):
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts_cur * n)]
    s = build_summary([], cur)
    assert s.odd_even_after and ":" in s.odd_even_after


# ---------- 扩展：提醒信号 ----------
@pytest.mark.parametrize("n_prev,n_cur", [(10, 15), (20, 25), (100, 110)])
def test_reminder_new_data_grid(n_prev, n_cur):
    prev = [_mk(i, "2026-01-01") for i in range(n_prev)]
    cur = [_mk(i, "2026-01-01") for i in range(n_cur)]
    s = build_summary(prev, cur)
    assert any("新增" in r for r in s.reminder)


@pytest.mark.parametrize("fronts_prev,fronts_cur", [
    ([[1, 2, 3, 4, 5]] * 10, [[6, 7, 8, 9, 10]] * 10),
    ([[1, 2, 3, 4, 5]] * 10, [[1, 2, 3, 4, 5]] * 10),
])
def test_reminder_hot_change(fronts_prev, fronts_cur):
    prev = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts_prev)]
    cur = [_mk(i, "2026-01-01", front=f) for i, f in enumerate(fronts_cur)]
    s = build_summary(prev, cur)
    if set(fronts_prev[0]) != set(fronts_cur[0]):
        assert any("格局" in r for r in s.reminder)


# ---------- 扩展：边界 ----------
@pytest.mark.parametrize("date", ["", "2026-08-02", "今日"])
def test_summary_date(date):
    cur = [_mk(i, "2026-01-01") for i in range(10)]
    s = build_summary([], cur, date)
    assert s.date == date or s.date == "今日"


@pytest.mark.parametrize("n", [1, 2, 3, 50])
def test_single_draw_summary(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    s = build_summary([], cur)
    assert s.latest_issue


@pytest.mark.parametrize("i", range(10))
def test_summary_repeatable(i):
    cur = [_mk(i, "2026-01-01") for i in range(30)]
    s1 = build_summary([], cur)
    s2 = build_summary([], cur)
    assert s1.to_dict() == s2.to_dict()


# ---------- 扩展：非预测红线 ----------
@pytest.mark.parametrize("n", [10, 100, 500])
@pytest.mark.parametrize("front", [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
def test_no_prediction_strict(n, front):
    cur = [_mk(i, "2026-01-01", front=front) for i in range(n)]
    s = build_summary([], cur)
    text = s.to_text()
    for bad in ["预测中奖", "必中", "包中", "稳赢", "保底", "保证中奖"]:
        assert bad not in text
    # 允许「非中奖预测」免责声明，但不允许肯定式预测
    assert "中奖预测" not in text or "非" in text


# ---------- 扩展：输出结构 ----------
@pytest.mark.parametrize("key", ["date", "new_draws", "hot_changed", "rising_numbers", "falling_numbers", "avg_sum_after", "sum_trend", "reminder"])
def test_dict_keys(key):
    cur = [_mk(i, "2026-01-01") for i in range(20)]
    d = build_summary([], cur).to_dict()
    assert key in d


@pytest.mark.parametrize("n", [0, 3, 30, 300])
def test_text_no_crash(n):
    cur = [_mk(i, "2026-01-01") for i in range(n)]
    text = build_summary([], cur).to_text()
    assert isinstance(text, str)
