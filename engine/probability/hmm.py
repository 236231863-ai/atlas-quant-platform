"""Hidden Markov Model Engine for number state analysis."""
from __future__ import annotations
import math
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
from engine.probability.markov import NumberState

@dataclass
class HMMResult:
    number: int; hidden_states: List[NumberState]; transition_matrix: Dict[str, Dict[str, float]]
    emission_probs: Dict[str, float]; future_distribution: Dict[str, float]; state_confidence: float
    def to_dict(self):
        return asdict(self)

class HMMEngine:
    STATES = ["cold", "normal", "hot"]
    @staticmethod
    def analyze_number(number: int, observations: List[int], n_states: int = 3, max_iter: int = 100) -> HMMResult:
        e = {s: {s2: 0.0 for s2 in HMMEngine.STATES} for s in HMMEngine.STATES}
        if not observations or len(observations) < 3:
            return HMMResult(number=number,hidden_states=[],transition_matrix=e,
                emission_probs={"cold":0.33,"normal":0.34,"hot":0.33},
                future_distribution={"cold":0.33,"normal":0.34,"hot":0.33},state_confidence=0.0)
        total = len(observations)
        freq = Counter(observations)
        t1, t2 = total * 0.3, total * 0.6
        state_map = {}
        for n in set(observations):
            c = freq[n]
            if c <= t1: state_map[n] = NumberState.COLD
            elif c <= t2: state_map[n] = NumberState.NORMAL
            else: state_map[n] = NumberState.HOT
        hidden = [state_map.get(o, NumberState.NORMAL) for o in observations]
        tc = {s: {s2: 0 for s2 in HMMEngine.STATES} for s in HMMEngine.STATES}
        for i in range(len(hidden)-1): f,t=hidden[i].value,hidden[i+1].value; tc[f][t]+=1
        tm = {}
        for s in HMMEngine.STATES:
            rt = sum(tc[s].values()); tm[s] = {s2: round(tc[s][s2]/rt,4) if rt>0 else 0.0 for s2 in HMMEngine.STATES}
        em = {s: round(sum(1 for h in hidden if h.value==s)/total,4) for s in HMMEngine.STATES}
        fd = {}
        if hidden:
            lv = hidden[-1].value
            for s2 in HMMEngine.STATES: fd[s2] = round(tm.get(lv,{}).get(s2,0),4)
        return HMMResult(number=number,hidden_states=hidden,transition_matrix=tm,emission_probs=em,
            future_distribution=fd,state_confidence=round(max(em.values()) if em else 0,4))

    @staticmethod
    def analyze_batch(frequency_data: Dict[int, List[int]]) -> List[HMMResult]:
        return [HMMEngine.analyze_number(n, obs) for n, obs in frequency_data.items()]
