"""feedback_intelligence - 反馈智能分析。"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

# 关键词分类
CATEGORY_KEYWORDS = {
    "bug": ["崩溃", "报错", "错误", "无法", "失效", "闪退", "异常"],
    "feature": ["希望", "建议", "想要", "增加", "支持", "优化"],
    "data": ["数据", "期数", "更新", "彩种", "号码"],
    "export": ["导出", "保存", "下载", "文件", "pdf", "csv"],
    "ui": ["界面", "显示", "布局", "按钮", "文字", "中文"],
}


@dataclass
class FeedbackInsight:
    """反馈洞察。"""

    total: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    top_keywords: List[tuple] = field(default_factory=list)
    open_rate: float = 0.0
    priority_order: List[str] = field(default_factory=list)

    def to_text(self) -> str:
        lines = ["💬 Atlas 反馈智能"]
        lines.append(f"· 反馈总数：{self.total}")
        lines.append("· 分类：" + ", ".join(f"{k}={v}" for k, v in sorted(self.by_category.items())))
        if self.top_keywords:
            lines.append("· 高频词：" + "、".join(f"{w}({c})" for w, c in self.top_keywords[:6]))
        lines.append(f"· 处理率：{(1 - self.open_rate) * 100:.0f}%")
        return "\n".join(lines)


def _categorize(text: str) -> str:
    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in text:
                return cat
    return "other"


class FeedbackIntelligence:
    """反馈智能分析器。"""

    @staticmethod
    def analyze(feedback_items: List[dict]) -> FeedbackInsight:
        """分析反馈列表。item: {content, status, ...}"""
        ins = FeedbackInsight(total=len(feedback_items))
        cat_counter: Counter = Counter()
        keyword_counter: Counter = Counter()
        open_items = 0
        for item in feedback_items:
            content = item.get("content", "")
            cat = _categorize(content)
            cat_counter[cat] += 1
            status = item.get("status", "new")
            if status in ("new", "reviewing"):
                open_items += 1
            for w in content.replace("，", " ").replace("。", " ").split():
                if len(w) >= 2 and w not in ("一个", "我们", "这个", "可以", "希望", "问题"):
                    keyword_counter[w] += 1
        ins.by_category = dict(cat_counter)
        ins.top_keywords = keyword_counter.most_common(10)
        ins.open_rate = open_items / len(feedback_items) if feedback_items else 0.0
        # 优先级：bug > data > feature > ui > export > other（按需调整）
        order = ["bug", "data", "feature", "ui", "export", "other"]
        ins.priority_order = [c for c in order if cat_counter.get(c, 0) > 0]
        return ins
