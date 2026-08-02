"""v3.8.2-P1 Phase 4/5：确认恢复闭环 + 报告增强（端到端）。"""
from __future__ import annotations

import pytest

from engine.assistant import handle_query
from engine.task_context import PendingTaskManager
from engine.lottery_intent import compute_prize_report, confirm_prize_task


def _notes_text(notes):
    return " ".join("".join(f"{n:02d}" for n in row) for t in notes for row in t)


# 15 注：第1注=开奖号码（一等奖），第6/11注=5+0（三等奖）
FRONTS = [[10, 11, 18, 22, 35], [1, 2, 3, 4, 5], [5, 10, 15, 20, 25],
          [3, 4, 14, 28, 31], [13, 25, 30, 32, 33]]
T15 = ([(f, [6, 12]) for f in FRONTS]
       + [(f, [2, 7]) for f in FRONTS]
       + [(f, [3, 9]) for f in FRONTS])
T15_TEXT = _notes_text(T15)


def _first_round(task_storage):
    """执行第一轮：用户输入 15 注，返回确认文案。"""
    user_input = f"7月31日购买了这15组，我能获得多少奖金：{T15_TEXT}"
    reply = handle_query(user_input)
    return reply


@pytest.fixture()
def flow_storage(task_storage):
    return task_storage


# ---------- 1. 购买日期+开奖日期 ----------
def test_purchase_and_draw_dates(flow_storage):
    r = compute_prize_report("7月31日买的，8月1日开奖：10111822350612")
    assert r["purchase_date"] == "2026-07-31"
    assert r["draw_date"] == "2026-08-01"
    assert r["draw"]["issue"] == "26086"


def test_explicit_draw_date_no_confirm(flow_storage):
    r = compute_prize_report("7月31日买的，8月1日开奖，号码 10111822350612")
    assert not r.get("need_confirm")
    assert r["is_prize"]


# ---------- 2. 购买日期等待确认 ----------
def test_purchase_only_triggers_confirm(flow_storage):
    r = compute_prize_report("7月31日买的大乐透：10111822350612")
    assert r.get("need_confirm") is True
    assert "是否按" in r["report_text"]


def test_confirm_text_contains_guidance(flow_storage):
    reply = _first_round(flow_storage)
    assert "是否按 2026-08-01 开奖计算" in reply
    assert "回复「是 / 好的 / 确认」" in reply


def test_pending_task_created_after_confirm_prompt(flow_storage):
    _first_round(flow_storage)
    mgr = PendingTaskManager()
    assert mgr.has_pending("default")
    t = mgr.get_pending_task("default")
    assert t.note_count == 15
    assert t.purchase_date == "2026-07-31"
    assert t.draw_date == "2026-08-01"


# ---------- 3. 用户确认 ----------
@pytest.mark.parametrize("confirm_text", ["是", "是的", "好的", "确认", "按这个算"])
def test_confirm_replies_resume(flow_storage, confirm_text):
    _first_round(flow_storage)
    reply = handle_query(confirm_text)
    assert "总奖金" in reply
    assert "26086" in reply
    assert "中奖注数" in reply


def test_confirm_returns_prize_report(flow_storage):
    _first_round(flow_storage)
    r = confirm_prize_task("default")
    assert r["confirmed"] is True
    assert r["resumed_from_task"] is True
    assert r["tickets"] == 15
    assert r["won_notes"] == 7
    assert r["total"] == 5_020_020


def test_confirm_consumes_task_once(flow_storage):
    _first_round(flow_storage)
    assert handle_query("是的")
    assert not PendingTaskManager().has_pending("default")


def test_confirm_without_task(flow_storage):
    reply = handle_query("是的")
    assert "待确认" in reply


# ---------- 4. 15注解析 + 5. 奖金计算 ----------
def test_full_flow_15_notes(flow_storage):
    reply = _first_round(flow_storage)
    assert "15" in reply or "15组" in reply
    reply2 = handle_query("是的")
    assert "投注注数：15 注" in reply2
    assert "中奖注数：7 / 15" in reply2
    assert "一等奖 ¥5,000,000" in reply2


def test_all_lose_flow(flow_storage):
    notes = [([1, 2, 3, 4, 5], [1, 2]), ([6, 7, 8, 9, 10], [3, 4])]
    s = _notes_text(notes)
    handle_query(f"7月31日购买了这{len(notes)}组，能中多少：{s}")
    reply = handle_query("确认")
    assert "中奖注数：0 / 2" in reply
    assert "未中奖" in reply
    assert "总奖金：¥0" in reply


# ---------- 6. 连续对话 ----------
def test_conversation_two_rounds(flow_storage):
    r1 = handle_query(f"7月31日买了15组，能得多少奖金：{T15_TEXT}")
    assert "是否按" in r1
    r2 = handle_query("是的")
    assert "总奖金" in r2
    # 第二轮新提问不受残留任务影响
    r3 = handle_query("推荐一注")
    assert "推荐" in r3 or "号码" in r3 or "大乐透" in r3


def test_multi_turn_no_interference(flow_storage):
    handle_query("哪些是热号")
    assert not PendingTaskManager().has_pending("default")


# ---------- 7. 重新打开软件恢复 ----------
def test_restart_restores_pending(task_storage):
    # 第一轮在"重启前"执行
    handle_query(f"7月31日买了15组：{T15_TEXT}")
    assert PendingTaskManager().has_pending("default")
    # 模拟重启：新管理器实例（同存储目录）
    mgr = PendingTaskManager()
    t = mgr.get_pending_task("default")
    assert t is not None and t.note_count == 15
    # 恢复后确认
    reply = handle_query("好的")
    assert "总奖金" in reply


def test_restart_issue_kept(task_storage):
    handle_query(f"7月31日买了15组：{T15_TEXT}")
    t = PendingTaskManager().get_pending_task("default")
    assert t.draw_date == "2026-08-01"


# ---------- 8. 错误输入 ----------
def test_bad_input_no_crash(flow_storage):
    for bad in ["", "  ", "abcd", "今天天气不错", "！！？？"]:
        reply = handle_query(bad)
        assert isinstance(reply, str)


def test_empty_input_no_task(flow_storage):
    handle_query("")
    assert not PendingTaskManager().has_pending("default")


def test_numbers_without_date_no_task(flow_storage):
    """有号码无日期 → 直接算最新一期，不创建确认任务。"""
    r = compute_prize_report("号码 10111822350612")
    assert not r.get("need_confirm")
    assert not PendingTaskManager().has_pending("default")


# ---------- Phase 5 报告字段 ----------
REPORT_FIELDS = ["购买日期", "开奖日期", "开奖期号", "投注注数", "中奖注数", "总奖金"]


@pytest.mark.parametrize("field", REPORT_FIELDS)
def test_report_has_all_fields(flow_storage, field):
    _first_round(flow_storage)
    reply = handle_query("是的")
    assert field in reply


def test_report_no_unknown_dates(flow_storage):
    _first_round(flow_storage)
    reply = handle_query("是的")
    assert "未知日期" not in reply
    assert "未知注数" not in reply


def test_report_each_note_detail(flow_storage):
    _first_round(flow_storage)
    reply = handle_query("是的")
    assert "第1注：10 11 18 22 35 + 06 12" in reply
    assert "一等奖" in reply


# ---------- 禁止回复 ----------
BANNED = ["请提供开奖结果", "请输入更多信息", "我无法计算"]


@pytest.mark.parametrize("banned", BANNED)
def test_no_banned_reply(flow_storage, banned):
    _first_round(flow_storage)
    reply = handle_query("是的")
    assert banned not in reply
