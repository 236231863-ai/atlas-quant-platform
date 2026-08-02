"""evaluation_v2 - 样本划分。

彩票数据严格有序（按时间），必须使用**时序划分**（不做随机 shuffle）：
  训练集 = 前 70% 期（用于观察/拟合策略）
  验证集 = 后 30% 期（样本外，检验策略泛化）
"""
from __future__ import annotations

from typing import List, Tuple, TypeVar

T = TypeVar("T")


def temporal_split(draws: List[T], train_ratio: float = 0.7) -> Tuple[List[T], List[T]]:
    """按时序切分数据为 (训练集, 验证集)。

    Args:
        draws: 按时间升序排列的数据列表。
        train_ratio: 训练集占比（默认 0.7）。

    Returns:
        (train, valid) 两个子列表，顺序保持原时序。
    """
    if train_ratio <= 0 or train_ratio >= 1:
        raise ValueError("train_ratio 必须在 (0, 1) 区间")
    n = len(draws)
    split_idx = int(n * train_ratio)
    return draws[:split_idx], draws[split_idx:]


def walk_forward_indexes(n: int, window: int = 3, step: int = 1) -> List[Tuple[int, int]]:
    """Walk-forward 索引对：每个 (hist_end, predict_idx)。

    Args:
        n: 数据总量
        window: 最少需要的历史期数（前 window 期用于生成推荐）
        step: 步长

    Returns:
        [(hist_end, predict_idx), ...] 列表，predict_idx 表示用 draws[:hist_end] 预测 draws[predict_idx]。
    """
    pairs = []
    for predict in range(window, n):
        pairs.append((predict, predict))
        if len(pairs) > n * 2:  # 防御
            break
    return pairs
