"""v3.9.0 Phase 7：AI 助手量化融合测试。"""
from __future__ import annotations

import os

import pytest

from engine.assistant import AssistantIntentRouter, execute_intent, handle_query
from engine.lottery_quant.quant_director import QuantDirector

TICKETS = [
    {"front": [10, 11, 18, 22, 35], "back": [6, 12]},
    {"front": [1, 2, 3, 4, 5], "back": [6, 7]},
    {"front": [5, 10, 15, 20, 25], "back": [8, 9]},
]
NOTES_TEXT = " ".join("".join(f"{n:02d}" for n in t["front"] + t["back"]) for t in TICKETS)


# ---------- 路由 ----------
@pytest.mark.parametrize("query,tool", [
    ("分析一下我的号码", "quant_analyze"),
    ("我的15注风险怎么样", "quant_analyze"),
    ("模拟一下中奖情况", "quant_analyze"),
    ("分析我这6注大乐透号码", "quant_analyze"),
    ("组合评分", "quant_analyze"),
    ("号码重复率", "quant_analyze"),
    ("资金风险分析", "quant_analyze"),
    ("概率分析", "quant_analyze"),
    ("中奖了吗", "prize"),
    ("7月31日买的大乐透能得多少奖金", "prize"),
    ("推荐一注号码", "recommend"),
    ("热号有哪些", "hot_cold"),
    ("冷号有哪些", "hot_cold"),
])
def test_route_tool(query, tool):
    r = AssistantIntentRouter().route(query)
    assert r.tool == tool, f"{query} → {r.tool}, 期望 {tool}"


def test_quant_priority_over_prize():
    """量化强意图优先于兑奖小词。"""
    r = AssistantIntentRouter().route("模拟一下中奖情况")
    assert r.tool == "quant_analyze"


def test_prize_priority_when_explicit():
    r = AssistantIntentRouter().route("我这15注中了多少钱")
    assert r.tool == "prize"


def test_pending_confirm_still_first(task_storage):
    """PendingTask 确认仍是最优先级。"""
    handle_query(f"7月31日买大乐透：{NOTES_TEXT}")
    r = AssistantIntentRouter().route("是的")
    assert r.is_confirm
    from engine.task_context import PendingTaskManager
    PendingTaskManager().clear_task("default")


# ---------- quant_analyze 执行 ----------
def test_execute_quant_full():
    res = execute_intent("quant_analyze", f"分析我的号码：{NOTES_TEXT}")
    assert res.success
    assert "量化分析报告" in res.text
    assert res.data["tickets"] == 3


def test_execute_quant_structure():
    res = execute_intent("quant_analyze", f"组合评分：{NOTES_TEXT}")
    assert res.success
    assert "组合评分" in res.text


def test_execute_quant_risk():
    res = execute_intent("quant_analyze", f"我的风险：{NOTES_TEXT}")
    assert res.success
    assert "风险" in res.text
    assert "风险等级" in res.text


def test_execute_quant_simulation():
    res = execute_intent("quant_analyze", f"模拟：{NOTES_TEXT}")
    assert res.success
    assert "蒙特卡洛" in res.text or "模拟" in res.text


def test_execute_quant_portfolio():
    res = execute_intent("quant_analyze", f"重复率：{NOTES_TEXT}")
    assert res.success
    assert "重复率" in res.text


def test_execute_quant_probability():
    res = execute_intent("quant_analyze", "概率分析大乐透")
    assert res.success
    assert "概率" in res.text
    assert "21,425,712" in res.text


# ---------- 无号码引导 ----------
def test_quant_no_numbers(tmp_path, monkeypatch):
    # 隔离票据存储，模拟"用户无号码"场景
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    res = execute_intent("quant_analyze", "分析一下我的号码")
    assert not res.success
    assert "号码" in res.text or "票据" in res.text


