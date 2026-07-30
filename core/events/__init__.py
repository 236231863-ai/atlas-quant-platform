"""
Atlas Quant Platform - Event Framework.

轻量级领域事件系统，用于模块间解耦通信。
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.types import Timestamp


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: Timestamp = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_type:
            self.event_type = self.__class__.__name__


# ---- 内置事件类型 ----
class DrawDataCollected(DomainEvent):
    """数据采集完成事件"""


class BacktestCompleted(DomainEvent):
    """回测完成事件"""


class StrategyCreated(DomainEvent):
    """策略创建事件"""


# ---- 事件处理器接口 ----
EventHandler = Callable[[DomainEvent], None]


class EventBus(ABC):
    """事件总线接口"""

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        ...

    @abstractmethod
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        ...

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        ...


class SimpleEventBus(EventBus):
    """内存实现的事件总线"""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}

    def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            handler(event)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
