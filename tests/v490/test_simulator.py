"""v4.9 P1 真实数据模拟环境测试。"""
import os
import csv
import json
import pytest

from engine.user_experiment import (
    SimConfig,
    SimUser,
    UserBehaviorSimulator,
)


@pytest.fixture()
def sim():
    return UserBehaviorSimulator(seed=42)


# ---- 导入 ----
def test_import_users_count(sim):
    users = sim.import_users(["u1", "u2", "u3"])
    assert len(users) == 3
    assert all(u.user_id in ("u1", "u2", "u3") for u in users)


def test_import_users_empty(sim):
    assert sim.import_users([]) == []


def test_import_users_initial_state(sim):
    users = sim.import_users(["u1"])
    assert users[0].installed is False
    assert users[0].saved is False


def test_import_csv(tmp_path, sim):
    p = tmp_path / "users.csv"
    p.write_text("user_id,installed,saved\nu1,1,0\nu2,0,0\n", encoding="utf-8")
    users = sim.import_csv(str(p))
    assert len(users) == 2
    assert users[0].user_id == "u1"
    assert users[0].installed is True
    assert users[0].saved is False


def test_import_csv_missing_file(sim):
    with pytest.raises(FileNotFoundError):
        sim.import_csv("nope.csv")


# ---- 行为路径生成 ----
def test_generate_path_install(sim):
    u = SimUser(user_id="u1")
    evs = sim.generate_path(u, SimConfig(install_complete=1.0, first_save=0.0))
    names = [e.event_name for e in evs]
    assert "app_install" in names
    assert "app_open" in names


def test_generate_path_no_open_when_prob_zero(sim):
    u = SimUser(user_id="u1")
    evs = sim.generate_path(u, SimConfig(install_complete=0.0, first_save=0.0))
    assert [e.event_name for e in evs] == ["app_install"]


def test_generate_path_save_flow(sim):
    u = SimUser(user_id="u1")
    evs = sim.generate_path(u, SimConfig(
        install_complete=1.0, first_save=1.0, reminder_click=1.0,
        claim_check=1.0, report_view=1.0, days=0))
    names = [e.event_name for e in evs]
    assert names == ["app_install", "app_open", "ticket_saved",
                     "draw_reminder_clicked", "claim_checked", "report_viewed"]


def test_generate_path_user_state_updated(sim):
    u = SimUser(user_id="u1")
    sim.generate_path(u, SimConfig(
        install_complete=1.0, first_save=1.0, reminder_click=1.0,
        claim_check=1.0, report_view=1.0, days=0))
    assert u.installed and u.opened and u.saved
    assert u.reminded and u.claimed and u.reviewed


def test_generate_path_premium(sim):
    u = SimUser(user_id="u1")
    evs = sim.generate_path(u, SimConfig(
        install_complete=1.0, first_save=1.0, days=1, daily_open=1.0,
        premium_view_rate=1.0, premium_click_rate=1.0))
    names = [e.event_name for e in evs]
    assert "premium_view" in names
    assert "premium_click" in names


def test_generate_path_weekly_return(sim):
    u = SimUser(user_id="u1")
    evs = sim.generate_path(u, SimConfig(
        install_complete=1.0, first_save=0.0, days=7, daily_open=1.0))
    assert sum(1 for e in evs if e.event_name == "weekly_return") == 2


@pytest.mark.parametrize("seed", [1, 7, 42])
def test_generate_path_seed_reproducible(seed):
    s1 = UserBehaviorSimulator(seed=seed)
    s2 = UserBehaviorSimulator(seed=seed)
    u1 = SimUser(user_id="u1")
    u2 = SimUser(user_id="u1")
    e1 = [e.event_name for e in s1.generate_path(u1, SimConfig(days=3))]
    e2 = [e.event_name for e in s2.generate_path(u2, SimConfig(days=3))]
    assert e1 == e2


# ---- run 全流程 ----
def test_run_returns_all_keys(sim):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(days=0))
    assert set(result.keys()) == {"events", "funnel", "retention", "metrics", "users"}


def test_run_events_generated(sim):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(days=0))
    assert len(result["events"]) >= 1


def test_run_funnel_total_installs(sim):
    users = sim.import_users(["u1", "u2"])
    result = sim.run(users, SimConfig(days=0))
    assert result["funnel"].total_installs == 2


def test_run_metrics_walu(sim):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(install_complete=1.0, first_save=1.0,
                                      days=0))
    assert result["metrics"].walu == 1


def test_run_persists_events(sim, exp_storage):
    users = sim.import_users(["u1"])
    sim.run(users, SimConfig(days=0))
    assert os.path.exists(os.path.join(exp_storage, "experiments_v49.jsonl"))


def test_run_experiment_id(sim):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(days=0), experiment_id="exp-A")
    assert all(e.experiment_id == "exp-A" for e in result["events"])


def test_run_multiple_users(sim):
    users = sim.import_users([f"u{i}" for i in range(10)])
    result = sim.run(users, SimConfig(days=0))
    assert result["funnel"].total_installs == 10


# ---- 导出 ----
def test_export_paths_creates_files(sim, tmp_path):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(days=1))
    out = str(tmp_path)
    paths = sim.export_paths(out, result)
    assert len(paths) == 3
    assert all(os.path.exists(p) for p in paths)


def test_export_user_paths_csv(sim, tmp_path):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(days=0))
    paths = sim.export_paths(str(tmp_path), result)
    with open(paths[0], newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["user_id"] == "u1"


def test_export_user_profiles_csv(sim, tmp_path):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(install_complete=1.0, first_save=1.0,
                                      days=0))
    paths = sim.export_paths(str(tmp_path), result)
    with open(paths[1], newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["user_id"] == "u1"
    assert rows[0]["saved"] == "True"


def test_export_metrics_json(sim, tmp_path):
    users = sim.import_users(["u1"])
    result = sim.run(users, SimConfig(days=0))
    paths = sim.export_paths(str(tmp_path), result)
    with open(paths[2], encoding="utf-8") as f:
        data = json.load(f)
    assert "metrics" in data and "walu" in data


# ---- SimConfig ----
def test_sim_config_defaults():
    c = SimConfig()
    assert c.first_save == 0.60
    assert c.days == 7


@pytest.mark.parametrize("field", ["install_complete", "first_save",
                                   "reminder_click", "claim_check",
                                   "report_view", "daily_open",
                                   "premium_view_rate", "premium_click_rate",
                                   "days"])
def test_sim_config_fields(field):
    c = SimConfig(**{field: 0.123})
    assert getattr(c, field) == 0.123


def test_sim_user_to_dict():
    u = SimUser(user_id="u1")
    d = u.to_dict()
    assert d["user_id"] == "u1"
    assert "installed" in d
