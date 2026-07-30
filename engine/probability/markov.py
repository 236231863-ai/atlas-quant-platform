import math
from collections import Counter
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

class NumberState(str, Enum):
    COLD = "cold"; NORMAL = "normal"; HOT = "hot"

@dataclass
class MarkovResult:
    number: int; states: List[NumberState]; transition_matrix: Dict[str, Dict[str, float]]
    current_state: NumberState; state_persistence: float
    hot_probability: float; normal_probability: float; cold_probability: float
    steady_state: Dict[str, float]
    def to_dict(self): return asdict(self)

class MarkovEngine:
    @staticmethod
    def analyze_number(number: int, draw_frequencies: List[float], hot_threshold: float = 0.6, cold_threshold: float = 0.3) -> MarkovResult:
        e = {"cold":{"cold":0.0,"normal":0.0,"hot":0.0},"normal":{"cold":0.0,"normal":0.0,"hot":0.0},"hot":{"cold":0.0,"normal":0.0,"hot":0.0}}
        if not draw_frequencies:
            return MarkovResult(number=number,states=[],transition_matrix=e,current_state=NumberState.NORMAL,
                state_persistence=0.0,hot_probability=0.0,normal_probability=0.0,cold_probability=0.0,steady_state={"cold":0.33,"normal":0.34,"hot":0.33})
        states = [NumberState.HOT if f >= hot_threshold else (NumberState.COLD if f <= cold_threshold else NumberState.NORMAL) for f in draw_frequencies]
        tc = {"cold":{"cold":0,"normal":0,"hot":0},"normal":{"cold":0,"normal":0,"hot":0},"hot":{"cold":0,"normal":0,"hot":0}}
        for i in range(len(states) - 1):
            f, t = states[i].value, states[i+1].value; tc[f][t] += 1
        tm = {}
        for s in ["cold","normal","hot"]:
            rt = sum(tc[s].values()); tm[s] = {t2: round(tc[s][t2]/rt,4) if rt>0 else 0.0 for t2 in ["cold","normal","hot"]}
        cs = states[-1] if states else NumberState.NORMAL
        pers = round(sum(tm[s][s] for s in ["cold","normal","hot"] if s in tm and s in tm[s]) / 3, 4)
        sc = Counter(states); t = len(states) or 1
        hp = round(sc.get(NumberState.HOT,0)/t,4); np = round(sc.get(NumberState.NORMAL,0)/t,4); cp = round(sc.get(NumberState.COLD,0)/t,4)
        ss = {"cold":1/3,"normal":1/3,"hot":1/3}
        for _ in range(100):
            nd = {"cold":0.0,"normal":0.0,"hot":0.0}
            for f2 in ["cold","normal","hot"]:
                for t2 in ["cold","normal","hot"]:
                    nd[t2] += ss[f2] * tm.get(f2,{}).get(t2,0)
            st = sum(nd.values())
            if st>0: ss = {s2: round(nd[s2]/st,4) for s2 in ["cold","normal","hot"]}
        return MarkovResult(number=number,states=states,transition_matrix=tm,current_state=cs,
            state_persistence=pers,hot_probability=hp,normal_probability=np,cold_probability=cp,steady_state=ss)

    @staticmethod
    def analyze_batch(frequency_history: Dict[int, List[float]], hot_threshold: float = 0.6, cold_threshold: float = 0.3) -> List[MarkovResult]:
        return [MarkovEngine.analyze_number(n, f, hot_threshold, cold_threshold) for n, f in frequency_history.items()]
