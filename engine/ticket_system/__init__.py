"""ticket_system - 彩票票据系统 v2（v3.8.0 P1）。

票据保存/加载/列表/删除/筛选，支持从自然语言解析入库。
"""
from .manager import TicketRecord, TicketManager

__all__ = ["TicketRecord", "TicketManager"]
