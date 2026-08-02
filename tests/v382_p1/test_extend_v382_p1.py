"""v3.8.2-P1 扩展矩阵：确认词变体 / 路由优先级 / 报告结构。"""
from __future__ import annotations

import pytest

from engine.assistant import AssistantIntentRouter, handle_query, execute_intent
from engine.lottery_intent import compute_prize_report, confirm_prize_task
from engine.task_context import PendingTaskManager

# 更多确认词变体（扩展）
EXTRA_CONFIRM = [
    ("按8.1算", True), ("按八月一日算", True), ("按2026.08.01算", True),
    ("好的", True), ("嗯", True), ("没问题", True), ("确认了", True),
    ("按这个开奖算", True), ("是的是的", True),
    ("好的谢谢", False), ("不用了", False), ("算了", False),
    ("不清楚", False), ("随便", False), ("另算", False),
    ("换一注", False), ("重新来", False), ("改号码", False),
]


@pytest.mark.parametrize("text,exp", EXTRA_CONFIRM)
def test_extra_confirm_variants(text, exp):
    assert PendingTaskManager.is_confirm_reply(text) == exp


# ---------- 路由优先级：确认 > 业务 > 普通 ----------
def test_confirm_priority_over_business(task_storage):
    """已有任务时，"是"优先走确认而非其他。"""
    handle_query("7月31日买了15组：10111822350612 01020304050607")
    assert PendingTaskManager().has_pending("default")
    router = AssistantIntentRouter()
    r = router.route("是")
    assert r.is_confirm
    assert r.tool == "prize"
    PendingTaskManager().clear_task("default")


def test_business_before_chat():
    router = AssistantIntentRouter()
    assert router.route("热号有哪些").tool == "hot_cold"
    assert router.route("给我推荐号码").tool == "recommend"
    assert router.route("中奖了吗").tool == "prize"
    assert router.route("生成报告").tool == "report"


def test_chat_fallback():
    router = AssistantIntentRouter()
    r = router.route("今天天气如何")
    assert not r.is_business
    assert r.intent == "chat"


# ---------- 否定取消任务 ----------
def test_deny_clears_task(task_storage):
    handle_query("7月31日买了15组：10111822350612 01020304050607")
    assert PendingTaskManager().has_pending("default")
    reply = handle_query("不是")
    assert "取消" in reply
    assert not PendingTaskManager().has_pending("default")


def test_deny_no_task(task_storage):
    reply = handle_query("不是")
    assert "待确认" in reply or "取消" in reply


# ---------- 报告结构断言 ----------
def test_report_structure_complete(task_storage):
    _input = "7月31日买的，8月1日开奖：10111822350612 01020304050607"
    r = compute_prize_report(_input)
    assert r["is_prize"] is True
    assert r["tickets"] == 2
    assert "purchase_date" in r
    assert "draw_date" in r
    assert "draw" in r and "issue" in r["draw"]
    assert "note_details" in r
    assert len(r["note_details"]) == 2
    d0 = r["note_details"][0]
    for k in ("front", "back", "front_hit", "back_hit", "level", "amount",
              "front_text", "back_text", "hit_text"):
        assert k in d0


@pytest.mark.parametrize("idx", [0, 1, 5, 10])
def test_note_detail_fields(task_storage, idx):
    _input = "7月31日买的，8月1日开奖：" + " ".join(
        "".join(f"{n:02d}" for n in row)
        for t in ([(f, [6, 12]) for f in [[10, 11, 18, 22, 35], [1, 2, 3, 4, 5]]] * 8)
        for row in t)
    r = compute_prize_report(_input)
    if idx < len(r["note_details"]):
        d = r["note_details"][idx]
        assert d["front_text"] and d["back_text"]
        assert 0 <= d["front_hit"] <= 5
        assert 0 <= d["back_hit"] <= 2


# ---------- confirm_prize_task 数据 ----------
def test_confirm_prize_data_fields(task_storage):
    handle_query("7月31日买了15组：10111822350612 01020304050607")
    r = confirm_prize_task("default")
    assert r["confirmed"] is True
    assert r["lottery"] == "dlt"
    assert r["tickets"] == 2
    assert r["purchase_date"] == "2026-07-31"
    assert r["draw_date"] == "2026-08-01"
    assert r["draw"]["issue"] == "26086"


def test_confirm_prize_report_text_fields(task_storage):
    handle_query("7月31日买了15组：10111822350612 01020304050607")
    r = confirm_prize_task("default")
    t = r["report_text"]
    for field in ["购买日期", "开奖日期", "开奖期号", "投注注数", "中奖注数", "总奖金"]:
        assert field in t


# ---------- 多用户并行 ----------
@pytest.mark.parametrize("uid", ["user_a", "user_b", "user_c"])
def test_multi_user_parallel_confirmation(task_storage, uid):
    # 通过 compute_prize_report 为不同用户创建任务
    compute_prize_report("7月31日买大乐透 10111822350612", user_id=uid)
    assert PendingTaskManager().has_pending(uid)
    r = confirm_prize_task(uid)
    assert r["confirmed"] is True
    assert not PendingTaskManager().has_pending(uid)


# ---------- handle_query user_id 参数 ----------
def test_handle_query_user_id(task_storage):
    compute_prize_report("7月31日买大乐透 10111822350612", user_id="uid2")
    reply = handle_query("是的", user_id="uid2")
    assert "总奖金" in reply
    assert not PendingTaskManager().has_pending("uid2")


# ---------- execute_intent 兑奖带日期 ----------
def test_execute_intent_prize_with_dates(task_storage):
    res = execute_intent("prize", "7月31日买的，8月1日开奖：10111822350612")
    assert res.success
    assert "总奖金" in res.text
    assert res.data["tickets"] == 1


def test_execute_intent_prize_confirm(task_storage):
    res = execute_intent("prize", "7月31日买大乐透：10111822350612")
    assert res.data.get("need_confirm") is True
    assert PendingTaskManager().has_pending("default")
    PendingTaskManager().clear_task("default")


# ---------- 各类彩种推断 ----------
@pytest.mark.parametrize("text,lottery", [
    ("大乐透 10111822350612", "dlt"),
    ("双色球 01020304050607", "ssq"),
])
def test_lottery_inference_by_keyword(text, lottery):
    from engine.lottery_intent import LotteryIntentRouter
    r = LotteryIntentRouter.detect(text)
    assert r.lottery == lottery


def test_lottery_inference_by_numbers():
    """未明说彩种时按号码特征推断（5+2 → dlt）。"""
    from engine.lottery_intent.ticket_parser import TicketParser
    r = TicketParser.parse("10111822350612")
    assert r.lottery == "dlt"
