"""Copy project to D drive, rebuild Atlas.exe, create shortcut, and launch."""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys


SRC = pathlib.Path(r"C:\Users\Administrator\Documents\Codex\2026-07-28\lqrp-v0-1-v0-2-v0\AtlasQuant")
DST = pathlib.Path(r"D:\Atlas Quant Platform")
PY = str(SRC / ".venv" / "Scripts" / "python.exe")
DESKTOP = pathlib.Path(os.environ["USERPROFILE"]) / "Desktop"
MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"

SKIP = {".venv", ".git", "build", "dist", "__pycache__", "node_modules", ".pytest_cache", ".mypy_cache"}


def copy_project() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir(parents=True)

    def _copy(src_dir: pathlib.Path, dst_dir: pathlib.Path) -> None:
        for item in src_dir.iterdir():
            if item.name in SKIP:
                continue
            target = dst_dir / item.name
            try:
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    _copy(item, target)
                else:
                    shutil.copy2(item, target)
            except PermissionError:
                print("skip locked:", item, flush=True)
            except OSError as exc:
                print("skip:", item, exc, flush=True)

    _copy(SRC, DST)
    print("COPY OK ->", DST, flush=True)


def rebuild() -> None:
    code = subprocess.run(
        [PY, "-m", "pip", "install", "-i", MIRROR, "PySide6", "PyInstaller", "-q"],
        timeout=900,
    ).returncode
    if code != 0:
        print("pip install failed", flush=True)
        return
    code = subprocess.run(
        [
            PY,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--name",
            "Atlas",
            str(DST / "desktop" / "main.py"),
        ],
        cwd=str(DST),
        timeout=1200,
    ).returncode
    exe = DST / "dist" / "Atlas.exe"
    print("REBUILD exit:", code, "exe:", exe.exists(), flush=True)
    if not exe.exists():
        print("REBUILD FAILED", flush=True)
        sys.exit(1)


def shortcut_and_launch() -> None:
    exe = DST / "dist" / "Atlas.exe"
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{DESKTOP}\\Atlas Quant Platform.lnk'); "
        f"$s.TargetPath = '{exe}'; "
        f"$s.WorkingDirectory = '{exe.parent}'; "
        "$s.Description = 'Atlas Quant Platform v3.5.2'; "
        "$s.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=60)
    print("Shortcut exists:", (DESKTOP / "Atlas Quant Platform.lnk").exists(), flush=True)
    subprocess.Popen([str(exe)])
    print("LAUNCHED", flush=True)


if __name__ == "__main__":
    copy_project()
    rebuild()
    shortcut_and_launch()
    print("ALL DONE", flush=True)
