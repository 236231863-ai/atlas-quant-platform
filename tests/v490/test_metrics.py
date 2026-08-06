"""v4.9 P1 验证指标测试（Q1-Q4 + WALU）。"""
import pytest

from engine.user_experiment import (
    ExperimentEvent,
    ValidationMetric,
    ValidationMetrics,
    ValidationMetricsBuilder,
    build_metrics,
)


def _ev(name, uid="u1", exp="default"):
    return ExperimentEvent(event_name=name, user_id=uid, experiment_id=exp,
                           timestamp="2026-08-03T10:00:00")


def _flow(uid="u1", save=True, reminder=True, claim=True,
          report=True, premium_view=False, premium_click=False):
    """构造一条完整用户流。"""
    evs = [_ev("app_install", uid), _ev("app_open", uid)]
    if save:
        evs.append(_ev("ticket_saved", uid))
    if reminder:
        evs.append(_ev("draw_reminder_clicked", uid))
    if claim:
        evs.append(_ev("claim_checked", uid))
    if report:
        evs.append(_ev("report_viewed", uid))
    if premium_view:
        evs.append(_ev("premium_view", uid))
    if premium_click:
        evs.append(_ev("premium_click", uid))
    return evs


# ---- Q1 安装完成率 ----
def test_q1_full():
    evs = [_ev("app_install", "u1"), _ev("app_open", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "install_complete")
    assert v.value == 1.0


def test_q1_half():
    evs = [_ev("app_install", "u1"), _ev("app_install", "u2"),
           _ev("app_open", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "install_complete")
    assert v.value == pytest.approx(0.5)


def test_q1_no_install():
    evs = [_ev("app_open", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "install_complete")
    assert v.value == 0.0


# ---- Q2 首次建档率 ----
def test_q2_full():
    evs = [_ev("app_install", "u1"), _ev("ticket_saved", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "first_save_rate")
    assert v.value == 1.0
    assert v.passed is True


def test_q2_below_target():
    evs = [_ev("app_install", "u1"), _ev("app_install", "u2"),
           _ev("ticket_saved", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "first_save_rate")
    assert v.value == pytest.approx(0.5)
    assert v.passed is True  # ≥50%


def test_q2_fail():
    evs = [_ev("app_install", "u1"), _ev("app_install", "u2"),
           _ev("app_install", "u3"), _ev("ticket_saved", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "first_save_rate")
    assert v.passed is False


# ---- Q3 留存 ----
def test_q3_d1_pass():
    evs = [_ev("app_open", "u1", exp="default"),
           ExperimentEvent(event_name="app_open", user_id="u1",
                           timestamp="2026-08-04T10:00:00")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "d1")
    assert v.value == 1.0 and v.passed is True


def test_q3_d1_fail():
    evs = [_ev("app_open", "u1", exp="default")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "d1")
    assert v.passed is False


def test_q3_d7_pass():
    evs = [_ev("app_open", "u1", exp="default"),
           ExperimentEvent(event_name="app_open", user_id="u1",
                           timestamp="2026-08-10T10:00:00")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "d7")
    assert v.passed is True


# ---- 提醒点击率 ----
def test_reminder_rate_full():
    evs = [_ev("app_install", "u1"), _ev("draw_reminder_clicked", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "reminder_click_rate")
    assert v.value == 1.0


def test_reminder_rate_below():
    evs = [_ev("app_install", "u1"), _ev("app_install", "u2"),
           _ev("app_install", "u3"), _ev("app_install", "u4"),
           _ev("draw_reminder_clicked", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "reminder_click_rate")
    assert v.value == pytest.approx(0.25)
    assert v.passed is False


# ---- Q4 付费意愿 ----
def test_q4_pay_willing():
    evs = _flow(premium_view=True, premium_click=True)
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "pay_willing")
    assert v.value == 1.0
    assert v.passed is True


def test_q4_no_click():
    evs = _flow(premium_view=True)
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "pay_willing")
    assert v.value == 0.0


def test_q4_no_view():
    evs = _flow()
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == "pay_willing")
    assert v.value == 0.0


# ---- 北极星 WALU ----
def test_walu_saved():
    evs = _flow(save=True, reminder=False, claim=False)
    m = ValidationMetricsBuilder.build(evs)
    assert m.walu == 1


def test_walu_claimed():
    evs = _flow(save=False, reminder=False, claim=True)
    m = ValidationMetricsBuilder.build(evs)
    assert m.walu == 1


def test_walu_reminded():
    evs = _flow(save=False, reminder=True, claim=False)
    m = ValidationMetricsBuilder.build(evs)
    assert m.walu == 1


def test_walu_not_counted_without_behavior():
    evs = [_ev("app_install", "u1"), _ev("app_open", "u1")]
    m = ValidationMetricsBuilder.build(evs)
    assert m.walu == 0


def test_walu_multiple_users():
    evs = _flow("u1", save=True) + _flow("u2", save=True)
    m = ValidationMetricsBuilder.build(evs)
    assert m.walu == 2


# ---- 参数化通过率 ----
@pytest.mark.parametrize("users,key", [
    (2, "first_save_rate"), (3, "first_save_rate"), (4, "first_save_rate"),
])
def test_save_rate_scales(users, key):
    evs = []
    for i in range(users):
        evs += [_ev("app_install", f"u{i}")]
    evs.append(_ev("ticket_saved", "u0"))
    m = ValidationMetricsBuilder.build(evs)
    v = next(x for x in m.metrics if x.key == key)
    assert v.value == pytest.approx(1.0 / users)


# ---- 序列化 ----
def test_metrics_to_dict():
    m = ValidationMetricsBuilder.build(_flow())
    d = m.to_dict()
    assert "metrics" in d and "walu" in d and "installs" in d


def test_metrics_to_text():
    m = ValidationMetricsBuilder.build(_flow())
    assert "用户验证指标" in m.to_text()


def test_build_helper():
    m = build_metrics(_flow())
    assert isinstance(m, ValidationMetrics)


def test_metric_dataclass():
    vm = ValidationMetric(key="k", label="标签", value=0.6, target=0.5, passed=True)
    d = vm.to_dict()
    assert d["key"] == "k" and d["passed"] is True


# ---- 空数据 ----
def test_empty_events_metrics():
    m = ValidationMetricsBuilder.build([])
    assert m.installs == 0
    assert m.walu == 0
    assert all(v.value == 0.0 for v in m.metrics)
