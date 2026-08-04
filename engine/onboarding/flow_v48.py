"""onboarding.flow_v48 - 新用户引导系统（v4.8 P3）。

首次打开不展示研究数据，展示价值三步：
  1. 建立我的彩票档案
  2. 看看我的购彩情况
  3. 开启开奖提醒

记录 onboarding_start / onboarding_complete / onboarding_drop。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

STEPS = (
    ("build_profile", "建立我的彩票档案", "导入或添加你的彩票，Atlas 帮你管理"),
    ("view_behavior", "看看我的购彩情况", "投入/中奖/健康分，看懂你的行为"),
    ("enable_reminder", "开启开奖提醒", "开奖自动提醒，不再错过"),
)


@dataclass
class OnboardingFlow:
    """新用户引导流程状态。"""

    current_step: int = 0
    completed: bool = False
    events: List[str] = field(default_factory=list)

    @property
    def step(self) -> dict:
        name, title, desc = STEPS[self.current_step]
        return {"name": name, "title": title, "desc": desc,
                "index": self.current_step, "total": len(STEPS)}

    def next(self) -> dict:
        if self.current_step < len(STEPS) - 1:
            self.current_step += 1
        return self.step

    def finish(self) -> bool:
        """完成引导（记录 onboarding_complete）。"""
        self.completed = True
        self._record("onboarding_complete")
        return True

    def drop(self) -> None:
        """中途退出（记录 onboarding_drop）。"""
        self._record("onboarding_drop")

    def _record(self, event: str) -> None:
        from engine.user_analytics import AnalyticsTracker
        try:
            AnalyticsTracker().record(event, source="onboarding")
        except Exception:
            pass
        self.events.append(event)


def start_onboarding() -> OnboardingFlow:
    """开始引导（记录 onboarding_start）。"""
    flow = OnboardingFlow()
    flow._record("onboarding_start")
    return flow
