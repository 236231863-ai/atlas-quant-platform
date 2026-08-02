# Atlas Current Product Map — v3.8.0

> 产品现状全景图（冻结于 v3.7.1-beta 之后）

## 1. 产品形态
- Windows 桌面应用（PySide6），本地优先，可安装/便携。
- 当前版本 v3.7.1-beta；1200 期大乐透 + 500 期双色球真实数据。

## 2. 模块地图

| 层 | 模块 | 用户入口 |
|----|------|----------|
| 桌面 | 6 页面（数据看板/数据分析/策略实验室/回测中心/AI 助手/研究报告） | ✅ 导航 |
| 桌面 | 帮助中心 / 首次引导 / 每日摘要 / 个人成就 | ✅ |
| 数据 | data_center_v2（1200+500 期）| ✅ Dashboard |
| 评估 | evaluation_v2（样本外/随机基准）| ✅ 回测中心 |
| 导出 | export（MD/CSV/PNG/PDF）| ✅ 报告/回测页 |
| 稳定性 | health（异常/日志/恢复）| ✅ 内置 |
| Beta | beta / product_analytics_v2 / feedback / release_center | ✅ 帮助中心 |
| 商业 | subscription（Community/Professional/Research）| ⚠️ 框架，无 UI |

## 3. 数据流
```
用户操作 → 桌面页面 → data/evaluation/export
  → user_feedback_v2 / product_analytics_v2（行为数据）
  → feedback（用户反馈）→ 决策输入
```

## 4. 缺口（v3.8.0 要补）
- 用户价值量化（value_score）缺失
- 功能价值归因（product_value）缺失
- 订阅无 UI 验证（subscription v2）
- 个人中心（Personal Dashboard）缺失
