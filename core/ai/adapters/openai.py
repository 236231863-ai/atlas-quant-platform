"""OpenAI compatible LLM adapter."""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from core.ai.adapters import LLMAdapterABC, LLMMessage, LLMResponse

class OpenAIAdapter(LLMAdapterABC):
    def __init__(self, api_key: str = "", model: str = "gpt-4", base_url: Optional[str] = None):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url or "https://api.openai.com/v1"
    @property
    def model_name(self) -> str: return self._model
    @property
    def is_available(self) -> bool: return bool(self._api_key)
    async def chat(self, messages: List[LLMMessage], temperature: float = 0.7, max_tokens: int = 4096) -> LLMResponse:
        if not self._api_key: return LLMResponse(content="API key not configured", model=self._model)
        return LLMResponse(content="OpenAI response simulated (API call skipped in this environment)", model=self._model,
            usage={"prompt_tokens":0,"completion_tokens":0,"total_tokens":0})
    async def chat_stream(self, messages: List[LLMMessage], temperature: float = 0.7, max_tokens: int = 4096):
        yield LLMResponse(content="", model=self._model)
