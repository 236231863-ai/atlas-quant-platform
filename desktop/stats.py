"""
Atlas Quant Desktop - 统计计算模块

基于本地开奖数据计算频率、和值、跨度、奇偶、冷热号等指标。
"""
from collections import Counter
from typing import Dict, List, Tuple

from data_loader import DrawRecord

FRONT_RANGE = range(1, 36)  # 大乐透前区 1-35
BACK_RANGE = range(1, 13)   # 大乐透后区 1-12


def front_frequency(draws: List[DrawRecord]) -> Dict[int, int]:
    """前区号码出现频率（含 0 次号码）。"""
    c = Counter()
    for d in draws:
        c.update(d.front)
    return {n: c.get(n, 0) for n in FRONT_RANGE}


def back_frequency(draws: List[DrawRecord]) -> Dict[int, int]:
    """后区号码出现频率（含 0 次号码）。"""
    c = Counter()
    for d in draws:
        c.update(d.back)
    return {n: c.get(n, 0) for n in BACK_RANGE}


def front_sums(draws: List[DrawRecord]) -> List[int]:
    """每期前区和值。"""
    return [d.front_sum for d in draws]


def front_spans(draws: List[DrawRecord]) -> List[int]:
    """每期前区跨度（最大-最小）。"""
    return [d.front_span for d in draws]


def parity_stats(draws: List[DrawRecord]) -> Dict[str, int]:
    """前区奇偶总数。"""
    odd = sum(1 for d in draws for n in d.front if n % 2 == 1)
    even = sum(1 for d in draws for n in d.front if n % 2 == 0)
    return {"odd": odd, "even": even}


def hot_numbers(draws: List[DrawRecord], k: int = 8) -> List[Tuple[int, int]]:
    """前区热号 TopK：(号码, 次数)。"""
    freq = front_frequency(draws)
    return sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:k]


def cold_numbers(draws: List[DrawRecord], k: int = 8) -> List[Tuple[int, int]]:
    """前区冷号 TopK：(号码, 次数)。"""
    freq = front_frequency(draws)
    return sorted(freq.items(), key=lambda kv: kv[1])[:k]


def consecutive_pairs(draws: List[DrawRecord]) -> int:
    """前区连号对总数。"""
    pairs = 0
    for d in draws:
        s = sorted(set(d.front))
        for i in range(len(s) - 1):
            if s[i + 1] - s[i] == 1:
                pairs += 1
    return pairs


def avg_pool(draws: List[DrawRecord]) -> float:
    """平均奖池。"""
    return sum(d.pool for d in draws) / len(draws) if draws else 0.0


def recommendation(draws: List[DrawRecord], method: str = "hot") -> Dict[str, List[int]]:
    """根据策略生成一注号码建议。

    method: hot=热号 / cold=冷号 / balanced=奇偶均衡
    """
    if method == "hot":
        cand = [n for n, _ in hot_numbers(draws, 15)]
        back_cand = [n for n, _ in sorted(back_frequency(draws).items(), key=lambda kv: kv[1], reverse=True)[:8]]
    elif method == "cold":
        cand = [n for n, _ in cold_numbers(draws, 15)]
        back_cand = [n for n, _ in sorted(back_frequency(draws).items(), key=lambda kv: kv[1])[:8]]
    else:  # balanced
        cand = [n for n, _ in sorted(front_frequency(draws).items(), key=lambda kv: kv[1])[:15]]
        cand = sorted(cand, key=lambda n: n % 2)  # 奇偶穿插
        back_cand = [n for n in range(1, 13) if n % 2 == 1][:4] + [n for n in range(1, 13) if n % 2 == 0][:4]

    front = _pick_balanced(cand, 5)
    back = sorted(back_cand[:2])
    return {"front": front, "back": back}


def _pick_balanced(cand: List[int], k: int) -> List[int]:
    """从候选里挑 k 个，尽量保证奇偶均衡。"""
    cand = sorted(set(cand))
    odds = [n for n in cand if n % 2 == 1]
    evens = [n for n in cand if n % 2 == 0]
    picks: List[int] = []
    while len(picks) < k and (odds or evens):
        if len(picks) % 2 == 0 and odds:
            picks.append(odds.pop(0))
        elif evens:
            picks.append(evens.pop(0))
        elif odds:
            picks.append(odds.pop(0))
    return sorted(picks[:k])
