"""v3.8.2-P1 Phase 6：错误输入与边界处理。"""
from __future__ import annotations

import pytest

from engine.assistant import handle_query, AssistantIntentRouter
from engine.lottery_intent import compute_prize_report
from engine.lottery_intent.ticket_parser import TicketParser


# ---------- 空/无效输入 ----------
@pytest.mark.parametrize("text", [
    "", "  ", "\n", "abc", "你好", "今天天气如何", "？？？", "！！！",
    "我", "的", "彩票", "无", "嗯？", "啊", "test",
    "hello world", "12345", "中文乱码！@#￥%", "  空格   ",
])
def test_invalid_inputs_no_crash(text):
    r = handle_query(text)
    assert isinstance(r, str)
    r2 = compute_prize_report(text)
    assert isinstance(r2, dict)


@pytest.mark.parametrize("text", [
    "没有号码", "帮我算算", "中了多少钱", "兑奖", "这期中了吗",
])
def test_prize_intent_without_numbers(text):
    r = compute_prize_report(text)
    # 未解析到号码 → 给出引导，不崩溃
    assert "report_text" in r
    assert "未" in r["report_text"] or "请" in r["report_text"] or "号码" in r["report_text"]


# ---------- 号码边界 ----------
@pytest.mark.parametrize("bad", [
    "99 99 99 99 99 + 99 99",
    "36 37 38 39 40 + 13 14",
    "100 200 300",
    "00000000000000",
])
def test_out_of_range_numbers(bad):
    r = TicketParser.parse(bad)
    assert r.parsed_notes >= 0  # 不崩溃
    for t in r.tickets:
        assert isinstance(t.front, list)
        assert isinstance(t.back, list)


@pytest.mark.parametrize("text", [
    "我就买了一注 05 08",          # 号码不足
    "前区 01 02 03",               # 只有前区
    "后区 06 07",                  # 只有后区
])
def test_partial_numbers(text):
    r = TicketParser.parse(text)
    assert isinstance(r.parsed_notes, int)


# ---------- 日期边界 ----------
@pytest.mark.parametrize("text", [
    "31日买的",                     # 无月份
    "2026-13-45 买的",              # 非法日期
    "99月99日买",                   # 非法月日
])
def test_invalid_dates(text):
    r = compute_prize_report(f"{text}，号码 10111822350612")
    assert isinstance(r, dict)
    assert "report_text" in r


# ---------- 长文本 ----------
@pytest.mark.parametrize("n", [30, 60, 100])
def test_large_note_counts(n):
    front = [1, 2, 3, 4, 5]
    notes = [(front, [6, 7]) for _ in range(n)]
    s = " ".join("".join(f"{x:02d}" for x in f + b) for f, b in notes)
    r = TicketParser.parse(s)
    assert r.parsed_notes == n


def test_very_long_text_no_crash():
    s = "7月31日买" + "了" * 500 + "，号码 10111822350612"
    r = compute_prize_report(s)
    assert "report_text" in r


# ---------- 路由边界 ----------
@pytest.mark.parametrize("text,intent", [
    ("是的", "confirm"),          # 无任务 → 引导确认提示
    ("今天热吗", "chat"),
    ("帮我看看冷号", "hot_cold"),
    ("推荐一注号码", "recommend"),
    ("生成研究报告", "report"),
    ("生成分析报告", "report"),
])
def test_router_edges(text, intent):
    router = AssistantIntentRouter()
    r = router.route(text)
    assert r.intent == intent


# ---------- execute_intent user_id ----------
def test_execute_intent_user_id(task_storage):
    from engine.assistant import execute_intent
    from engine.task_context import PendingTaskManager
    res = execute_intent("prize", "7月31日买大乐透 10111822350612", user_id="uid-test")
    assert res.tool == "prize"
    # 确认文案 → 已创建任务（uid-test）
    if "是否按" in res.text:
        assert PendingTaskManager().has_pending("uid-test")
    PendingTaskManager().clear_task("uid-test")


# ---------- confirm 无任务 ----------
@pytest.mark.parametrize("text", ["是", "是的", "好的", "确认", "按这个算"])
def test_confirm_without_task_reply(task_storage, text):
    reply = handle_query(text)
    assert "待确认" in reply or "兑奖" in reply
