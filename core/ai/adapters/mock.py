"""Mock LLM Adapter for testing."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.ai.adapters import LLMAdapterABC, LLMMessage, LLMResponse


class MockLLMAdapter(LLMAdapterABC):
    """Mock LLM adapter that returns deterministic responses.

    Used for testing intelligence modules without an actual LLM API call.
    """

    def __init__(self, responses: Optional[Dict[str, str]] = None) -> None:
        self._responses = responses or {}
        self._call_count = 0
        self._last_messages: Optional[List[LLMMessage]] = None

    @property
    def model_name(self) -> str:
        return "mock-model"

    @property
    def is_available(self) -> bool:
        return True

    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        self._call_count += 1
        self._last_messages = messages

        # Check for predefined responses
        last_content = messages[-1].content if messages else ""
        for key, response in self._responses.items():
            if key in last_content:
                return LLMResponse(content=response, model="mock")

        # Default response
        return LLMResponse(
            content="This is a mock LLM response for testing purposes.",
            model="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        )

    async def chat_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        yield LLMResponse(content="Mock stream response", model="mock")

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def last_messages(self) -> Optional[List[LLMMessage]]:
        return self._last_messages
