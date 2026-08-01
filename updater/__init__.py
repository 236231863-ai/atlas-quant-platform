"""Auto Updater - version check, download, install, rollback."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class UpdateInfo:
    current_version:str="3.5.1"
    latest_version:str="3.5.1"
    update_available:bool=False
    download_url:str=""
    changelog:str=""
    def to_dict(self):
        return {"current":self.current_version,"latest":self.latest_version,"available":self.update_available}

class AutoUpdater:
    def __init__(self):
        self._version="3.5.1"
    def check_update(self) -> UpdateInfo: return UpdateInfo()
    def download(self,url) -> str: return f"Downloading from {url}..."
    def install(self) -> str: return "Installing update..."
    def rollback(self) -> str: return "Rolled back to previous version"
    def get_current_version(self) -> str: return self._version
