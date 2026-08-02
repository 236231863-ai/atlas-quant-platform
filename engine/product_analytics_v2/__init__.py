"""product_analytics_v2 - 产品数据分析（v3.7.1 Phase 2）。

标准事件：app_open/analysis_start/analysis_complete/report_export/backtest_run/strategy_view/app_close
输出：ProductUsageReport
"""
from .analytics import ProductAnalytics, ProductUsageReport, build_usage_report, EVENTS

__all__ = ["ProductAnalytics", "ProductUsageReport", "build_usage_report", "EVENTS"]
