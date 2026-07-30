"""
Atlas Quant Platform - AI / LLM Adapters.

统一的LLM适配器接口，支持多种AI模型。
切换模型不需要修改业务代码。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class LLMMessage:
    """LLM消息"""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw: Optional[Dict[str, Any]] = None


class LLMAdapterABC(ABC):
    """LLM适配器抽象基类"""

    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """发送对话请求"""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        """流式对话请求"""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """返回模型名称"""
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        ...
