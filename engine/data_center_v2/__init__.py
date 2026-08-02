"""data_center_v2 - 数据真实性升级（v3.6.1 Phase 1）。

多数据源管理 + 数据质量报告：
  - DataSourceManager : CSV / Excel / API / Database 统一接入
  - DataQualityReport : 数据数量 / 时间范围 / 完整率 / 可信等级
  - DrawRecord        : 统一数据模型

用法:
    mgr = DataSourceManager.from_project("dlt")
    draws = mgr.load()
    print(mgr.quality().trust_label)   # 可信 / 基本可用 / 数据不足
"""
from .models import DrawRecord, DataSourceInfo, LOTTERY_SPECS, lottery_name
from .quality import DataQualityReport, TRUST_THRESHOLDS
from .sources import (
    DataSourceManager,
    CSVDatasource,
    ExcelDatasource,
    APIDatasource,
    DatabaseDatasource,
)

__all__ = [
    "DrawRecord",
    "DataSourceInfo",
    "DataSourceManager",
    "DataQualityReport",
    "CSVDatasource",
    "ExcelDatasource",
    "APIDatasource",
    "DatabaseDatasource",
    "LOTTERY_SPECS",
    "lottery_name",
    "TRUST_THRESHOLDS",
]
