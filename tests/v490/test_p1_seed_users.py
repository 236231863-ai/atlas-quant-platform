"""v4.9.1 P1 种子用户实验基础设施 测试。

覆盖（任务书 P1 ①-④）：
  ① 用户编号体系 UserRegistry（U0001-U0050、字段、CSV 导出）
  ② 4 问反馈问卷 UserFeedbackSurvey（Q1/Q2 不可替代性/Q3 流失/Q4 付费）
  ③ 每日实验记录 DailyExperimentLog（累加、汇总、CSV 导出）
  ④ 提醒价值统计 ReminderValueTracker（点击率≥30% 目标）
  ⑤ 事件集扩展（reminder_sent/reminder_enabled/asset_viewed 等）
  ⑥ 旧接口向后兼容（P3 的 2 问 submit）
"""
import os

import pytest

from engine.user_experiment import (
    EXPERIMENT_EVENTS,
    INDISPENSABLE_REASONS,
    MILESTONES,
    PAY_LEVELS,
    DAILY_LOG_FIELDS,
    ExperimentTracker,
    UserFeedbackSurvey,
    UserRegistry,
    DailyExperimentLog,
    ReminderValueTracker,
)


# ---------------- ① 用户编号体系 ----------------

def test_registry_allocate_sequential(exp_storage):
    reg = UserRegistry()
    assert reg.register().user_id == "U0001"
    assert reg.register().user_id == "U0002"
    assert reg.register().user_id == "U0003"


def test_registry_allocate_after_existing(exp_storage):
    reg = UserRegistry()
    reg.register()
    reg.register()
    reg.register()
    # 重新加载后继续递增
    assert UserRegistry().allocate_next_id() == "U0004"


def test_registry_register_fields(exp_storage):
    reg = UserRegistry()
    u = reg.register("大乐透", "每周")
    assert u.lottery_type == "大乐透"
    assert u.purchase_frequency == "每周"
    assert u.first_open_at  # 默认填充


def test_registry_rejects_invalid_fields(exp_storage):
    reg = UserRegistry()
    u = reg.register("不存在彩种", "每月十次")
    assert u.lottery_type == "其他"
    assert u.purchase_frequency == "首次"


def test_registry_mark_flags(exp_storage):
    reg = UserRegistry()
    u = reg.register()
    assert reg.mark(u.user_id, "reminder_enabled")
    assert reg.get(u.user_id).reminder_enabled is True
    assert not reg.mark(u.user_id, "非法字段")
    assert not reg.mark("U9999", "draw_checked")


def test_registry_set_first_ticket(exp_storage):
    reg = UserRegistry()
    u = reg.register()
    assert reg.set_first_ticket_at(u.user_id, "2026-08-09T10:00:00")
    assert reg.get(u.user_id).first_ticket_saved_at == "2026-08-09T10:00:00"


def test_registry_count_and_get(exp_storage):
    reg = UserRegistry()
    reg.register()
    reg.register()
    assert reg.count() == 2
    assert reg.get("U0001") is not None
    assert reg.get("U9999") is None


def test_registry_export_csv(exp_storage):
    reg = UserRegistry()
    reg.register("双色球", "每周")
    reg.mark("U0001", "asset_viewed")
    path = reg.export_csv()
    assert os.path.exists(path)
    with open(path, encoding="utf-8-sig") as f:
        content = f.read()
    assert "U0001" in content
    assert "asset_viewed" in content


def test_registry_50_users(exp_storage):
    reg = UserRegistry()
    for _ in range(50):
        reg.register("大乐透", "每周")
    assert reg.count() == 50
    assert reg.get("U0050") is not None


# ---------------- ② 4 问反馈问卷 ----------------

def test_feedback_full_4_questions(exp_storage):
    s = UserFeedbackSurvey()
    fb = s.submit_full(
        "U0001", "防止忘记兑奖",
        indispensable_reason=INDISPENSABLE_REASONS[0],
        uninstall_reason="微信已经够用",
        pay_level="9元/月",
    )
    assert fb is not None
    assert fb.use_reason == "防止忘记兑奖"
    assert fb.indispensable_reason == INDISPENSABLE_REASONS[0]
    assert fb.pay_level == "9元/月"


