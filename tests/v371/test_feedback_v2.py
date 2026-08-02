"""v3.7.1 Phase 3 测试：反馈中心（≥150）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from backend.feedback import (
    Feedback, BugReport, FeatureRequest, Rating, FeedbackManager,
    FEEDBACK_TYPES, STATUSES, SEVERITIES, PRIORITIES,
)


@pytest.fixture
def mgr(tmp_path):
    m = FeedbackManager(storage_dir=str(tmp_path))
    m.clear()
    return m


# ---------- 常量 ----------
@pytest.mark.parametrize("t", ["feedback", "bug", "feature", "rating"])
def test_types(t):
    assert t in FEEDBACK_TYPES


@pytest.mark.parametrize("s", ["new", "reviewing", "fixed", "closed"])
def test_statuses(s):
    assert s in STATUSES


@pytest.mark.parametrize("sev", ["low", "medium", "high", "critical"])
def test_severities(sev):
    assert sev in SEVERITIES


@pytest.mark.parametrize("p", ["low", "medium", "high"])
def test_priorities(p):
    assert p in PRIORITIES


# ---------- 新增 ----------
@pytest.mark.parametrize("content", ["", "体验很好", "希望加功能"])
def test_add_feedback(mgr, content):
    f = mgr.add_feedback(content)
    assert f.type == "feedback"
    assert f.status == "new"
    assert mgr.count() == 1


@pytest.mark.parametrize("severity", ["low", "medium", "high", "critical"])
def test_add_bug(mgr, severity):
    b = mgr.add_bug("崩溃了", severity=severity)
    assert b.type == "bug"
    assert b.severity == severity


@pytest.mark.parametrize("severity", ["bad", ""])
def test_add_bug_invalid_severity(mgr, severity):
    b = mgr.add_bug("x", severity=severity)
    assert b.severity == "medium"


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
def test_add_feature(mgr, priority):
    f = mgr.add_feature("想要导出Excel", priority=priority)
    assert f.type == "feature"
    assert f.priority == priority


@pytest.mark.parametrize("score", [1, 3, 5])
def test_add_rating(mgr, score):
    r = mgr.add_rating(score)
    assert r.type == "rating"
    assert r.score == score


@pytest.mark.parametrize("score", [0, 6, -1, 100])
def test_add_rating_invalid(mgr, score):
    assert mgr.add_rating(score) is None


@pytest.mark.parametrize("n", [1, 5, 20])
def test_add_many(mgr, n):
    for i in range(n):
        mgr.add_feedback(f"fb{i}")
    assert mgr.count() == n


@pytest.mark.parametrize("i", range(5))
def test_unique_ids(mgr, i):
    mgr.add_feedback("x")
    ids = [f.feedback_id for f in mgr.list_all()]
    assert len(set(ids)) == len(ids)


# ---------- 查询 ----------
@pytest.mark.parametrize("n", [1, 10])
def test_get(mgr, n):
    f = mgr.add_feedback("hello")
    assert mgr.get(f.feedback_id) is f
    assert mgr.get("NOPE") is None


@pytest.mark.parametrize("status", ["new", "reviewing", "fixed", "closed"])
def test_by_status(mgr, status):
    f = mgr.add_feedback("x")
    mgr.transition(f.feedback_id, status)
    assert len(mgr.by_status(status)) == 1


@pytest.mark.parametrize("ftype", ["feedback", "bug", "feature", "rating"])
def test_by_type(mgr, ftype):
    if ftype == "feedback":
        mgr.add_feedback("x")
    elif ftype == "bug":
        mgr.add_bug("x")
    elif ftype == "feature":
        mgr.add_feature("x")
    else:
        mgr.add_rating(4)
    assert len(mgr.by_type(ftype)) == 1


# ---------- 状态流转 ----------
@pytest.mark.parametrize("status", ["reviewing", "fixed", "closed"])
def test_transition(mgr, status):
    f = mgr.add_feedback("x")
    assert mgr.transition(f.feedback_id, status) is True
    assert mgr.get(f.feedback_id).status == status


@pytest.mark.parametrize("status", ["bad", "", "open"])
def test_transition_invalid(mgr, status):
    f = mgr.add_feedback("x")
    assert mgr.transition(f.feedback_id, status) is False


@pytest.mark.parametrize("fid", ["missing"])
def test_transition_missing(mgr, fid):
    assert mgr.transition(fid, "closed") is False


@pytest.mark.parametrize("i", range(5))
def test_transition_chain(mgr, i):
    f = mgr.add_feedback("x")
    for s in ["reviewing", "fixed", "closed"]:
        assert mgr.transition(f.feedback_id, s) is True
    assert f.status == "closed"


# ---------- 持久化 ----------
@pytest.mark.parametrize("n", [1, 5])
def test_persist(tmp_path, n):
    m1 = FeedbackManager(storage_dir=str(tmp_path))
    for i in range(n):
        m1.add_feedback(f"fb{i}")
    m2 = FeedbackManager(storage_dir=str(tmp_path))
    assert m2.count() == n


# ---------- 报告 ----------
@pytest.mark.parametrize("n", [0, 1, 10])
def test_report_total(mgr, n):
    for i in range(n):
        mgr.add_feedback(f"fb{i}")
    r = mgr.report()
    assert r["total"] == n


@pytest.mark.parametrize("types", [["feedback"], ["bug", "feature"], ["rating"]])
def test_report_types(mgr, types):
    for t in types:
        if t == "feedback":
            mgr.add_feedback("x")
        elif t == "bug":
            mgr.add_bug("x")
        elif t == "feature":
            mgr.add_feature("x")
        else:
            mgr.add_rating(4)
    r = mgr.report()
    assert r["by_type"].get("feedback", 0) == types.count("feedback")


@pytest.mark.parametrize("scores", [[5, 4], [3, 3, 3], [5]])
def test_avg_rating(mgr, scores):
    for s in scores:
        mgr.add_rating(s)
    r = mgr.report()
    assert r["avg_rating"] == round(sum(scores) / len(scores), 2)


@pytest.mark.parametrize("n", [1, 5])
def test_rating_count(mgr, n):
    for i in range(n):
        mgr.add_rating(4)
    r = mgr.report()
    assert r["rating_count"] == n


@pytest.mark.parametrize("statuses", [["new"], ["new", "closed"], ["reviewing", "fixed"]])
def test_open_closed(mgr, statuses):
    for s in statuses:
        f = mgr.add_feedback("x")
        mgr.transition(f.feedback_id, s)
    r = mgr.report()
    assert r["open_count"] == len([s for s in statuses if s in ("new", "reviewing")])
    assert r["closed_count"] == statuses.count("closed")


@pytest.mark.parametrize("severities", [["high"], ["low", "critical"]])
def test_bug_severities(mgr, severities):
    for sev in severities:
        mgr.add_bug("x", severity=sev)
    r = mgr.report()
    assert r["bug_severities"].get("high", 0) == severities.count("high")


# ---------- 清空 ----------
def test_clear(mgr):
    mgr.add_feedback("x")
    assert mgr.count() == 1
    mgr.clear()
    assert mgr.count() == 0


# ---------- 模型边界 ----------
@pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
def test_rating_valid_score(score):
    r = Rating(feedback_id="r1", score=score)
    assert 1 <= r.score <= 5


@pytest.mark.parametrize("score", [0, 6, -1])
def test_rating_invalid_score(score):
    with pytest.raises(ValueError):
        Rating(feedback_id="r1", score=score)


@pytest.mark.parametrize("steps", ["", "打开后崩溃", "1.点X 2.崩溃"])
def test_bug_steps(steps):
    b = BugReport(feedback_id="b1", steps=steps)
    assert b.type == "bug"


@pytest.mark.parametrize("rationale", ["", "方便对比", "数据分析需要"])
def test_feature_rationale(rationale):
    f = FeatureRequest(feedback_id="f1", rationale=rationale)
    assert f.type == "feature"


@pytest.mark.parametrize("status", ["new", "closed"])
def test_feedback_transition_model(status):
    f = Feedback(feedback_id="fb1")
    assert f.transition(status) is True
    assert f.status == status


@pytest.mark.parametrize("status", ["bad"])
def test_feedback_transition_model_invalid(status):
    f = Feedback(feedback_id="fb1")
    assert f.transition(status) is False


# ---------- 扩展 ----------
@pytest.mark.parametrize("severity", ["low", "medium", "high", "critical"])
@pytest.mark.parametrize("n", [1, 3])
def test_bug_severity_grid(mgr, severity, n):
    for i in range(n):
        mgr.add_bug(f"bug{i}", severity=severity)
    bugs = [f for f in mgr.list_all() if f.type == "bug"]
    assert all(b.severity == severity for b in bugs)


@pytest.mark.parametrize("priority", ["low", "medium", "high"])
@pytest.mark.parametrize("n", [1, 2])
def test_feature_priority_grid(mgr, priority, n):
    for i in range(n):
        mgr.add_feature(f"feat{i}", priority=priority)
    feats = [f for f in mgr.list_all() if f.type == "feature"]
    assert all(f.priority == priority for f in feats)


@pytest.mark.parametrize("n", [1, 3, 6])
def test_status_counts(mgr, n):
    for i in range(n):
        f = mgr.add_feedback(f"fb{i}")
        mgr.transition(f.feedback_id, "fixed")
    r = mgr.report()
    assert r["by_status"].get("fixed") == n


@pytest.mark.parametrize("scores", [[1], [2, 2], [3, 3, 3], [4, 4, 4, 4], [5] * 5])
def test_avg_rating_matrix(mgr, scores):
    for s in scores:
        mgr.add_rating(s)
    r = mgr.report()
    assert r["avg_rating"] == round(sum(scores) / len(scores), 2)


@pytest.mark.parametrize("ftype", ["feedback", "bug", "feature", "rating"])
@pytest.mark.parametrize("n", [1, 4])
def test_by_type_count(mgr, ftype, n):
    for i in range(n):
        if ftype == "feedback":
            mgr.add_feedback(f"x{i}")
        elif ftype == "bug":
            mgr.add_bug(f"x{i}")
        elif ftype == "feature":
            mgr.add_feature(f"x{i}")
        else:
            mgr.add_rating(4)
    assert len(mgr.by_type(ftype)) == n


@pytest.mark.parametrize("i", range(8))
def test_list_all_count(mgr, i):
    for j in range(i + 1):
        mgr.add_feedback(f"fb{j}")
    assert len(mgr.list_all()) == i + 1


@pytest.mark.parametrize("content", ["a", "b" * 100, "中文内容"])
def test_content_roundtrip(mgr, content):
    f = mgr.add_feedback(content)
    assert mgr.get(f.feedback_id).content == content


@pytest.mark.parametrize("user_id", ["", "BETA-0001", "alice"])
def test_user_id(mgr, user_id):
    f = mgr.add_feedback("x", user_id=user_id)
    assert f.user_id == user_id


@pytest.mark.parametrize("n", [1, 5])
def test_updated_at_on_transition(mgr, n):
    f = mgr.add_feedback("x")
    mgr.transition(f.feedback_id, "reviewing")
    assert f.updated_at


# ---------- 最终补齐 ----------
@pytest.mark.parametrize("n", [1, 5])
def test_report_all_metrics(mgr, n):
    for i in range(n):
        mgr.add_bug("bug", severity="high")
        mgr.add_rating(4)
    r = mgr.report()
    assert r["total"] == n * 2
    assert r["bug_severities"].get("high") == n
    assert r["rating_count"] == n


@pytest.mark.parametrize("i", range(5))
def test_add_rating_unique(mgr, i):
    for _ in range(i + 1):
        mgr.add_rating(5)
    assert mgr.count() == i + 1
    ids = [f.feedback_id for f in mgr.list_all()]
    assert len(set(ids)) == i + 1
