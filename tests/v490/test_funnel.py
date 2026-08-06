"""v4.9 P1 用户漏斗测试。"""
import pytest

from engine.user_experiment import (
    ExperimentEvent,
    ExperimentFunnel,
    ExperimentFunnelReport,
    build_funnel,
)


def _mk(events):
    """构造事件列表。"""
    out = []
    for (uid, name) in events:
        out.append(ExperimentEvent(event_name=name, user_id=uid,
                                   timestamp="2026-08-03T10:00:00"))
    return out


# ---- 基本漏斗 ----
def test_full_funnel_users_accumulate():
    events = _mk([
        ("u1", "app_install"), ("u1", "app_open"), ("u1", "ticket_saved"),
        ("u1", "draw_reminder_clicked"), ("u1", "claim_checked"),
        ("u1", "report_viewed"),
    ])
    report = ExperimentFunnel.build(events)
    assert report.total_installs == 1
    assert [s.users for s in report.stages] == [1, 1, 1, 1, 1, 1]


def test_empty_events():
    report = ExperimentFunnel.build([])
    assert report.total_installs == 0
    assert all(s.users == 0 for s in report.stages)


def test_install_only():
    events = _mk([("u1", "app_install")])
    report = ExperimentFunnel.build(events)
    assert [s.users for s in report.stages] == [1, 0, 0, 0, 0, 0]


def test_funnel_returns_report_type():
    assert isinstance(ExperimentFunnel.build(_mk([("u1", "app_install")])),
                      ExperimentFunnelReport)


@pytest.mark.parametrize("n_users", [1, 2, 5, 10])
def test_full_funnel_n_users(n_users):
    events = []
    for i in range(n_users):
        uid = f"u{i}"
        for name in ("app_install", "app_open", "ticket_saved",
                     "draw_reminder_clicked", "claim_checked", "report_viewed"):
            events.append(ExperimentEvent(event_name=name, user_id=uid,
                                          timestamp="2026-08-03T10:00:00"))
    report = ExperimentFunnel.build(events)
    assert report.total_installs == n_users
    assert all(s.users == n_users for s in report.stages)


# ---- 转化率/流失率 ----
def test_conversion_full():
    events = _mk([("u1", "app_install"), ("u1", "ticket_saved")])
    report = ExperimentFunnel.build(events)
    assert report.stages[0].conversion == 1.0   # 安装
    assert report.stages[2].conversion == 1.0   # 保存（相对安装）
    assert report.stages[1].users == 0          # 未打开


def test_conversion_half():
    events = _mk([("u1", "app_install"), ("u2", "app_install"),
                  ("u1", "app_open")])
    report = ExperimentFunnel.build(events)
    assert report.total_installs == 2
    assert report.stages[1].conversion == pytest.approx(0.5)


def test_drop_rate_between_stages():
    events = _mk([("u1", "app_install"), ("u2", "app_install"),
                  ("u1", "app_open"), ("u2", "app_open")])
    report = ExperimentFunnel.build(events)
    # 安装→打开无流失
    assert report.stages[1].drop_rate == 0.0


def test_drop_rate_half():
    events = _mk([("u1", "app_install"), ("u2", "app_install"),
                  ("u1", "app_open")])
    report = ExperimentFunnel.build(events)
    assert report.stages[1].drop_rate == pytest.approx(0.5)


# ---- 过滤 ----
def test_filter_experiment_id():
    events = [
        ExperimentEvent(event_name="app_install", user_id="u1",
                        experiment_id="exp-A", timestamp="2026-08-03T10:00:00"),
        ExperimentEvent(event_name="app_install", user_id="u2",
                        experiment_id="exp-B", timestamp="2026-08-03T10:00:00"),
        ExperimentEvent(event_name="app_open", user_id="u1",
                        experiment_id="exp-A", timestamp="2026-08-03T10:00:00"),
    ]
    report = ExperimentFunnel.build(events, experiment_id="exp-A")
    assert report.total_installs == 1
    assert report.stages[1].users == 1


def test_user_deduped_per_stage():
    events = _mk([("u1", "app_install"), ("u1", "app_open"),
                  ("u1", "app_open"), ("u1", "ticket_saved")])
    report = ExperimentFunnel.build(events)
    assert report.stages[1].users == 1  # 同一用户只计一次


# ---- 序列化 ----
def test_report_to_dict():
    report = ExperimentFunnel.build(_mk([("u1", "app_install")]))
    d = report.to_dict()
    assert "total_installs" in d
    assert len(d["stages"]) == 6


def test_report_to_text():
    report = ExperimentFunnel.build(_mk([("u1", "app_install")]))
    assert "用户漏斗" in report.to_text()


def test_build_funnel_helper():
    report = build_funnel(_mk([("u1", "app_install")]))
    assert report.total_installs == 1


# ---- 六阶段标签顺序 ----
def test_stage_order():
    report = ExperimentFunnel.build(_mk([("u1", "app_install")]))
    labels = [s.label for s in report.stages]
    assert labels == ["安装", "首次打开", "保存彩票", "开奖提醒", "兑奖查看", "周报查看"]
