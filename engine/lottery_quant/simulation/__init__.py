"""simulation - 蒙特卡洛模拟（v3.9.0 Phase 3）。

随机生成开奖，模拟用户投注组合的中奖覆盖情况。

重要：模拟结果不代表未来。开奖结果具有随机性。
"""
from .monte_carlo import SimulationEngine, SimulationReport, simulate_coverage

__all__ = ["SimulationEngine", "SimulationReport", "simulate_coverage"]
