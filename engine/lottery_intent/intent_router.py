"""lottery_intent - 意图路由（LotteryIntentRouter）。

识别用户输入是否为「兑奖计算」任务，并判断彩种（大乐透/双色球）。
"""
from __future__ import annotations

from dataclasses import dataclass

# 彩种关键词
DLT_KEYWORDS = ["大乐透", "dlt", "超级大乐透"]
SSQ_KEYWORDS = ["双色球", "ssq", "福彩"]

# 兑奖/中奖意图关键词
PRIZE_INTENT_KEYWORDS = [
    "中了", "中奖", "中多少", "奖金", "兑奖", "赚了", "多少钱",
    "有没有中", "兑了", "中了吗", "算算", "帮我算",
]


@dataclass
class IntentResult:
    """意图识别结果。"""

    is_prize_intent: bool = False
    lottery: str = ""          # dlt / ssq / ""
    confidence: float = 0.0    # 0-1

    def to_dict(self) -> dict:
        return {"is_prize_intent": self.is_prize_intent, "lottery": self.lottery, "confidence": round(self.confidence, 2)}


class LotteryIntentRouter:
    """意图路由器。"""

    @staticmethod
    def _detect_lottery(text: str) -> str:
        tl = text.lower()
        for k in SSQ_KEYWORDS:
            if k in tl:
                return "ssq"
        for k in DLT_KEYWORDS:
            if k in tl:
                return "dlt"
        # 未明说彩种时，按号码特征推断（由 TicketParser 补充）
        return ""

    @staticmethod
    def detect(text: str) -> IntentResult:
        """识别输入意图。"""
        if not text or not text.strip():
            return IntentResult()
        tl = text.lower()
        # 意图匹配
        hit = 0
        for k in PRIZE_INTENT_KEYWORDS:
            if k in tl:
                hit += 1
        is_prize = hit > 0
        lottery = LotteryIntentRouter._detect_lottery(text)
        # 若文本含号码（数字+可能的中奖意图），也视为兑奖候选
        import re
        has_numbers = bool(re.search(r"\d{1,2}", text))
        if is_prize or (has_numbers and any(k in tl for k in ["买", "号码", "注", "票"])):
            is_prize = True
        # 置信度：彩种明确 + 意图明确 → 高
        conf = 0.0
        if is_prize:
            conf = 0.7
            if lottery:
                conf = 0.95
            if hit >= 2:
                conf = min(1.0, conf + 0.05)
        return IntentResult(is_prize_intent=is_prize, lottery=lottery, confidence=conf)
