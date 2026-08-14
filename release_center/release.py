"""release_center - 发布中心。

提供：版本信息 / 更新说明 / 安装指南 / FAQ。
数据驱动（后续可接远程版本检查）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

CURRENT_VERSION = "v4.10.0"

# 版本历史
VERSIONS = {
    "v4.10.0": {
        "date": "2026-08-14",
        "summary": "量化模型升级：数据准确性审计 + 随机性检验 + 描述统计免责声明",
        "features": [
            "数据准确性全量审计（兑奖复核 + 数据源连续性）",
            "随机性检验引擎（卡方/游程/自相关）",
            "描述统计免责声明补齐",
            "版本号统一 v4.10",
        ],
    },
    "v3.7.1-beta": {
        "date": "2026-08-02",
        "summary": "Beta 发布：用户反馈 + 产品分析 + 版本中心",
        "features": [
            "Beta 用户系统",
            "产品使用分析",
            "用户反馈中心",
            "Release Center",
        ],
    },
    "v3.7.0": {
        "date": "2026-08-02",
        "summary": "用户验证与产品智能",
        "features": [
            "首次成功体验", "每日智能", "1200期大乐透数据",
            "用户行为追踪", "商业版本框架",
        ],
    },
    "v3.6.1": {
        "date": "2026-08-02",
        "summary": "产品信任升级",
        "features": ["520期真实数据", "诚实回测", "四格式导出", "稳定性"],
    },
}

# 更新说明（当前版本）
UPDATE_NOTES = [
    "【新增】随机性检验引擎：卡方/游程/自相关，用数学证明任何选号策略无统计优势",
    "【审计】兑奖金额与数据源连续性全量复核通过（60 张票 / 6 中奖全对）",
    "【合规】频次/遗漏/分布统计补齐「仅陈述历史，不构成选号依据」免责声明",
    "【优化】性能：事件/数据源缓存（看板刷新 20 秒 → 213 毫秒）",
    "【升级】版本号统一 v4.10.0",
]

# 安装指南
INSTALL_GUIDE = [
    "1. 下载 AtlasQuant-v4.10.0-Setup.exe（安装包）或 zip（便携版）",
    "2. 安装包：双击运行，按向导完成；便携版：解压后运行 Atlas.exe",
    "3. 若 SmartScreen 提示，点「更多信息」→「仍要运行」",
    "4. 首次启动完成三步引导，自动生成第一份报告",
]

# FAQ
FAQ: List[Dict[str, str]] = [
    {"q": "需要联网吗？", "a": "基础功能离线可用；在线 AI 需配置 API Key。"},
    {"q": "数据是真的吗？", "a": "大乐透 1205 期 + 双色球 500 期，来自官方开奖 API。"},
    {"q": "能导出报告吗？", "a": "报告支持 MD/PDF/CSV，回测支持 CSV/PDF/PNG。"},
    {"q": "回测结果可信吗？", "a": "包含样本外划分与随机基准对照，方法诚实。"},
    {"q": "如何反馈问题？", "a": "通过帮助中心提交，或发送邮件（附复现步骤）。"},
    {"q": "为什么提示数据不足？", "a": "数据量低于 500 期时会提示；导入更多数据即可。"},
]


@dataclass
class ReleaseCenter:
    """发布中心（本地静态数据 + 查询 API）。"""

    current_version: str = CURRENT_VERSION

    def version_info(self) -> dict:
        return {
            "current": self.current_version,
            "available": list(VERSIONS.keys()),
        }

    def release_notes(self, version: Optional[str] = None) -> dict:
        v = version or self.current_version
        return VERSIONS.get(v, {"date": "", "summary": "未知版本", "features": []})

    def update_notes(self) -> List[str]:
        return UPDATE_NOTES

    def install_guide(self) -> List[str]:
        return INSTALL_GUIDE

    def faq(self) -> List[Dict[str, str]]:
        return FAQ

    def faq_search(self, keyword: str) -> List[Dict[str, str]]:
        if not keyword:
            return []
        return [f for f in FAQ if keyword in f["q"] or keyword in f["a"]]

    def has_update(self, installed_version: str) -> bool:
        """当前版本是否比已安装版本新。"""
        return self._cmp(installed_version) > 0

    def _cmp(self, v: str) -> int:
        """粗略比较版本号：返回正数=当前更新，0=相同，负数=旧。"""
        if v == self.current_version:
            return 0
        return 1  # 简化：不同即视为可更新

    def summary(self) -> str:
        info = self.release_notes()
        return f"{self.current_version} ({info['date']})：{info['summary']}"
