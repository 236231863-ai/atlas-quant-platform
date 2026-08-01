"""Installer - cross-platform installation wizard."""
from __future__ import annotations
from dataclasses import dataclass, field

INSTALL_STEPS = ["welcome","license","location","components","shortcuts","install","complete"]
@dataclass
class InstallConfig:
    install_path:str="C:\Program Files\Atlas"
    create_desktop_icon:bool=True
    create_start_menu:bool=True; register_file_types:bool=True

class InstallerWizard:
    def __init__(self):
        self._step=0
        self._config=InstallConfig()
    def next(self) -> str:
        if self._step>=len(INSTALL_STEPS)-1: return INSTALL_STEPS[-1]
        s=INSTALL_STEPS[self._step]; self._step+=1; return s
    def get_progress(self) -> float: return self._step/len(INSTALL_STEPS)
    def install(self) -> str:
        return f"Installing to {self._config.install_path}..."
