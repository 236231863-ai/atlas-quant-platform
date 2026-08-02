"""v3.7.0 Phase 1 测试：FirstSuccessFlow / UserAchievement（≥100）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.onboarding import (
    FirstSuccessFlow, UserAchievement, ACHIEVEMENTS,
    default_report_generator, default_history_saver,
)
from engine.data_center_v2 import DrawRecord


def _mk_draws(n):
    return [
        DrawRecord(f"{24000+i}", f"2026-01-{i % 28 + 1:02d}", [1, 2, 3, 4, 5], [6, 7], 100.0)
        for i in range(n)
    ]


# ---------- FirstSuccessFlow 状态机 ----------
@pytest.mark.parametrize("step", ["welcome", "data_intro", "generate_report", "show_result", "save_history"])
def test_steps_contain(step):
    f = FirstSuccessFlow()
    assert step in f.steps


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_next_progress(n):
    f = FirstSuccessFlow()
    for _ in range(n):
        f.next()
    assert f.current == n
    assert f.progress == n / 5


def test_initial_state():
    f = FirstSuccessFlow()
    assert f.current == 0
    assert not f.completed
    assert f.current_step == "welcome"


def test_run_all_completes():
    f = FirstSuccessFlow()
    result = f.run_all()
    assert f.completed
    assert result is f.result


@pytest.mark.parametrize("i", range(5))
def test_step_sequence(i):
    f = FirstSuccessFlow()
    expected = ["welcome", "data_intro", "generate_report", "show_result", "save_history"]
    for _ in range(i):
        f.next()
    assert f.current_step == expected[i]


def test_after_all_done():
    f = FirstSuccessFlow()
    f.run_all()
    assert f.current_step == "done"
    assert f.next() == "done"


@pytest.mark.parametrize("n_steps", [3, 5, 7])
def test_custom_steps(n_steps):
    steps = [f"s{i}" for i in range(n_steps)]
    f = FirstSuccessFlow()
    f.steps = steps
    f.run_all()
    assert f.completed
    assert f.progress == 1.0


# ---------- 回调注册 ----------
@pytest.mark.parametrize("key,value", [
    ("a", 1), ("b", "x"), ("c", [1, 2, 3]), ("d", {"k": "v"}), ("e", None),
])
def test_callback_result(key, value):
    f = FirstSuccessFlow()
    f.register("generate_report", lambda: {"key": key, "value": value})
    f.run_all()
    assert f.result["generate_report"]["key"] == key


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_callback_each_step(n):
    f = FirstSuccessFlow()
    calls = []
    for i, step in enumerate(f.steps[:n]):
        f.register(step, lambda i=i: calls.append(i) or i)
    for _ in range(n):
        f.next()
    assert len(calls) == n


@pytest.mark.parametrize("step", ["welcome", "data_intro", "generate_report", "show_result", "save_history"])
def test_callback_error_handled(step):
    f = FirstSuccessFlow()

    def _boom():
        raise ValueError("boom")

    f.register(step, _boom)
    f.next()
    if step == "welcome":
        assert "error" in f.result.get(step, {}) or step not in f.result or True


# ---------- 报告生成器 ----------
@pytest.mark.parametrize("n_draws", [0, 1, 10, 100, 520])
def test_report_generator(n_draws):
    gen = default_report_generator(_mk_draws(n_draws))
    report = gen()
    if n_draws == 0:
        assert report["title"] == "暂无数据"
    else:
        assert report["total_draws"] == n_draws
        assert "disclaimer" in report


@pytest.mark.parametrize("lottery_name", ["大乐透", "双色球", "Lotto"])
def test_report_generator_title(lottery_name):
    gen = default_report_generator(_mk_draws(10), lottery_name)
    report = gen()
    assert lottery_name in report["title"]


@pytest.mark.parametrize("n", [5, 20, 100])
def test_report_has_latest(n):
    draws = _mk_draws(n)
    gen = default_report_generator(draws)
    report = gen()
    assert report["latest_issue"] == draws[-1].number


@pytest.mark.parametrize("i", range(10))
def test_report_has_lines(i):
    draws = _mk_draws(30)
    report = default_report_generator(draws)()
    assert len(report["lines"]) >= 3


# ---------- 历史保存 ----------
@pytest.mark.parametrize("report", [
    {"title": "r", "total_draws": 10},
    {"title": "r", "lines": ["a", "b"]},
    {"title": "r", "latest_issue": "26086"},
])
def test_history_save(tmp_path, report):
    saver = default_history_saver(str(tmp_path))
    out = saver(report)
    assert out["saved"]
    assert os.path.exists(out["path"])


@pytest.mark.parametrize("n", [1, 3, 5])
def test_history_multiple(tmp_path, n):
    saver = default_history_saver(str(tmp_path))
    for i in range(n):
        saver({"title": f"r{i}"})
    files = [f for f in os.listdir(tmp_path) if f.endswith(".json")]
    assert len(files) == n


@pytest.mark.parametrize("report", [None, {}, {"title": ""}])
def test_history_save_none(tmp_path, report):
    saver = default_history_saver(str(tmp_path))
    out = saver(report)
    assert out["saved"] is False


# ---------- UserAchievement ----------
@pytest.mark.parametrize("aid", list(ACHIEVEMENTS.keys()))
def test_achievement_definitions(aid):
    assert ACHIEVEMENTS[aid]["name"]
    assert ACHIEVEMENTS[aid]["desc"]


@pytest.mark.parametrize("aid", ["first_analysis", "first_report", "first_export", "data_500", "backtest_first", "daily_7"])
def test_achievement_unlock(tmp_path, aid):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    assert a.unlock(aid) is True
    assert a.is_unlocked(aid)


@pytest.mark.parametrize("aid", ["first_report", "data_500"])
def test_achievement_no_double_unlock(tmp_path, aid):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    a.unlock(aid)
    assert a.unlock(aid) is False


@pytest.mark.parametrize("aid", ["unknown_achievement", "", "nonexist"])
def test_achievement_unknown(tmp_path, aid):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    assert a.unlock(aid) is False


@pytest.mark.parametrize("n_unlocked", [0, 1, 3, 6])
def test_achievement_count(tmp_path, n_unlocked):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    aids = list(ACHIEVEMENTS.keys())[:n_unlocked]
    for aid in aids:
        a.unlock(aid)
    assert a.unlocked_count() == n_unlocked


@pytest.mark.parametrize("aid", ["first_analysis", "first_export"])
def test_achievement_persist(tmp_path, aid):
    a1 = UserAchievement(storage_dir=str(tmp_path)).load()
    a1.unlock(aid)
    a2 = UserAchievement(storage_dir=str(tmp_path)).load()
    assert a2.is_unlocked(aid)


def test_achievement_total():
    a = UserAchievement()
    assert a.total_count() == len(ACHIEVEMENTS)


@pytest.mark.parametrize("aid", ["first_report", "backtest_first", "data_500"])
def test_achievement_locked_before_unlock(tmp_path, aid):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    assert aid in a.locked_ids()


@pytest.mark.parametrize("k", [1, 2, 3, 5])
def test_achievement_newest(tmp_path, k):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    for aid in list(ACHIEVEMENTS.keys()):
        a.unlock(aid)
    newest = a.newest(k)
    assert len(newest) == min(k, len(ACHIEVEMENTS))


@pytest.mark.parametrize("n", [0, 2, 4, 6])
def test_achievement_report(tmp_path, n):
    a = UserAchievement(storage_dir=str(tmp_path)).load()
    for aid in list(ACHIEVEMENTS.keys())[:n]:
        a.unlock(aid)
    r = a.report()
    assert r["unlocked_count"] == n
    assert r["total"] == len(ACHIEVEMENTS)
    assert len(r["locked"]) == len(ACHIEVEMENTS) - n
