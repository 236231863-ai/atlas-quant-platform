"""v3.6.1 安装/发布流程测试：setup.iss / spec / 版本 / requirements / 产物规范。"""
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


# ---------- 安装器 setup.iss ----------
SETUP_ISS = os.path.join(ROOT, "installer", "setup.iss")

@pytest.mark.parametrize("token", [
    "MyAppName", "DefaultDirName", "OutputDir", "OutputBaseFilename",
    "AppVersion", "PrivilegesRequired", "UninstallDisplayIcon",
])
def test_setup_iss_has_sections(token):
    content = _read(SETUP_ISS)
    assert token in content


@pytest.mark.parametrize("keyword", [
    "[Setup]", "[Files]", "[Icons]", "[Run]", "[Tasks]",
])
def test_setup_iss_sections(keyword):
    content = _read(SETUP_ISS)
    assert keyword in content


@pytest.mark.parametrize("filename", [
    "Atlas_Setup", "Atlas.exe", "Atlas_CLI.exe", "Atlas_Worker.exe",
])
def test_setup_iss_refs_exe(filename):
    content = _read(SETUP_ISS)
    assert filename in content


@pytest.mark.parametrize("pattern", [
    r"3\.8\.0", r"Atlas Quant Platform",
])
def test_setup_iss_version(pattern):
    content = _read(SETUP_ISS)
    assert re.search(pattern, content)


# ---------- PyInstaller spec ----------
@pytest.mark.parametrize("spec_file", [
    "packaging/atlas_desktop.spec",
    "packaging/atlas_cli.spec",
    "packaging/atlas_worker.spec",
])
def test_spec_exists(spec_file):
    p = os.path.join(ROOT, spec_file)
    assert os.path.exists(p)


@pytest.mark.parametrize("spec_file,needle", [
    ("packaging/atlas_desktop.spec", "Atlas.exe"),
    ("packaging/atlas_desktop.spec", "data"),
])
def test_desktop_spec_content(spec_file, needle):
    p = os.path.join(ROOT, spec_file)
    assert needle in _read(p)


# ---------- 版本一致性 ----------
@pytest.mark.parametrize("path,needle", [
    ("pyproject.toml", "4.0.0"),
    ("desktop/windows/main_window.py", "v4.6.0"),
    ("CHANGELOG.md", "4.0.0"),
])
def test_version_consistency(path, needle):
    p = os.path.join(ROOT, path)
    assert needle in _read(p)


# ---------- requirements 家族 ----------
@pytest.mark.parametrize("req", [
    "requirements.txt", "requirements-dev.txt", "requirements-desktop.txt",
    "requirements-web.txt", "requirements-ai.txt", "constraints.txt",
])
def test_requirements_exist(req):
    assert os.path.exists(os.path.join(ROOT, req))


@pytest.mark.parametrize("pkg", ["PySide6", "matplotlib", "fpdf2", "pytest", "fastapi"])
def test_requirements_cover_pkgs(pkg):
    all_reqs = "\n".join(_read(os.path.join(ROOT, f)) for f in
                         ["requirements.txt", "requirements-dev.txt", "requirements-desktop.txt", "requirements-ai.txt"])
    assert pkg.lower() in all_reqs.lower()


# ---------- 产物路径规范 ----------
@pytest.mark.parametrize("path", [
    "dist", "release", "packaging", "installer", "docs/audit",
])
def test_dirs_exist(path):
    assert os.path.isdir(os.path.join(ROOT, path))


# ---------- 新模块存在性 ----------
@pytest.mark.parametrize("path", [
    "engine/data_center_v2/__init__.py",
    "engine/data_center_v2/models.py",
    "engine/data_center_v2/sources.py",
    "engine/data_center_v2/quality.py",
    "engine/evaluation_v2/__init__.py",
    "engine/evaluation_v2/split.py",
    "engine/evaluation_v2/baseline.py",
    "engine/evaluation_v2/metrics.py",
    "engine/evaluation_v2/disclaimer.py",
    "engine/export/__init__.py",
    "engine/export/markdown.py",
    "engine/export/csv.py",
    "engine/export/png.py",
    "engine/export/pdf.py",
    "desktop/health.py",
    "tools/fetch_lottery_data.py",
])
def test_v361_modules_exist(path):
    assert os.path.exists(os.path.join(ROOT, path))


# ---------- 数据文件 ----------
@pytest.mark.parametrize("data_file", [
    "data/raw/dlt_history.csv",
    "data/raw/dlt_2024_sample.csv",
    "data/raw/ssq_2024_sample.csv",
])
def test_data_files_exist(data_file):
    p = os.path.join(ROOT, data_file)
    assert os.path.exists(p)


@pytest.mark.parametrize("min_expected", [500, 450, 400])
def test_dlt_history_enough_rows(min_expected):
    p = os.path.join(ROOT, "data/raw/dlt_history.csv")
    rows = [l for l in _read(p).splitlines() if l.strip()]
    assert len(rows) - 1 >= min_expected  # 减表头


@pytest.mark.parametrize("col", ["issue", "date", "numbers", "pool"])
def test_dlt_history_header(col):
    p = os.path.join(ROOT, "data/raw/dlt_history.csv")
    header = _read(p).splitlines()[0]
    assert col in header


# ---------- 文档交付 ----------
@pytest.mark.parametrize("doc", [
    "docs/audit/Atlas_Module_Usage_Report.md",
])
def test_audit_docs(doc):
    assert os.path.exists(os.path.join(ROOT, doc))


# ---------- 治理文件 ----------
@pytest.mark.parametrize("gov", ["LICENSE", "README.md", "CHANGELOG.md", "CONTRIBUTING.md"])
def test_governance_files(gov):
    assert os.path.exists(os.path.join(ROOT, gov))
