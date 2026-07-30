"""Application Launcher - main entry point."""
from __future__ import annotations
class ApplicationLauncher:
    MODES={"desktop":"Start desktop","web":"Start web","cli":"Start CLI","service":"Background service"}
    def __init__(self): self._mode="cli"
    def set_mode(self,m): 
        if m not in self.MODES: return False
        self._mode=m; return True
    def launch(self): return f"Atlas starting in {self._mode} mode"
