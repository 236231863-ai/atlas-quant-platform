"""v4.9 P3 测试：REAL/SIM 隔离 + 真实数据导入 + 反馈问卷。

验证核心：真实用户数据与模拟数据禁止混合统计。
"""
import json
import os

import pytest

from engine.user_experiment import (
    ExperimentTracker,
    ExperimentFunnel,
    ExperimentRetentionBuilder,
    ValidationMetricsBuilder,
    UserBehaviorSimulator,
    SimConfig,
    SOURCE_REAL,
    SOURCE_SIMULATION,
    normalize_source,
    UserFeedbackSurvey,
)


@pytest.fixture()
def exp_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    return str(tmp_path)


# ---------- normalize_source ----------
@pytest.mark.parametrize("src,expect", [
    ("desktop", SOURCE_REAL),
    ("REAL", SOURCE_REAL),
    ("", SOURCE_REAL),
    ("SIMULATION", SOURCE_SIMULATION),
    (None, SOURCE_REAL),
])
def test_normalize_source(src, expect):
    assert normalize_source(src) == expect


# ---------- REAL/SIM 事件分离 ----------
def test_simulator_marks_simulation(exp_storage):
    """模拟器事件必须标记 SIMULATION。"""
    sim = UserBehaviorSimulator(seed=1)
    sim.run(sim.import_users(["s0"]), SimConfig(days=1), experiment_id="sim")
    t = ExperimentTracker()
    assert len(t.simulation_events()) > 0
    assert len(t.real_events()) == 0  # 无真实事件混入


def test_record_default_is_real(exp_storage):
    """默认 record（desktop source）视为真实。"""
    t = ExperimentTracker()
    t.record("app_open", "u1")
    assert len(t.real_events()) == 1
    assert len(t.simulation_events()) == 0


def test_import_real_events_marks_real(exp_storage, tmp_path):
    """从埋点文件导入的事件标记 REAL。"""
    p = tmp_path / "analytics.jsonl"
    p.write_text(
        json.dumps({"event_name": "app_open", "user_id": "realA",
                    "timestamp": "2026-08-01T10:00:00"}) + "\n" +
        json.dumps({"event_name": "ticket_saved", "user_id": "realA",
                    "timestamp": "2026-08-01T10:05:00"}) + "\n",
        encoding="utf-8",
    )
    t = ExperimentTracker()
    n = t.import_real_events(str(p), experiment_id="real-x")
    assert n == 2
    assert len(t.real_events("real-x")) == 2
    assert len(t.simulation_events("real-x")) == 0


def test_import_ignores_unknown_events(exp_storage, tmp_path):
    """未知事件名忽略。"""
    p = tmp_path / "analytics.jsonl"
    p.write_text(json.dumps({"event_name": "not_an_event", "user_id": "u"}) + "\n",
                 encoding="utf-8")
    t = ExperimentTracker()
    assert t.import_real_events(str(p)) == 0


def test_import_missing_file(exp_storage):
    assert ExperimentTracker().import_real_events("nope.jsonl") == 0


def test_event_alias_mapping(exp_storage, tmp_path):
    """旧事件名映射到实验事件集。"""
    p = tmp_path / "analytics.jsonl"
    p.write_text(json.dumps({"event_name": "app_opened", "user_id": "u"}) + "\n",
                 encoding="utf-8")
    t = ExperimentTracker()
    t.import_real_events(str(p))
    evs = t.real_events()
    assert evs[0].event_name == "app_open"  # app_opened → app_open


# ---------- 隔离统计 ----------
def test_funnel_default_real_only(exp_storage):
    """漏斗默认只统计真实（不混 SIM）。"""
    t = ExperimentTracker()
    t.record("app_install", "real1")
    t.record("app_open", "real1")
    # 加模拟事件
    sim = UserBehaviorSimulator(seed=2)
    sim.run(sim.import_users(["s0"]), SimConfig(days=0), experiment_id="sim")
    f = ExperimentFunnel.build()  # 默认 source=REAL
    assert f.total_installs == 1  # 只有 real1


def test_funnel_source_none_all(exp_storage):
    """source=None 统计全部（测试用）。"""
    t = ExperimentTracker()
    t.record("app_install", "real1")
    sim = UserBehaviorSimulator(seed=3)
    sim.run(sim.import_users(["s0"]), SimConfig(days=0), experiment_id="sim")
    f = ExperimentFunnel.build(source=None)
    assert f.total_installs == 2


def test_metrics_real_only(exp_storage):
    """指标默认只统计真实。"""
    t = ExperimentTracker()
    t.record("app_install", "real1")
    t.record("ticket_saved", "real1")
    sim = UserBehaviorSimulator(seed=4)
    sim.run(sim.import_users(["s0"]), SimConfig(days=0), experiment_id="sim")
    m = ValidationMetricsBuilder.build(source=SOURCE_REAL)
    assert m.walu == 1
    assert m.installs == 1


# ---------- 反馈问卷 ----------
def test_feedback_submit(exp_storage):
    s = UserFeedbackSurvey()
    fb = s.submit("userA", "自动兑奖", "操作复杂")
    assert fb is not None
    assert s.count() == 1


def test_feedback_invalid_use_reason(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit("u", "非法原因") is None
    assert s.count() == 0


def test_feedback_invalid_uninstall(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit("u", "自动提醒", "非法卸载原因") is None


def test_feedback_distribution(exp_storage):
    s = UserFeedbackSurvey()
    s.submit("a", "自动兑奖")
    s.submit("b", "自动兑奖")
    s.submit("c", "自动提醒")
    d = s.distribution("use_reason")
    assert d["自动兑奖"] == 2
    assert d["自动提醒"] == 1


def test_feedback_top_reason(exp_storage):
    s = UserFeedbackSurvey()
    s.submit("a", "自动兑奖")
    s.submit("b", "自动提醒")
    assert s.top_use_reason() == "自动兑奖"
    assert s.top_uninstall_reason() == "（暂无反馈）"


def test_feedback_persist_reload(exp_storage):
    s = UserFeedbackSurvey()
    s.submit("a", "管理投入", "没中奖")
    s2 = UserFeedbackSurvey()  # 重新加载
    assert s2.count() == 1
    assert s2.all()[0].use_reason == "管理投入"


@pytest.mark.parametrize("reason", ["自动提醒", "自动兑奖", "管理投入", "查看历史", "其他"])
def test_feedback_valid_use_reasons(exp_storage, reason):
    s = UserFeedbackSurvey()
    assert s.submit("u", reason) is not None


@pytest.mark.parametrize("reason", ["没必要", "操作复杂", "没中奖", "提醒无用", "数据问题", "其他"])
def test_feedback_valid_uninstall_reasons(exp_storage, reason):
    s = UserFeedbackSurvey()
    assert s.submit("u", "自动提醒", reason) is not None


def test_feedback_clear(exp_storage):
    s = UserFeedbackSurvey()
    s.submit("a", "自动兑奖")
    s.clear()
    assert s.count() == 0


def test_feedback_summary(exp_storage):
    s = UserFeedbackSurvey()
    s.submit("a", "自动兑奖", "操作复杂")
    summary = s.summary()
    assert summary["total"] == 1
    assert "use_reasons" in summary
    assert "uninstall_reasons" in summary
