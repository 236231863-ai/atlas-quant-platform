# Atlas v4.3 架构报告（Architecture Report）

版本：v4.3.0 · 2026-08-03

## 新增模块（全部有桌面入口）

| 模块 | 职责 | 桌面入口 | 复用 |
|------|------|---------|------|
| `engine/user_events/` | 用户行为事件追踪（jsonl） | main_window 启动 / dashboard | — |
| `engine/claim_center/` | 自动兑奖中心（4 状态机） | 首页待兑奖列表 + 启动自动兑奖 | AutoReviewEngine / DrawResultMatcher / PrizeCalculator |
| `engine/asset_center/` | 彩票资产中心（风险 + 年度） | 个人中心资产区块 | user_archive / PrizeCalculator |
| `engine/growth_system/` | 用户成长系统（连续周 + 等级） | 个人中心成长区块 | user_events |

## 数据流

```
TicketManager(保存) → user_events.record(ticket_saved)
开奖日 → reminder_center(桌面通知) → user_events.record(reminder_shown)
开奖后 → claim_center.auto_claim(自动匹配) → notify + record(auto_claim_run)
个人中心 → asset_center + growth_system(读事件+票据) → 报告
```

## 关键修复

| 缺陷 | 修复 |
|------|------|
| `TicketRecord` 无 `claimed` 字段 → 重启丢失兑奖状态 | 新增 `claimed: bool = False`（持久化） |
| 资产中心活跃月 `[:7]` 切片优先级 bug | 括号修正 |
| 首页研究指标（平均和值/奇偶/冷热）在首屏 | 移至「数据分析」页，首页只留 3 秒价值 |

## 架构原则

- **验收 = 用户行为发生**：关键步骤全部记录事件（可查、可统计）
- **禁止孤立模块**：全部新模块被桌面直接引用
- **优先复用**：claim_center 复用 AutoReviewEngine，asset_center 复用 user_archive

## 依赖

- 无新外部依赖
- spec hiddenimports 追加 v4.3 四模块
