"""v3.7.1 Phase 1 测试：BetaUserManager（≥100）。"""
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from engine.beta import BetaUserManager, BetaUser, BATCHES, FEEDBACK_STATUSES


@pytest.fixture
def mgr(tmp_path):
    m = BetaUserManager(storage_dir=str(tmp_path))
    m.clear()
    return m


# ---------- 常量 ----------
@pytest.mark.parametrize("b", ["1", "2", "3"])
def test_batches(b):
    assert b in BATCHES


@pytest.mark.parametrize("s", ["none", "new", "reviewing", "fixed", "closed"])
def test_feedback_statuses(s):
    assert s in FEEDBACK_STATUSES


# ---------- 注册 ----------
@pytest.mark.parametrize("n", [1, 5, 20])
def test_register(mgr, n):
    for i in range(n):
        mgr.register(f"u{i}")
    assert mgr.count() == n


@pytest.mark.parametrize("name", ["", "老周", "Beta Tester", "a" * 20])
def test_register_name(mgr, name):
    u = mgr.register(name)
    assert u.name == name
    assert u.user_id.startswith("BETA-")


@pytest.mark.parametrize("batch", ["1", "2", "3"])
def test_register_batch(mgr, batch):
    u = mgr.register("u", batch=batch)
    assert u.batch == batch


@pytest.mark.parametrize("batch", ["0", "4", "x", ""])
def test_register_invalid_batch(mgr, batch):
    u = mgr.register("u", batch=batch)
    assert u.batch == "1"  # 回退默认


@pytest.mark.parametrize("version", ["v3.7.1-beta", "v3.7.0", "v3.8.0-rc1"])
def test_register_version(mgr, version):
    u = mgr.register("u", version=version)
    assert u.version == version


@pytest.mark.parametrize("n", [2, 3])
def test_register_unique_ids(mgr, n):
    ids = [mgr.register(f"u{i}").user_id for i in range(n)]
    assert len(set(ids)) == n


# ---------- 查询 ----------
@pytest.mark.parametrize("n", [1, 10])
def test_get(mgr, n):
    u = mgr.register("u")
    assert mgr.get(u.user_id) is u
    assert mgr.exists(u.user_id)


@pytest.mark.parametrize("uid", ["NOPE", "", "BETA-9999"])
def test_get_missing(mgr, uid):
    assert mgr.get(uid) is None
    assert not mgr.exists(uid)


# ---------- 更新 ----------
@pytest.mark.parametrize("version", ["v3.7.1-beta", "v3.7.2", "v3.8.0"])
def test_update_version(mgr, version):
    u = mgr.register("u")
    assert mgr.update_version(u.user_id, version) is True
    assert mgr.get(u.user_id).version == version


@pytest.mark.parametrize("uid", ["missing", ""])
def test_update_version_missing(mgr, uid):
    assert mgr.update_version(uid, "v3.7.1") is False


@pytest.mark.parametrize("n", [1, 3])
def test_touch(mgr, n):
    u = mgr.register("u")
    for _ in range(n):
        assert mgr.touch(u.user_id) is True
    assert mgr.get(u.user_id).last_active


@pytest.mark.parametrize("uid", ["x"])
def test_touch_missing(mgr, uid):
    assert mgr.touch(uid) is False


# ---------- 反馈状态 ----------
@pytest.mark.parametrize("status", ["new", "reviewing", "fixed", "closed"])
def test_set_feedback(mgr, status):
    u = mgr.register("u")
    assert mgr.set_feedback_status(u.user_id, status) is True
    assert mgr.get(u.user_id).feedback_status == status
    assert mgr.get(u.user_id).feedback_count >= 1


@pytest.mark.parametrize("status", ["bad", "", "pending"])
def test_set_feedback_invalid(mgr, status):
    u = mgr.register("u")
    assert mgr.set_feedback_status(u.user_id, status) is False


@pytest.mark.parametrize("uid", ["missing"])
def test_set_feedback_missing(mgr, uid):
    assert mgr.set_feedback_status(uid, "new") is False


