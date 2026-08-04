# Atlas v4.8 Phase 2 Product Review：彩票票面 OCR 识别

> 2026-08-05

## 产品目标

识别彩票照片提取彩种/号码/日期/金额。**OCR 错误必须允许人工确认**，禁止自动无确认写入。

## 交付

| 模块 | 功能 |
|------|------|
| `engine/ticket_ocr/ocr.py` | TicketOCREngine：OCR 文本解析 + 日期/金额提取 + confirm 确认流程 + save_confirmed（仅确认后保存） |

## 流程

```
图片 → OCR 文本 → parse_ocr_text（待确认）→ 人工确认/编辑 → save_confirmed
```

- 未确认 → 拒绝保存（`needs_confirmation`）
- 人工可编辑号码/日期/金额后确认

## 测试

- tests/v480/test_ocr_v480.py：37 场景（解析/日期金额/确认流程/未确认拒绝/矩阵）

## 用户价值

用户拍张彩票照片即可建档（OCR 结果可人工校正），5 分钟建档的关键入口。

**P2 通过，进入 P3。**
