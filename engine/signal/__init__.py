"""Real Time Signal Engine - convert world information into research signals."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class ResearchSignal:
    signal_id:str
    signal_type:str
    description:str
    confidence:float=0.5
    severity:str="info"
    source:str=""
    def to_dict(self):
        return asdict(self)

SIGNAL_TYPES = {"trend":"Trend Signal","risk":"Risk Signal","opportunity":"Opportunity Signal","anomaly":"Anomaly Signal"}

class SignalGenerator:
    def __init__(self):
        self._signals: List[ResearchSignal] = []
    def generate(self, signal: ResearchSignal):
        self._signals.append(signal)
        return signal
    def get_signals(self, signal_type: Optional[str]=None) -> List[ResearchSignal]:
        if signal_type: return [s for s in self._signals if s.signal_type == signal_type]
        return self._signals
    def get_high_confidence(self, threshold: float=0.7) -> List[ResearchSignal]:
        return [s for s in self._signals if s.confidence >= threshold]
    def count(self) -> int: return len(self._signals)