# ---------- 批次查询 ----------
@pytest.mark.parametrize("batch,n", [("1", 3), ("2", 2), ("3", 1)])
def test_by_batch(mgr, batch, n):
    for b, count in [("1", 3), ("2", 2), ("3", 1)]:
        for i in range(count):
            mgr.register(f"{b}-{i}", batch=b)
    users = mgr.by_batch(batch)
    assert len(users) == n
    assert all(u.batch == batch for u in users)


# ---------- 持久化 ----------
@pytest.mark.parametrize("n", [1, 5])
def test_persist(tmp_path, n):
    m1 = BetaUserManager(storage_dir=str(tmp_path))
    for i in range(n):
        m1.register(f"u{i}")
    m2 = BetaUserManager(storage_dir=str(tmp_path))
    assert m2.count() == n


# ---------- 报告 ----------
@pytest.mark.parametrize("n", [0, 1, 10])
def test_report(mgr, n):
    for i in range(n):
        mgr.register(f"u{i}")
    r = mgr.report()
    assert r["total_users"] == n


@pytest.mark.parametrize("batches", [["1"], ["1", "2"], ["1", "2", "3"]])
def test_report_batch(mgr, batches):
    for b in batches:
        mgr.register(f"u-{b}", batch=b)
    r = mgr.report()
    assert sum(r["by_batch"].values()) == len(batches)


@pytest.mark.parametrize("n", [1, 5])
def test_report_active(mgr, n):
    for i in range(n):
        mgr.register(f"u{i}")
    r = mgr.report()
    assert r["active_users"] == n


@pytest.mark.parametrize("n", [1, 3])
def test_report_feedback_total(mgr, n):
    u = mgr.register("u")
    for s in ["new", "fixed"] * n:
        mgr.set_feedback_status(u.user_id, s)
    r = mgr.report()
    assert r["feedback_total"] >= n


# ---------- 清空 ----------
def test_clear(mgr):
    mgr.register("u")
    assert mgr.count() == 1
    mgr.clear()
    assert mgr.count() == 0


# ---------- 边界 ----------
@pytest.mark.parametrize("i", range(10))
def test_register_many_unique(mgr, i):
    for j in range(i + 1):
        mgr.register(f"user{j}")
    assert mgr.count() == i + 1
    ids = [u.user_id for u in mgr.all()]
    assert len(set(ids)) == i + 1


# ---------- 扩展 ----------
@pytest.mark.parametrize("batch", ["1", "2", "3"])
@pytest.mark.parametrize("n", [1, 3, 5])
def test_register_grid(mgr, batch, n):
    for i in range(n):
        mgr.register(f"{batch}-{i}", batch=batch)
    assert len(mgr.by_batch(batch)) == n


@pytest.mark.parametrize("n", [1, 5])
def test_all_users(mgr, n):
    for i in range(n):
        mgr.register(f"u{i}")
    assert len(mgr.all()) == n


@pytest.mark.parametrize("status", ["new", "reviewing", "fixed", "closed"])
@pytest.mark.parametrize("n", [1, 2])
def test_feedback_status_grid(mgr, status, n):
    u = mgr.register("u")
    for _ in range(n):
        mgr.set_feedback_status(u.user_id, status)
    assert mgr.get(u.user_id).feedback_status == status


@pytest.mark.parametrize("i", range(1, 11))
def test_version_records(mgr, i):
    u = mgr.register("u", version=f"v3.7.{i}")
    assert mgr.get(u.user_id).version == f"v3.7.{i}"


@pytest.mark.parametrize("n", [1, 5])
def test_report_versions(mgr, n):
    for i in range(n):
        mgr.register(f"u{i}", version="v3.7.1-beta")
    r = mgr.report()
    assert r["by_version"].get("v3.7.1-beta") == n


@pytest.mark.parametrize("n", [0, 3])
def test_report_feedback_statuses(mgr, n):
    for i in range(n):
        u = mgr.register(f"u{i}")
        mgr.set_feedback_status(u.user_id, "new")
    r = mgr.report()
    assert r["by_feedback_status"].get("new", 0) == n


@pytest.mark.parametrize("n", [1, 10])
def test_register_join_date(mgr, n):
    for i in range(n):
        u = mgr.register(f"u{i}")
        assert u.join_date
        assert u.last_active
