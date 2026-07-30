"""Desktop Packaging - PyInstaller configuration."""
from __future__ import annotations
class DesktopPackager:
    def __init__(self): self._config={}
    def configure(self,name,ver,entry):
        self._config={"app_name":name,"version":ver,"entry_point":entry,"one_file":True,"windowed":True}
        return self._config
    def get_config(self): return self._config
