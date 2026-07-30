"""First Run Experience - guided onboarding wizard."""
from __future__ import annotations
from dataclasses import dataclass, field

FIRST_RUN_STEPS = ["welcome","language","theme","workspace","create_account","complete"]

@dataclass
class UserPreferences: language:str="zh-CN"; theme:str="light"; default_workspace:str="lottery"

class FirstRunWizard:
    def __init__(self): self._step=0; self._prefs=UserPreferences(); self._completed=False
    def current(self) -> str: return FIRST_RUN_STEPS[self._step] if self._step<len(FIRST_RUN_STEPS) else "done"
    def next(self):
        if self._step<len(FIRST_RUN_STEPS)-1: self._step+=1
        else: self._completed=True
    def is_completed(self): return self._completed
    def set_language(self,l): self._prefs.language=l
    def set_theme(self,t): self._prefs.theme=t
    def set_workspace(self,w): self._prefs.default_workspace=w
