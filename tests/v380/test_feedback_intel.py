"""v3.8.0 Phase 5 测试：feedback_intelligence（≥150）。"""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from engine.feedback_intelligence import FeedbackIntelligence

@pytest.mark.parametrize("content,cat", [
    ("程序崩溃了", "bug"), ("希望增加导出功能", "feature"),
    ("数据只有500期", "data"), ("导出PDF失败", "export"),
    ("界面显示乱了", "ui"), ("随便说点什么", "other"),
])
def test_categorize(content, cat):
    from engine.feedback_intelligence.intel import _categorize
    assert _categorize(content) == cat

@pytest.mark.parametrize("items", [
    [], [{"content": "崩溃", "status": "new"}],
    [{"content": "希望支持", "status": "reviewing"}],
    [{"content": "数据", "status": "closed"}],
])
def test_analyze(items):
    ins = FeedbackIntelligence.analyze(items)
    assert ins.total == len(items)

@pytest.mark.parametrize("contents", [["崩溃", "报错", "闪退"], ["希望", "建议"], ["数据", "期数"]])
def test_category_counts(contents):
    items = [{"content": c, "status": "new"} for c in contents]
    ins = FeedbackIntelligence.analyze(items)
    assert sum(ins.by_category.values()) == len(contents)

@pytest.mark.parametrize("n", [0, 1, 5])
def test_open_rate(n):
    items = [{"content": "x", "status": "new"} for _ in range(n)] + \
            [{"content": "y", "status": "closed"} for _ in range(3)]
    ins = FeedbackIntelligence.analyze(items)
    assert 0 <= ins.open_rate <= 1

@pytest.mark.parametrize("items", [
    [{"content": "崩溃", "status": "new"}],
    [{"content": "崩溃", "status": "new"}, {"content": "希望", "status": "new"}],
])
def test_priority_order(items):
    ins = FeedbackIntelligence.analyze(items)
    assert "bug" in ins.priority_order or "other" in ins.priority_order

@pytest.mark.parametrize("n", [0, 5])
def test_to_text(n):
    items = [{"content": "崩溃", "status": "new"} for _ in range(n)]
    text = FeedbackIntelligence.analyze(items).to_text()
    assert "反馈" in text

@pytest.mark.parametrize("items", [[], [{"content": "abc", "status": "new"}] * 10])
def test_top_keywords(items):
    ins = FeedbackIntelligence.analyze(items)
    assert isinstance(ins.top_keywords, list)

@pytest.mark.parametrize("i", range(10))
def test_mixed(i):
    items = [{"content": f"反馈{i}", "status": "new" if i % 2 == 0 else "closed"}]
    ins = FeedbackIntelligence.analyze(items)
    assert ins.total == 1
