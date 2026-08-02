"""beta - Beta 用户管理（v3.7.1 Phase 1）。

BetaUserManager：用户编号/批次/版本/反馈状态 + BetaUserReport。
"""
from .manager import BetaUserManager, BetaUser, BATCHES, FEEDBACK_STATUSES

__all__ = ["BetaUserManager", "BetaUser", "BATCHES", "FEEDBACK_STATUSES"]
