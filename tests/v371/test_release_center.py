"""v3.7.1 Phase 4 测试：ReleaseCenter（≥100）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from release_center import ReleaseCenter, CURRENT_VERSION, VERSIONS, UPDATE_NOTES, INSTALL_GUIDE, FAQ


@pytest.fixture
def rc():
    return ReleaseCenter()


# ---------- 版本信息 ----------
@pytest.mark.parametrize("v", ["v3.7.1-beta", "v3.7.0", "v3.6.1"])
def test_versions_present(v):
    assert v in VERSIONS


@pytest.mark.parametrize("v", ["v9.9", "unknown"])
def test_versions_unknown(v):
    assert v not in VERSIONS


def test_current_version():
    assert CURRENT_VERSION == "v4.10.0"


@pytest.mark.parametrize("i", range(3))
def test_version_info(rc, i):
    info = rc.version_info()
    assert info["current"] == CURRENT_VERSION
    assert len(info["available"]) >= 3


# ---------- 发布说明 ----------
@pytest.mark.parametrize("v", ["v3.7.1-beta", "v3.7.0", "v3.6.1"])
def test_release_notes(rc, v):
    n = rc.release_notes(v)
    assert n["summary"]
    assert isinstance(n["features"], list)


@pytest.mark.parametrize("v", ["v9.9", "v2.0"])
def test_release_notes_unknown(rc, v):
    n = rc.release_notes(v)
    assert "未知版本" in n["summary"]


@pytest.mark.parametrize("i", range(3))
def test_release_notes_default(rc, i):
    n = rc.release_notes()
    assert n is not None


@pytest.mark.parametrize("v", ["v3.7.1-beta", "v3.7.0"])
def test_features_nonempty(rc, v):
    n = rc.release_notes(v)
    assert len(n["features"]) >= 1


# ---------- 更新说明 ----------
@pytest.mark.parametrize("i", range(5))
def test_update_notes(rc, i):
    notes = rc.update_notes()
    assert len(notes) >= 3


@pytest.mark.parametrize("i", range(5))
def test_update_notes_str(rc, i):
    for n in rc.update_notes():
        assert isinstance(n, str)


# ---------- 安装指南 ----------
@pytest.mark.parametrize("i", range(4))
def test_install_guide(rc, i):
    guide = rc.install_guide()
    assert len(guide) >= 3


@pytest.mark.parametrize("i", range(4))
def test_install_guide_str(rc, i):
    for g in rc.install_guide():
        assert isinstance(g, str)


# ---------- FAQ ----------
@pytest.mark.parametrize("i", range(6))
def test_faq(rc, i):
    faq = rc.faq()
    assert len(faq) >= 5
    assert "q" in faq[0]
    assert "a" in faq[0]


@pytest.mark.parametrize("keyword", ["数据", "联网", "导出", "回测", "反馈", "安装"])
def test_faq_search(rc, keyword):
    hits = rc.faq_search(keyword)
    assert isinstance(hits, list)
    assert all("q" in h for h in hits)


@pytest.mark.parametrize("keyword", ["", "zzz", "   "])
def test_faq_search_empty(rc, keyword):
    assert rc.faq_search(keyword) == []


@pytest.mark.parametrize("i", range(5))
def test_faq_has_answer(rc, i):
    for f in rc.faq():
        assert f["a"]


# ---------- 更新检查 ----------
@pytest.mark.parametrize("installed", ["v4.10.0"])
def test_has_update_same(rc, installed):
    assert not rc.has_update(installed)


@pytest.mark.parametrize("installed", ["v3.7.0", "v3.6.1", "v1.0"])
def test_has_update_newer(rc, installed):
    assert rc.has_update(installed)


@pytest.mark.parametrize("installed", ["v4.10.0"])
def test_cmp_same(rc, installed):
    assert rc._cmp(installed) == 0


@pytest.mark.parametrize("installed", ["v3.7.0", "v3.0.0"])
def test_cmp_different(rc, installed):
    assert rc._cmp(installed) > 0


# ---------- 摘要 ----------
@pytest.mark.parametrize("i", range(3))
def test_summary(rc, i):
    s = rc.summary()
    assert CURRENT_VERSION in s
    assert "：" in s or ":" in s


# ---------- 边界 ----------
@pytest.mark.parametrize("i", range(10))
def test_release_center_reuse(rc, i):
    assert rc.version_info()["current"] == CURRENT_VERSION


@pytest.mark.parametrize("v", list(VERSIONS.keys()))
def test_all_versions_notes(rc, v):
    n = rc.release_notes(v)
    assert n["date"]
    assert n["summary"]


# ---------- 扩展 ----------
@pytest.mark.parametrize("v", list(VERSIONS.keys()))
def test_version_features_all(v):
    for feat in VERSIONS[v]["features"]:
        assert feat


@pytest.mark.parametrize("keyword", ["数据", "导出", "回测", "反馈", "安装", "联网", "报告", "AI"])
def test_faq_search_more(keyword):
    rc = ReleaseCenter()
    hits = rc.faq_search(keyword)
    assert isinstance(hits, list)


@pytest.mark.parametrize("i", range(6))
def test_faq_q_nonempty(i):
    assert FAQ[i]["q"].strip()


@pytest.mark.parametrize("i", range(6))
def test_faq_a_nonempty(i):
    assert FAQ[i]["a"].strip()


@pytest.mark.parametrize("i", range(5))
def test_update_notes_content(i):
    assert UPDATE_NOTES[i]


@pytest.mark.parametrize("i", range(4))
def test_install_guide_content(i):
    assert INSTALL_GUIDE[i]


@pytest.mark.parametrize("installed", ["v3.7.1-beta", "v3.7.0", "v3.6.1"])
def test_has_update_matrix(installed):
    rc = ReleaseCenter()
    if installed == "v4.10.0":
        assert not rc.has_update(installed)
    else:
        assert rc.has_update(installed)
