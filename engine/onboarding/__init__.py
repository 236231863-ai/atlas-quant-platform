"""onboarding - 首次成功体验（v3.7.0 Phase 1）。

FirstSuccessFlow：欢迎 → 数据介绍 → 自动生成报告 → 展示 → 保存历史。
UserAchievement：用户成就系统。
"""
from .flow import FirstSuccessFlow, default_report_generator, default_history_saver
from .achievements import UserAchievement, ACHIEVEMENTS

__all__ = [
    "FirstSuccessFlow",
    "default_report_generator",
    "default_history_saver",
    "UserAchievement",
    "ACHIEVEMENTS",
]
