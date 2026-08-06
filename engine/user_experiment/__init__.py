"""user_experiment - 用户实验系统（v4.9 P1）。

验证 Sprint 基础设施：实验事件追踪（experiment_id）、用户漏斗、
留存曲线、Q1-Q4 验证指标、真实数据模拟环境（可导入/生成/查看）。

用途边界：模拟器输出合成数据，用于验证实验管道与建立基准预期，
不能替代真实用户数据。
"""
from engine.user_experiment.events import (
    EXPERIMENT_EVENTS,
    MILESTONES,
    ExperimentEvent,
    ExperimentTracker,
)
from engine.user_experiment.funnel import (
    ExperimentFunnel,
    ExperimentFunnelReport,
    build_funnel,
)
from engine.user_experiment.retention import (
    ExperimentRetention,
    ExperimentRetentionBuilder,
    build_retention,
)
from engine.user_experiment.metrics import (
    ValidationMetric,
    ValidationMetrics,
    ValidationMetricsBuilder,
    build_metrics,
)
from engine.user_experiment.simulator import (
    SimConfig,
    SimUser,
    UserBehaviorSimulator,
)

__all__ = [
    "EXPERIMENT_EVENTS", "MILESTONES", "ExperimentEvent", "ExperimentTracker",
    "ExperimentFunnel", "ExperimentFunnelReport", "build_funnel",
    "ExperimentRetention", "ExperimentRetentionBuilder", "build_retention",
    "ValidationMetric", "ValidationMetrics", "ValidationMetricsBuilder",
    "build_metrics", "SimConfig", "SimUser", "UserBehaviorSimulator",
]
