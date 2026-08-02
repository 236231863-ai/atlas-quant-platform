"""evaluation_v2 - 免责声明模块。

提供标准化的风险 / 随机性声明文案。
强制禁止任何「诱导中奖概率」或「保证收益」表达。
"""
from __future__ import annotations

DISCLAIMER = (
    "【重要声明】\n"
    "1. 本软件所有统计、分析与回测结果均基于历史开奖数据，仅供研究参考。\n"
    "2. 彩票开奖为独立随机事件，每一期开奖之间没有关联性，历史结果不构成对未来结果的预测。\n"
    "3. 回测中的历史表现不代表未来表现，任何策略都不能保证中奖或盈利。\n"
    "4. 请理性购彩，量力而行。未成年人禁止购买彩票。"
)

# 页面级短声明（展示在回测/策略/报告页）
SHORT_DISCLAIMER = "彩票开奖为随机事件，历史数据仅供参考，回测不代表未来，理性购彩。"

# 禁用表达词（开发红线：UI/报告/文案不得出现）
FORBIDDEN_EXPRESSIONS = [
    "稳赚",
    "包中",
    "必中",
    "100%中奖",
    "稳赢",
    "保底",
    "中奖率提升到",
    "保证盈利",
    "稳赚不赔",
]


def get_disclaimer() -> str:
    return DISCLAIMER


def get_short_disclaimer() -> str:
    return SHORT_DISCLAIMER


def validate_copy(text: str) -> list:
    """检查文案是否包含禁用表达，返回命中的词列表。"""
    return [w for w in FORBIDDEN_EXPRESSIONS if w in text]
