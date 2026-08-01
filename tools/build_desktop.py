"""Build Atlas desktop executable, create shortcut, and clean desktop."""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys


PROJ = pathlib.Path(r"C:\Users\Administrator\Documents\Codex\2026-07-28\lqrp-v0-1-v0-2-v0\AtlasQuant")
PY = str(PROJ / ".venv" / "Scripts" / "python.exe")
DESKTOP = pathlib.Path(os.environ["USERPROFILE"]) / "Desktop"
MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"


def run(cmd: list[str], timeout: int = 900) -> int:
    print("RUN:", " ".join(cmd)[:220], flush=True)
    return subprocess.run(cmd, timeout=timeout).returncode


def main() -> int:
    print("=== Step 1: install PySide6 + PyInstaller ===", flush=True)
    code = run(
        [PY, "-m", "pip", "install", "-i", MIRROR, "PySide6", "PyInstaller", "-q"],
        timeout=900,
    )
    if code != 0:
        print("pip install failed", flush=True)
        return 1

    print("=== Step 2: build Atlas.exe ===", flush=True)
    code = run(
        [
            PY,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--windowed",
            "--name",
            "Atlas",
            str(PROJ / "desktop" / "main.py"),
        ],
        timeout=1200,
    )
    exe = PROJ / "dist" / "Atlas.exe"
    if not exe.exists():
        print("BUILD FAILED: Atlas.exe not found", flush=True)
        return 1
    print(f"BUILD OK: {exe} ({exe.stat().st_size / 1024 / 1024:.1f} MB)", flush=True)

    print("=== Step 3: create desktop shortcut ===", flush=True)
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{DESKTOP}\\Atlas Quant Platform.lnk'); "
        f"$s.TargetPath = '{exe}'; "
        f"$s.WorkingDirectory = '{exe.parent}'; "
        "$s.Description = 'Atlas Quant Platform'; "
        "$s.Save()"
    )
    run(["powershell", "-NoProfile", "-Command", ps], timeout=60)
    lnk = DESKTOP / "Atlas Quant Platform.lnk"
    print(f"Shortcut exists: {lnk.exists()}", flush=True)

    print("=== Step 4: clean temp files from desktop ===", flush=True)
    temp_files = [
        "add_key.js",
        "authorize_github.js",
        "test_github_now.js",
        "github_now.png",
        "github_end.png",
        "github_ssh.png",
        "github_ssh_1.png",
        "github_ssh_2.png",
        "github_ssh_3.png",
        "github_ssh_4.png",
        "github_device_1.png",
        "github_device_2.png",
        "github_device_error.png",
        "github_result.png",
        "github_ssh_page.png",
        "github_keys_page.png",
    ]
    for name in temp_files:
        p = DESKTOP / name
        if p.exists():
            p.unlink()
            print("removed:", name, flush=True)

    print("=== Step 5: launch Atlas ===", flush=True)
    subprocess.Popen([str(exe)])
    print("LAUNCHED", flush=True)

    print("=== Desktop contents ===", flush=True)
    for p in sorted(DESKTOP.iterdir()):
        print(" -", p.name, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
