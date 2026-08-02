"""assistant - 工具注册表（Tool Registry）。

注册所有业务工具（复用已有能力），供 Intent Router 调用。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class ToolResult:
    """工具执行结果。"""

    tool: str
    success: bool = True
    text: str = ""
    data: dict = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)  # 缺失信息

    @property
    def needs_more_info(self) -> bool:
        return bool(self.missing)


@dataclass
class Tool:
    """工具定义。"""

    name: str
    description: str
    handler: Callable[[str, str], ToolResult]   # (query, user_id)
    keywords: List[str] = field(default_factory=list)  # 触发关键词


class ToolRegistry:
    """工具注册表。"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def all(self) -> List[Tool]:
        return list(self._tools.values())

    def names(self) -> List[str]:
        return list(self._tools.keys())

    def execute(self, name: str, query: str, user_id: str = "default") -> ToolResult:
        t = self._tools.get(name)
        if not t:
            return ToolResult(tool=name, success=False, text=f"未知工具：{name}")
        try:
            return t.handler(query, user_id)
        except TypeError:
            # 兼容单参数 handler（旧签名 Callable[[str], ToolResult]）
            try:
                return t.handler(query)
            except Exception as e:
                return ToolResult(tool=name, success=False, text=f"工具执行失败：{e}")
        except Exception as e:
            return ToolResult(tool=name, success=False, text=f"工具执行失败：{e}")


# ---------------- 工具处理器 ----------------
def _prize_handler(query: str, user_id: str = "default") -> ToolResult:
    """兑奖计算工具（v3.8.2-P1：支持 PendingTask 确认上下文）。"""
    from engine.lottery_intent import compute_prize_report
    r = compute_prize_report(query, user_id=user_id)
    if not r.get("is_prize"):
        return ToolResult(tool="prize", text=r.get("report_text", "未识别到兑奖意图。"))
    if r.get("tickets", 0) == 0:
        return ToolResult(
            tool="prize", success=False,
            text="未解析到有效号码。请提供号码，例如：01 02 03 04 05 + 06 07，或连续号码串 13212326330112。",
            missing=["numbers"],
        )
    return ToolResult(tool="prize", text=r["report_text"], data={
        "lottery": r.get("lottery"), "tickets": r.get("tickets"),
        "won": r.get("won_notes"), "total": r.get("total"),
        "need_confirm": r.get("need_confirm", False),
        "purchase_date": r.get("purchase_date"),
        "draw_date": r.get("draw_date"),
    })


def _hot_numbers_handler(query: str, user_id: str = "default") -> ToolResult:
    from data_loader import load_draws
    from stats import hot_numbers, cold_numbers
    draws = load_draws()
    if not draws:
        return ToolResult(tool="hot_cold", success=False, text="暂无数据。", missing=["data"])
    if "冷" in query:
        cold = cold_numbers(draws, 8)
        return ToolResult(tool="hot_cold", text="近期冷号（前区）：" + " ".join(f"{n:02d}({c}次)" for n, c in cold))
    hot = hot_numbers(draws, 8)
    return ToolResult(tool="hot_cold", text="近期热号（前区）：" + " ".join(f"{n:02d}({c}次)" for n, c in hot))


def _recommend_handler(query: str, user_id: str = "default") -> ToolResult:
    from data_loader import load_draws
    from stats import recommendation
    draws = load_draws()
    if not draws:
        return ToolResult(tool="recommend", success=False, text="暂无数据。", missing=["data"])
    method = "cold" if "冷" in query else "balanced" if "均衡" in query else "hot"
    rec = recommendation(draws, method)
    label = {"hot": "热号", "cold": "冷号", "balanced": "奇偶均衡"}[method]
    return ToolResult(tool="recommend", text=f"{label}推荐：{' '.join(f'{n:02d}' for n in rec['front'])} + {' '.join(f'{n:02d}' for n in rec['back'])}")


def _backtest_handler(query: str, user_id: str = "default") -> ToolResult:
    return ToolResult(tool="backtest", text="回测工具：请在「回测中心」页面选择策略运行，这里仅提示。")


def _report_handler(query: str, user_id: str = "default") -> ToolResult:
    return ToolResult(tool="report", text="报告工具：请到「研究报告」页面一键生成并导出。")


