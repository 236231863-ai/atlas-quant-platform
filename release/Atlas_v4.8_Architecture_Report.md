# Atlas v4.8 架构报告（Architecture Report）

版本：v4.8.0 · 2026-08-05

## 新增模块

| 模块 | 职责 | 复用 |
|------|------|------|
| `engine/import_center/imports.py` | TextImporter/CSVImporter/HistoricalImporter + ImportReport | ticket_system + TicketParser |
| `engine/ticket_ocr/ocr.py` | TicketOCREngine（解析 + 人工确认流程） | ticket_system |
| `engine/onboarding/flow_v48.py` | OnboardingFlow（三步引导 + 事件） | user_analytics |
| `engine/profile_card/card.py` | ProfileCardBuilder（档案卡） | PrizeCalculator |
| `engine/data_quality/quality.py` | DataQualityChecker（A/B/C） | — |

## 数据流（冷启动闭环）

```
新用户 → OnboardingFlow（建档案引导）
  → import_center（文本/CSV/OCR/手动）
    → ticket_system（存储）
      → profile_card（档案卡）
      → data_quality（可信等级）
      → behavior/asset（画像/盈亏）
      → AI import_analyze（问答）
```

## 关键设计

- **4 种导入方式**统一到 ticket_system（记录/管理/复盘核心）
- **OCR 人工确认**：未确认禁止保存（needs_confirmation）
- **数据质量**：5 类问题 → 可信等级 A/B/C
- **AI 建档**：import_analyze 工具（优先级：兑奖→导入→行为→资产→LLM）

## 修改文件

- `engine/assistant/registry.py`（import_analyze + 亏损→资产）
- `engine/user_analytics/analytics.py`（+onboarding 事件）
- `packaging/atlas_desktop.spec`（+9 模块）

## 测试数量

- tests/v480 新增 1035 场景

## 已知限制

- OCR 真实图片识别依赖外部引擎（当前文本解析）
- 双色球源不可用
