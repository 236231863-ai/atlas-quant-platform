# Atlas 反馈流程（Feedback Process）

> 定义用户反馈从提交到关闭的完整闭环。

---

## 1. 反馈类型

| 类型 | 说明 | 优先级 |
|------|------|--------|
| BugReport | 功能异常/崩溃 | 高 |
| FeatureRequest | 功能建议 | 中 |
| Rating | 评分（1-5） | 参考 |
| Feedback | 一般反馈 | 中 |

## 2. 反馈状态机

```
New → Reviewing → Fixed → Closed
      ↘ Rejected → Closed
```

| 状态 | 说明 |
|------|------|
| New | 已提交，待处理 |
| Reviewing | 团队评估中 |
| Fixed | 已修复（等待用户确认） |
| Closed | 已关闭（确认或拒绝） |

## 3. 处理时限

| 优先级 | New → Reviewing | Reviewing → Fixed |
|--------|-----------------|-------------------|
| 高（Bug） | ≤24h | ≤72h |
| 中（建议） | ≤72h | ≤1 周 |

## 4. 提交渠道

- 软件内「帮助中心」反馈表单（自动带版本/系统信息）。
- 邮件模板：主题 `[Atlas Beta] 反馈-类型`，内容含复现步骤。

## 5. 数据闭环

反馈数据（backend/feedback）→ 每周汇总 → 纳入产品迭代（v3.7.x）。
用户行为数据（product_analytics_v2）→ 观察功能使用 → 指导优化。