def _quant_analyze_handler(query: str, user_id: str = "default") -> ToolResult:
    """彩票量化分析工具（v3.9.0 Phase 7）。

    支持：结构分析 / 概率模型 / 蒙特卡洛模拟 / 资金风险 / 组合分析。
    从输入解析号码，或读取票据系统已保存票据。
    """
    from engine.lottery_quant.quant_director import QuantDirector
    from engine.lottery_intent.ticket_parser import TicketParser
    from engine.lottery_intent.intent_router import LotteryIntentRouter

    parse = TicketParser.parse(query)
    tickets = parse.to_ticket_dicts()
    lottery = parse.lottery or LotteryIntentRouter.detect(query).lottery or "dlt"

    # 无号码 → 读取票据系统
    source = "input"
    if not tickets:
        try:
            from engine.ticket_system import TicketManager
            mgr = TicketManager()
            saved = mgr.list_all()
            if saved:
                tickets = [{"front": t.front, "back": t.back} for t in saved[:30]]
                lottery = saved[0].lottery
                source = "tickets"
        except Exception:
            pass

    # 概率分析不需要号码（理论概率固定）
    if not tickets and any(k in query for k in ("概率",)):
        r = QuantDirector.probability_report(lottery)
        return ToolResult(tool="quant_analyze", text=r["report_text"],
                          data={"lottery": lottery, "source": "probability"})

    if not tickets:
        return ToolResult(tool="quant_analyze", success=False,
                          text="未找到可分析的号码。请提供号码，或在「工作台」保存票据后分析。",
                          missing=["numbers"])

    # 子意图路由：明确子意图走专项，否则完整量化报告（v3.9.0 验收）
    ql = query
    if any(k in ql for k in ("风险", "投入", "亏损")):
        r = QuantDirector.risk_report(tickets, lottery)
    elif any(k in ql for k in ("模拟", "覆盖", "中奖情况")):
        r = QuantDirector.simulation_report(tickets, lottery)
    elif any(k in ql for k in ("重复", "集中", "相关性")):
        r = QuantDirector.portfolio_report(tickets, lottery)
    elif any(k in ql for k in ("概率",)):
        r = QuantDirector.probability_report(lottery)
    else:
        r = QuantDirector.full_report(tickets, lottery)

    return ToolResult(tool="quant_analyze", text=r["report_text"], data={
        "lottery": r.get("lottery"), "tickets": r.get("tickets", len(tickets)),
        "score": r.get("score"), "coverage_rate": r.get("coverage_rate"),
        "risk_level": r.get("risk_level"), "source": source,
    })


# 能力地图：工具 → 触发关键词
TOOL_KEYWORDS = {
    "prize": ["中了", "中奖", "兑奖", "奖金", "多少钱", "中了吗", "算算", "赚了", "中没中", "有没有中", "中了没"],
    "quant_analyze": ["分析", "评分", "量化", "组合评分", "概率分析", "资金风险", "重复率",
                      "结构分析", "组合分析", "模拟", "风险", "覆盖", "我的号码", "号码结构",
                      "分析号码", "分析我的"],
    "hot_cold": ["热号", "冷号", "热码", "冷码"],
    "recommend": ["推荐", "号码", "一注", "选号", "选几个", "选一些"],
    "backtest": ["回测", "验证策略", "策略表现"],
    "report": ["报告", "生成报告", "分析报告"],
}

# 量化强意图词（路由加权，优先于兑奖小词）
QUANT_STRONG_WORDS = ["风险", "模拟", "结构", "重复率", "覆盖", "组合评分", "资金风险", "概率分析", "分析"]


def register_tools() -> ToolRegistry:
    """注册全部业务工具。"""
    reg = ToolRegistry()
    reg.register(Tool(name="prize", description="兑奖计算", handler=_prize_handler, keywords=TOOL_KEYWORDS["prize"]))
    reg.register(Tool(name="quant_analyze", description="彩票量化分析", handler=_quant_analyze_handler, keywords=TOOL_KEYWORDS["quant_analyze"]))
    reg.register(Tool(name="hot_cold", description="热号/冷号查询", handler=_hot_numbers_handler, keywords=TOOL_KEYWORDS["hot_cold"]))
    reg.register(Tool(name="recommend", description="号码推荐", handler=_recommend_handler, keywords=TOOL_KEYWORDS["recommend"]))
    reg.register(Tool(name="backtest", description="回测指引", handler=_backtest_handler, keywords=TOOL_KEYWORDS["backtest"]))
    reg.register(Tool(name="report", description="报告指引", handler=_report_handler, keywords=TOOL_KEYWORDS["report"]))
    return reg


def execute_intent(intent: str, query: str, registry: Optional[ToolRegistry] = None,
                   user_id: str = "default") -> ToolResult:
    """按意图执行工具（v3.8.2-P1：支持 user_id 上下文）。"""
    reg = registry or register_tools()
    if intent in reg.names():
        return reg.execute(intent, query, user_id=user_id)
    return ToolResult(tool=intent, success=False, text=f"未知意图：{intent}")
