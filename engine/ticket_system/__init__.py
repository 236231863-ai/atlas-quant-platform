"""ticket_system - 彩票票据系统 v2（v3.8.0 P1）+ 日期升级。

票据保存/加载/列表/删除/筛选 + 日期意图解析 + 开奖日程。
"""
from .manager import TicketRecord, TicketManager
from .date_parser import DateIntentParser, DateIntent
from .schedule import LotterySchedule

__all__ = ["TicketRecord", "TicketManager", "DateIntentParser", "DateIntent", "LotterySchedule"]
