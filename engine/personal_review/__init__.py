"""personal_review - 历史投注复盘（v4.0.0 Phase 3）。

PersonalReviewEngine：读取 ticket_system 历史票据，分析
购买趋势 / 中奖情况 / 奖金累计 / 投入收益比 / 最高投入周期，
输出个人复盘报告。

声明：复盘中奖数据基于历史开奖，不能预测未来。
"""
from .review import PersonalReviewEngine, PersonalReviewReport, review_tickets

__all__ = ["PersonalReviewEngine", "PersonalReviewReport", "review_tickets"]
