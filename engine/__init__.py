"""
Atlas Quant Platform - Engine Layer.

引擎是平台的核心。所有数学公式、统计计算、模拟推理都在此完成。

引擎原则:
1. 纯计算 - 不做IO、不直接访问数据库
2. 无状态 - 不保存状态，状态由上层管理
3. 可测试 - 每个模块可独立测试
4. 可组合 - 通过定义好的接口互相调用
5. 数据驱动 - 输入输出都是纯数据结构
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

import numpy as np
import pandas as pd


# ---- 引擎基类型 ----
EngineParams = Dict[str, Any]
"""引擎输入参数通用类型"""

EngineResult = Dict[str, Any]
"""引擎输出结果通用类型"""

DataFrame = pd.DataFrame
"""统一使用Pandas DataFrame作为表格数据载体"""

Series = pd.Series
"""统一使用Pandas Series作为序列数据载体"""


class EngineABC(Protocol):
    """引擎模块协议 - 所有引擎模块遵循此协议"""

    def calculate(self, data: DataFrame, params: EngineParams) -> EngineResult:
        """执行计算，无副作用。"""
        ...
