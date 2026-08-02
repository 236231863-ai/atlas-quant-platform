"""report - 量化报告生成（v3.9.0 Phase 8）。

生成 Lottery Quant Report，支持 Markdown / PDF / PNG 导出。
所有报告必须包含免责声明：本报告基于历史统计，不能预测未来开奖。
"""
from .generator import QuantReportGenerator, generate_quant_report

__all__ = ["QuantReportGenerator", "generate_quant_report"]
