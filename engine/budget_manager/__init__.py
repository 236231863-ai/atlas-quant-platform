"""budget_manager - 个人资金管理（v4.0.0 Phase 2）。

BudgetPlanner：管理月/年度预算，评估实际投入，超额提醒。
输出 BudgetHealthReport。

声明：预算管理帮助用户控制购彩支出，不涉及预测。
"""
from .budget import BudgetPlanner, BudgetHealthReport, BudgetSettings

__all__ = ["BudgetPlanner", "BudgetHealthReport", "BudgetSettings"]
