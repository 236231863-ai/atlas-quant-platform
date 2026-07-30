"""
Atlas Quant Platform - AI Services.

基于LLM适配器构建的AI服务。
包括分析辅助、报告生成、策略推荐等。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.ai.adapters import LLMAdapterABC, LLMMessage, LLMResponse


class AnalysisAssistant:
    """分析助手 - 根据用户自然语言需求执行分析"""

    def __init__(self, llm: LLMAdapterABC) -> None:
        self._llm = llm

    async def analyze(self, user_query: str, context: Dict[str, Any]) -> str:
        """根据用户查询和上下文，生成分析结果"""
        messages = [
            LLMMessage(
                role="system",
                content=(
                    "You are a quantitative analysis assistant. "
                    "You help users understand lottery data through statistical analysis. "
                    "Always note that past performance does not indicate future results."
                ),
            ),
            LLMMessage(
                role="user",
                content=f"Context: {context}\n\nUser query: {user_query}",
            ),
        ]
        response = await self._llm.chat(messages)
        return response.content

    async def generate_report(self, data: Dict[str, Any]) -> str:
        """基于结构化数据生成分析报告"""
        messages = [
            LLMMessage(
                role="system",
                content="Generate a comprehensive analysis report based on the data.",
            ),
            LLMMessage(role="user", content=str(data)),
        ]
        response = await self._llm.chat(messages)
        return response.content


class StrategyAdvisor:
    """策略顾问 - 基于历史数据推荐策略方向"""

    def __init__(self, llm: LLMAdapterABC) -> None:
        self._llm = llm

    async def recommend(
        self, analysis_results: Dict[str, Any], available_strategies: List[str]
    ) -> str:
        """推荐策略方向"""
        messages = [
            LLMMessage(
                role="system",
                content="Recommend research directions based on analysis results.",
            ),
            LLMMessage(
                role="user",
                content=f"Analysis: {analysis_results}\nStrategies: {available_strategies}",
            ),
        ]
        response = await self._llm.chat(messages)
        return response.content
