"""Tests for MockLLMAdapter."""
from __future__ import annotations
import pytest
from core.ai.adapters.mock import MockLLMAdapter
from core.ai.adapters import LLMMessage

class TestMockLLM:
    @pytest.mark.asyncio
    async def test_chat_returns_response(self):
        llm = MockLLMAdapter()
        r = await llm.chat([LLMMessage(role="user", content="hello")])
        assert r.content == "This is a mock LLM response for testing purposes."

    @pytest.mark.asyncio
    async def test_model_name(self):
        llm = MockLLMAdapter()
        assert llm.model_name == "mock-model"

    def test_is_available(self):
        llm = MockLLMAdapter()
        assert llm.is_available

    @pytest.mark.asyncio
    async def test_call_count(self):
        llm = MockLLMAdapter()
        assert llm.call_count == 0
        await llm.chat([LLMMessage(role="user", content="hi")])
        assert llm.call_count == 1

    @pytest.mark.asyncio
    async def test_custom_responses(self):
        llm = MockLLMAdapter({"performance": "Strategy performed well."})
        r = await llm.chat([LLMMessage(role="user", content="analysis: performance review")])
        assert r.content == "Strategy performed well."

    @pytest.mark.asyncio
    async def test_tracks_last_messages(self):
        llm = MockLLMAdapter()
        msgs = [LLMMessage(role="user", content="hello")]
        await llm.chat(msgs)
        assert llm.last_messages is not None
        assert llm.last_messages[0].content == "hello"

    @pytest.mark.asyncio
    async def test_usage_stats(self):
        llm = MockLLMAdapter()
        r = await llm.chat([LLMMessage(role="user", content="hello")])
        assert r.usage["total_tokens"] == 20

    @pytest.mark.asyncio
    async def test_chat_stream(self):
        llm = MockLLMAdapter()
        async for chunk in llm.chat_stream([LLMMessage(role="user", content="hello")]):
            assert chunk.content == "Mock stream response"
            break

    @pytest.mark.asyncio
    async def test_default_on_unmatched(self):
        llm = MockLLMAdapter({"specific": "matched"})
        r = await llm.chat([LLMMessage(role="user", content="something else")])
        assert "mock" in r.content.lower()
    async def test_aa_temperature_passed(self):
        llm = MockLLMAdapter(); await llm.chat([LLMMessage(role="user",content="hi")], temperature=0.5)
        assert llm.call_count == 1
    async def test_ab_max_tokens_passed(self):
        llm = MockLLMAdapter(); await llm.chat([LLMMessage(role="user",content="hi")], max_tokens=100)
        assert llm.call_count == 1
    async def test_ac_response_always_string(self):
        llm = MockLLMAdapter(); r = await llm.chat([LLMMessage(role="user",content="x")])
        assert isinstance(r.content, str)
    async def test_ad_model_always_mock(self):
        llm = MockLLMAdapter(); r = await llm.chat([LLMMessage(role="user",content="x")])
        assert r.model == "mock"
    async def test_ae_empty_messages(self):
        llm = MockLLMAdapter(); r = await llm.chat([])
        assert r.content != ""
    async def test_af_system_message_handled(self):
        llm = MockLLMAdapter()
        r = await llm.chat([LLMMessage(role="system",content="be helpful"),LLMMessage(role="user",content="hi")])
        assert r.content != ""
