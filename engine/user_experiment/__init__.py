"""user_experiment - 用户实验系统（v4.9 P1 → v4.9.1 P1 扩展）。

验证 Sprint 基础设施：实验事件追踪（experiment_id）、用户漏斗、
留存曲线、Q1-Q4 验证指标、真实数据模拟环境、种子用户编号体系、
每日实验记录、提醒价值统计、4 问反馈问卷。

用途边界：模拟器输出合成数据，用于验证实验管道与建立基准预期，
不能替代真实用户数据。REAL / SIMULATION 严格隔离。
"""
from engine.user_experiment.events import (
    EXPERIMENT_EVENTS,
    MILESTONES,
    SOURCE_REAL,
    SOURCE_SIMULATION,
    SOURCE_MOBILE,
    ExperimentEvent,
    ExperimentTracker,
    is_real_source,
    normalize_source,
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
from engine.user_experiment.feedback import (
    INDISPENSABLE_REASONS,
    PAY_LEVELS,
    Q1_REASONS,
    Q3_UNINSTALL_REASONS,
    UNINSTALL_REASONS,
    USE_REASONS,
    UserFeedback,
    UserFeedbackSurvey,
)
from engine.user_experiment.simulator import (
    SimConfig,
    SimUser,
    UserBehaviorSimulator,
)
from engine.user_experiment.registry import (
    LOTTERY_TYPES,
    PURCHASE_FREQUENCIES,
    ExperimentUser,
    UserRegistry,
)
from engine.user_experiment.daily_log import (
    DAILY_LOG_FIELDS,
    DailyExperimentLog,
    DailyLogEntry,
)
from engine.user_experiment.reminder_value import (
    ReminderEvent,
    ReminderValueTracker,
)

__all__ = [
    "EXPERIMENT_EVENTS", "MILESTONES",
    "SOURCE_REAL", "SOURCE_SIMULATION", "SOURCE_MOBILE",
    "is_real_source", "normalize_source",
    "ExperimentEvent", "ExperimentTracker",
    "ExperimentFunnel", "ExperimentFunnelReport", "build_funnel",
    "ExperimentRetention", "ExperimentRetentionBuilder", "build_retention",
    "ValidationMetric", "ValidationMetrics", "ValidationMetricsBuilder",
    "build_metrics", "SimConfig", "SimUser", "UserBehaviorSimulator",
    "USE_REASONS", "UNINSTALL_REASONS", "INDISPENSABLE_REASONS",
    "PAY_LEVELS", "Q1_REASONS", "Q3_UNINSTALL_REASONS",
    "UserFeedback", "UserFeedbackSurvey",
    "LOTTERY_TYPES", "PURCHASE_FREQUENCIES",
    "ExperimentUser", "UserRegistry",
    "DAILY_LOG_FIELDS", "DailyExperimentLog", "DailyLogEntry",
    "ReminderEvent", "ReminderValueTracker",
]