def test_feedback_rejects_invalid_q1(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit_full("U0001", "非法原因") is None


def test_feedback_rejects_invalid_q2(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit_full("U0001", "防止忘记兑奖",
                         indispensable_reason="非法理由") is None


def test_feedback_rejects_invalid_q3(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit_full("U0001", "防止忘记兑奖",
                         uninstall_reason="非法流失") is None


def test_feedback_rejects_invalid_q4(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit_full("U0001", "防止忘记兑奖",
                         pay_level="99元/月") is None


def test_feedback_q2_all_valid(exp_storage):
    s = UserFeedbackSurvey()
    for r in INDISPENSABLE_REASONS:
        assert s.submit_full("U0001", "自动查看中奖", indispensable_reason=r)


def test_feedback_pay_levels_all_valid(exp_storage):
    s = UserFeedbackSurvey()
    for p in PAY_LEVELS:
        assert s.submit_full("U0001", "数据分析", pay_level=p)


def test_feedback_pay_willing_rate(exp_storage):
    s = UserFeedbackSurvey()
    s.submit_full("U0001", "防止忘记兑奖", pay_level="9元/月")
    s.submit_full("U0002", "自动查看中奖", pay_level="6元/月")
    s.submit_full("U0003", "管理彩票投入", pay_level="不愿意")
    assert round(s.pay_willing_rate(), 4) == round(2 / 3, 4)


def test_feedback_summary_fields(exp_storage):
    s = UserFeedbackSurvey()
    s.submit_full("U0001", "防止忘记兑奖",
                  indispensable_reason=INDISPENSABLE_REASONS[0],
                  uninstall_reason="微信已经够用", pay_level="9元/月")
    sm = s.summary()
    assert sm["total"] == 1
    assert "use_reasons" in sm
    assert "indispensable_reasons" in sm
    assert "uninstall_reasons" in sm
    assert "pay_levels" in sm
    assert sm["top_indispensable"] == INDISPENSABLE_REASONS[0]


def test_feedback_old_2q_compat(exp_storage):
    """P3 旧版 2 问接口必须继续可用。"""
    s = UserFeedbackSurvey()
    fb = s.submit("userA", "自动兑奖", "操作复杂")
    assert fb is not None
    assert fb.use_reason == "自动兑奖"
    assert fb.uninstall_reason == "操作复杂"


def test_feedback_old_invalid_still_rejected(exp_storage):
    s = UserFeedbackSurvey()
    assert s.submit("u", "非法原因") is None
    assert s.submit("u", "自动提醒", "非法卸载原因") is None


# ---------------- ③ 每日实验记录 ----------------

def test_daily_log_record(exp_storage):
    dl = DailyExperimentLog()
    e = dl.record(date="2026-08-09", new_users=3, ticket_saved=2)
    assert e.date == "2026-08-09"
    assert e.new_users == 3
    assert e.ticket_saved == 2


def test_daily_log_accumulate(exp_storage):
    dl = DailyExperimentLog()
    dl.record(date="2026-08-09", ticket_saved=2)
    dl.record(date="2026-08-09", ticket_saved=1)
    assert dl.get("2026-08-09").ticket_saved == 3


def test_daily_log_multiple_days(exp_storage):
    dl = DailyExperimentLog()
    dl.record(date="2026-08-09", new_users=3, feedback_count=1)
    dl.record(date="2026-08-10", new_users=5, feedback_count=2)
    assert dl.get("2026-08-10").new_users == 5
    assert dl.get("2026-08-09").feedback_count == 1


def test_daily_log_summary(exp_storage):
    dl = DailyExperimentLog()
    dl.record(date="2026-08-09", new_users=3, ticket_saved=2)
    dl.record(date="2026-08-10", new_users=5, ticket_saved=1)
    s = dl.summary()
    assert s["days"] == 2
    assert s["totals"]["new_users"] == 8
    assert s["totals"]["ticket_saved"] == 3


def test_daily_log_fields_complete(exp_storage):
    dl = DailyExperimentLog()
    e = dl.record(date="2026-08-09")
    d = e.to_dict()
    for k in DAILY_LOG_FIELDS:
        assert k in d


def test_daily_log_export_csv(exp_storage):
    dl = DailyExperimentLog()
    dl.record(date="2026-08-09", new_users=3)
    path = dl.export_csv()
    assert os.path.exists(path)
    with open(path, encoding="utf-8-sig") as f:
        assert "2026-08-09" in f.read()


def test_daily_log_empty_summary(exp_storage):
    dl = DailyExperimentLog()
    s = dl.summary()
    assert s["days"] == 0
    assert s["totals"]["new_users"] == 0


# ---------------- ④ 提醒价值统计 ----------------

def test_reminder_tracker_counts(exp_storage):
    rv = ReminderValueTracker()
    rv.sent("U0001")
    rv.sent("U0001")
    rv.clicked("U0001")
    c = rv.counts()
    assert c["sent"] == 2
    assert c["clicked"] == 1
    assert c["checked_after"] == 0


def test_reminder_click_rate(exp_storage):
    rv = ReminderValueTracker()
    rv.sent("U0001")
    rv.sent("U0002")
    rv.clicked("U0001")
    assert rv.click_rate() == 0.5


def test_reminder_click_rate_goal(exp_storage):
    rv = ReminderValueTracker()
    for _ in range(10):
        rv.sent("U0001")
    for _ in range(4):
        rv.clicked("U0001")
    s = rv.summary()
    assert s["click_rate"] == 0.4
    assert s["click_rate_met"] is True


def test_reminder_click_rate_below_goal(exp_storage):
    rv = ReminderValueTracker()
    for _ in range(10):
        rv.sent("U0001")
    for _ in range(2):
        rv.clicked("U0001")
    assert rv.click_rate() == 0.2
    assert rv.summary()["click_rate_met"] is False


def test_reminder_checked_after_rate(exp_storage):
    rv = ReminderValueTracker()
    rv.sent("U0001")
    rv.checked_after("U0001")
    assert rv.checked_after_rate() == 1.0


def test_reminder_zero_denominator(exp_storage):
    rv = ReminderValueTracker()
    assert rv.click_rate() == 0.0
    assert rv.checked_after_rate() == 0.0


def test_reminder_per_user(exp_storage):
    rv = ReminderValueTracker()
    rv.sent("U0001")
    rv.sent("U0002")
    rv.clicked("U0001")
    pu = rv.per_user()
    assert pu["U0001"]["sent"] == 1
    assert pu["U0001"]["clicked"] == 1
    assert pu["U0002"]["sent"] == 1


def test_reminder_invalid_kind(exp_storage):
    rv = ReminderValueTracker()
    assert rv._append("U0001", "非法类型", {}) is None
    assert rv._append("U0001", "sent", {}) is not None


def test_reminder_export_csv(exp_storage):
    rv = ReminderValueTracker()
    rv.sent("U0001")
    path = rv.export_csv()
    assert os.path.exists(path)


# ---------------- ⑤ 事件集扩展 ----------------

def test_events_extended_v491():
    required = {
        "app_install", "app_open", "ticket_saved", "draw_reminder_clicked",
        "claim_checked", "report_viewed", "premium_view",
        "onboarding_start", "reminder_enabled", "reminder_sent",
        "draw_checked", "draw_checked_after_reminder", "claim_completed",
        "asset_viewed", "weekly_report_viewed",
    }
    assert required.issubset(set(EXPERIMENT_EVENTS))


def test_milestones_extended():
    for ev in ("onboarding_start", "reminder_enabled", "draw_checked",
               "claim_completed", "asset_viewed", "weekly_report_viewed"):
        assert ev in set(MILESTONES.values())


def test_tracker_new_shortcuts(exp_storage):
    t = ExperimentTracker()
    assert t.onboarding_start("U0001") is not None
    assert t.enable_reminder("U0001") is not None
    assert t.reminder_sent("U0001") is not None
    assert t.check_draw("U0001") is not None
    assert t.checked_after_reminder("U0001") is not None
    assert t.claim_completed("U0001") is not None
    assert t.view_asset("U0001") is not None
    assert t.view_weekly_report("U0001") is not None
    for ev in ("onboarding_start", "reminder_enabled", "reminder_sent",
               "draw_checked", "draw_checked_after_reminder",
               "claim_completed", "asset_viewed", "weekly_report_viewed"):
        assert t.count(ev) == 1


def test_tracker_milestones_new(exp_storage):
    t = ExperimentTracker()
    t.open_app("U0001")
    t.onboarding_start("U0001")
    t.save_ticket("U0001")
    t.enable_reminder("U0001")
    t.view_asset("U0001")
    m = t.milestones("U0001")
    assert m["first_open_at"] is not None
    assert m["first_onboarding_at"] is not None
    assert m["first_ticket_saved_at"] is not None
    assert m["first_reminder_enabled_at"] is not None
    assert m["first_asset_viewed_at"] is not None


def test_import_alias_new_events(exp_storage, tmp_path):
    src = tmp_path / "analytics.jsonl"
    src.write_text(
        '{"event_name": "onboarding_complete", "user_id": "u1", "timestamp": "2026-08-09T10:00:00"}\n'
        '{"event_name": "asset_viewed", "user_id": "u1", "timestamp": "2026-08-09T11:00:00"}\n'
        '{"event_name": "weekly_report_opened", "user_id": "u1", "timestamp": "2026-08-10T09:00:00"}\n',
        encoding="utf-8",
    )
    t = ExperimentTracker()
    n = t.import_real_events(str(src))
    assert n == 3
    assert t.count("onboarding_start") == 1
    assert t.count("asset_viewed") == 1
    assert t.count("weekly_report_viewed") == 1