def test_quant_no_numbers_missing_field(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_STORAGE_DIR", str(tmp_path))
    res = execute_intent("quant_analyze", "分析一下我的号码")
    assert "numbers" in res.missing


# ---------- handle_query 端到端 ----------
def test_handle_query_quant():
    reply = handle_query(f"分析我这3注大乐透号码：{NOTES_TEXT}")
    assert "量化分析报告" in reply
    assert "随机性" in reply


def test_handle_query_quant_risk():
    reply = handle_query(f"我的15注风险：{NOTES_TEXT}")
    assert "风险" in reply


def test_handle_query_quant_prize_not_confused():
    reply = handle_query("7月31日买大乐透能得多少奖金：10111822350612")
    assert "是否按" in reply  # 走兑奖确认，不是量化


# ---------- QuantDirector ----------
def test_director_full_report():
    r = QuantDirector.full_report(TICKETS, sim_trials=500)
    assert r["is_quant"]
    assert r["score"] > 0
    assert r["coverage_rate"] > 0


def test_director_full_report_no_tickets():
    r = QuantDirector.full_report([])
    assert "号码" in r["report_text"]


def test_director_structure():
    r = QuantDirector.structure_report(TICKETS)
    assert "组合评分" in r["report_text"]


def test_director_risk():
    r = QuantDirector.risk_report(TICKETS)
    assert "年度投入" in r["report_text"]


def test_director_simulation():
    r = QuantDirector.simulation_report(TICKETS, trials=1000)
    assert "覆盖率" in r["report_text"]


def test_director_portfolio():
    r = QuantDirector.portfolio_report(TICKETS)
    assert "重复率" in r["report_text"]


def test_director_probability():
    r = QuantDirector.probability_report("dlt")
    assert "一等奖" in r["report_text"]


def test_director_ssq():
    r = QuantDirector.full_report([{"front": [1, 2, 3, 4, 5, 6], "back": [1]}], "ssq", sim_trials=500)
    assert "双色球" in r["report_text"]


# ---------- 免责声明与随机性 ----------
@pytest.mark.parametrize("kw", ["随机性", "概率相同", "不代表未来"])
def test_full_report_disclaimer(kw):
    r = QuantDirector.full_report(TICKETS, sim_trials=500)
    assert kw in r["report_text"]


def test_no_prediction_claims():
    r = QuantDirector.full_report(TICKETS, sim_trials=500)
    for banned in ("预测中奖", "提高中奖概率", "稳赚"):
        assert banned not in r["report_text"]


@pytest.mark.parametrize("method", ["structure_report", "risk_report",
                                    "simulation_report", "portfolio_report"])
def test_each_report_has_disclaimer(method):
    if method == "simulation_report":
        r = getattr(QuantDirector, method)(TICKETS, trials=500)
    else:
        r = getattr(QuantDirector, method)(TICKETS)
    assert any(kw in r["report_text"] for kw in ("随机性", "不代表", "负期望", "理性购彩"))


# ---------- 报告结构 ----------
@pytest.mark.parametrize("f", ["is_quant", "lottery", "tickets", "report_text"])
def test_full_report_fields(f):
    r = QuantDirector.full_report(TICKETS, sim_trials=500)
    assert f in r


def test_full_report_sections():
    r = QuantDirector.full_report(TICKETS, sim_trials=500)
    for sec in ("组合评分", "概率模型", "蒙特卡洛", "组合分析", "资金风险", "汇总"):
        assert sec in r["report_text"]


# ---------- 从票据读取 ----------
def test_quant_from_tickets(task_storage):
    from engine.ticket_system import TicketManager
    from engine.task_context import PendingTaskManager
    PendingTaskManager().clear_task("default")
    mgr = TicketManager()
    mgr.clear()
    mgr.add("dlt", [1, 2, 3, 4, 5], [6, 7])
    mgr.add("dlt", [8, 9, 10, 11, 12], [8, 9])
    res = execute_intent("quant_analyze", "分析一下我的号码")
    assert res.success
    assert res.data["source"] == "tickets"
    mgr.clear()


# ---------- 大规模参数化 ----------
@pytest.mark.parametrize("seed", range(40))
def test_full_report_param_matrix(seed):
    import random
    rng = random.Random(seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(rng.randint(1, 8))]
    r = QuantDirector.full_report(tickets, sim_trials=800)
    assert r["tickets"] == len(tickets)
    assert 0 <= r["score"] <= 100
    assert 0 <= r["coverage_rate"] <= 1
    assert r["risk_level"] in ("A", "B", "C", "D")


@pytest.mark.parametrize("i", range(30))
def test_quant_tool_param_matrix(i):
    import random
    rng = random.Random(2000 + i)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(3)]
    text = " ".join("".join(f"{n:02d}" for n in t["front"] + t["back"]) for t in tickets)
    res = execute_intent("quant_analyze", f"分析我的号码：{text}")
    assert res.success
    assert res.data["tickets"] == 3


@pytest.mark.parametrize("seed", range(20))
def test_director_ssq_matrix(seed):
    import random
    rng = random.Random(3000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 34), 6)),
                "back": [rng.randint(1, 16)]} for _ in range(5)]
    r = QuantDirector.full_report(tickets, "ssq", sim_trials=800)
    assert "双色球" in r["report_text"]
    assert r["tickets"] == 5


# ---------- 补充矩阵 ----------
@pytest.mark.parametrize("seed", range(30))
def test_director_structure_matrix(seed):
    import random
    rng = random.Random(4000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(4)]
    r = QuantDirector.structure_report(tickets)
    assert "组合评分" in r["report_text"]
    assert "随机性" in r["report_text"]


@pytest.mark.parametrize("query_prefix", [
    "分析", "量化分析", "组合评分", "我的号码结构", "分析一下",
    "帮我分析", "号码结构怎么样", "分析这组号码", "看看我的号码",
])
def test_handle_query_quant_variants(query_prefix):
    reply = handle_query(f"{query_prefix}：{NOTES_TEXT}")
    assert "随机性" in reply or "评分" in reply or "概率" in reply


@pytest.mark.parametrize("seed", range(25))
def test_risk_report_matrix(seed):
    import random
    rng = random.Random(5000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(3)]
    r = QuantDirector.risk_report(tickets)
    assert "年度投入" in r["report_text"]
    assert "风险等级" in r["report_text"]


@pytest.mark.parametrize("seed", range(25))
def test_simulation_report_matrix(seed):
    import random
    rng = random.Random(6000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(3)]
    r = QuantDirector.simulation_report(tickets, trials=500)
    assert "覆盖率" in r["report_text"]
    assert "不代表未来" in r["report_text"]


@pytest.mark.parametrize("seed", range(25))
def test_portfolio_report_matrix(seed):
    import random
    rng = random.Random(7000 + seed)
    tickets = [{"front": sorted(rng.sample(range(1, 36), 5)),
                "back": sorted(rng.sample(range(1, 13), 2))} for _ in range(5)]
    r = QuantDirector.portfolio_report(tickets)
    assert "重复率" in r["report_text"]
    assert "不能保证中奖" in r["report_text"]
