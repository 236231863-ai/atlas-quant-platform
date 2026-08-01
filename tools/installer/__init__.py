"""Installer - guided installation."""
from __future__ import annotations
from dataclasses import dataclass, field
STEPS=["welcome","license","deps","database","admin","config","done"]
@dataclass
class InstallState:
    current_step:int=0
    completed:bool=False
    errors:List[str]=field(default_factory=list)
from typing import List
@dataclass
class Installer:
    state:InstallState=field(default_factory=InstallState)
    def next_step(self):
        if self.state.current_step>=len(STEPS)-1: self.state.completed=True; return STEPS[-1]
        s=STEPS[self.state.current_step]; self.state.current_step+=1; return s
    def get_progress(self):
        return self.state.current_step/len(STEPS)
    def is_completed(self):
        return self.state.completed
