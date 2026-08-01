"""工程测试：验证 Sprint E1 工程化交付物的完整性。

覆盖：项目结构 / Git 治理 / 依赖 / VSCode / 打包 / Docker / CI-CD / 文档 / 桌面模块。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


# ---------- 项目结构 ----------

def test_standard_directories_present():
    """企业级标准目录必须全部存在。"""
    required = [
        "apps", "backend", "engine", "sdk", "plugins", "deployment",
        "scripts", "tools", "tests", "docs", "examples", "assets",
        "branding", "installer", "packaging", "release",
        ".github", ".vscode", "engineering",
    ]
    missing = [d for d in required if not (ROOT / d).is_dir()]
    assert not missing, f"缺少标准目录: {missing}"


# ---------- Git 治理 ----------

@pytest.mark.parametrize(
    "fname",
    [
        "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md", "SECURITY.md", ".gitignore",
        "engineering/Git_Workflow.md", "engineering/Sprint_E1_Architecture.md",
    ],
)
def test_git_governance_files_exist(fname):
    assert (ROOT / fname).is_file(), f"缺少治理文件: {fname}"


def test_gitignore_covers_build_artifacts():
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for token in ("dist/", "build/", ".env", "release/*.exe"):
        assert token in gi, f".gitignore 缺少: {token}"


# ---------- 依赖管理 ----------

@pytest.mark.parametrize(
    "req_file",
    [
        "requirements.txt", "requirements-desktop.txt", "requirements-web.txt",
        "requirements-ai.txt", "requirements-enterprise.txt", "requirements-dev.txt",
        "constraints.txt",
    ],
)
def test_requirements_files_exist(req_file):
    assert (ROOT / req_file).is_file(), f"缺少依赖文件: {req_file}"


@pytest.mark.parametrize(
    "req_file",
    [
        "requirements.txt", "requirements-desktop.txt", "requirements-web.txt",
        "requirements-ai.txt", "requirements-enterprise.txt", "requirements-dev.txt",
        "constraints.txt",
    ],
)
def test_requirements_syntax_valid(req_file):
    import re

    text = (ROOT / req_file).read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r "):
            continue
        assert re.match(r"^[A-Za-z0-9_.\-\[\]]+[<>=!~].*$", line), \
            f"{req_file} 中非法依赖行: {line}"


# ---------- VSCode ----------

@pytest.mark.parametrize("fname", ["settings.json", "launch.json", "tasks.json", "extensions.json"])
def test_vscode_config_valid(fname):
    data = json.loads((ROOT / ".vscode" / fname).read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{fname} 应为 JSON 对象"


def test_vscode_launch_has_desktop_config():
    launch = json.loads((ROOT / ".vscode" / "launch.json").read_text(encoding="utf-8"))
    names = [c["name"] for c in launch["configurations"]]
    assert any("Desktop" in n for n in names), "缺少 Desktop 调试配置"
    assert any("Backend" in n for n in names), "缺少 Backend 调试配置"


# ---------- 打包 ----------

@pytest.mark.parametrize("spec", ["atlas_desktop.spec", "atlas_cli.spec", "atlas_worker.spec"])
def test_packaging_specs_exist(spec):
    assert (ROOT / "packaging" / spec).is_file(), f"缺少 spec: {spec}"


def test_packaging_script_exists():
    assert (ROOT / "packaging" / "package.ps1").is_file()


def test_desktop_entry_exists():
    assert (ROOT / "desktop" / "main.py").is_file()


# ---------- Docker ----------

@pytest.mark.parametrize("fname", ["docker-compose.yml", "compose.override.yml"])
def test_docker_compose_valid(fname):
    import yaml

    data = yaml.safe_load((ROOT / "docker" / fname).read_text(encoding="utf-8"))
    assert "services" in data, f"{fname} 缺少 services"


def test_docker_has_required_services():
    import yaml

    data = yaml.safe_load((ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8"))
    services = set(data["services"].keys())
    assert {"backend", "frontend", "nginx", "db", "redis"} <= services, \
        f"docker 服务缺失: {services}"


# ---------- CI/CD ----------

@pytest.mark.parametrize("wf", ["ci.yml", "release.yml"])
def test_workflow_valid(wf):
    import yaml

    data = yaml.safe_load((ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8"))
    assert "jobs" in data, f"{wf} 缺少 jobs"


def test_ci_has_test_job():
    import yaml

    data = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    assert "test" in data["jobs"], "CI 缺少 test job"


# ---------- 文档 ----------

@pytest.mark.parametrize(
    "guide",
    [
        "00_Quick_Start.md", "01_Developer_Guide.md", "02_User_Guide.md",
        "03_Installation_Guide.md", "04_Deployment_Guide.md", "05_API_Guide.md",
        "06_Plugin_Guide.md", "07_Architecture_Guide.md", "08_FAQ.md",
        "09_Marketplace_Guide.md",
    ],
)
def test_doc_guides_exist(guide):
    assert (ROOT / "docs" / "guides" / guide).is_file(), f"缺少文档: {guide}"


@pytest.mark.parametrize(
    "release_doc",
    ["RELEASE_NOTES.md", "Release_Checklist.md", "Build_Report.md"],
)
def test_release_docs_exist(release_doc):
    assert (ROOT / "release" / release_doc).is_file(), f"缺少发布文档: {release_doc}"


# ---------- 桌面模块可导入 ----------

def test_desktop_modules_importable():
    """桌面核心模块应可导入（跳过 GUI 实例化）。"""
    sys.path.insert(0, str(ROOT / "desktop"))
    import data_loader  # noqa: F401
    import stats  # noqa: F401
    from pages import dashboard_page, analysis_page, strategy_page  # noqa: F401

    draws = data_loader.load_draws()
    assert len(draws) > 0, "内置数据为空"
    assert stats.hot_numbers(draws), "统计计算失败"
