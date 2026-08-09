# Atlas v4.9.1 — Mobile MVP 留存报告（Retention Report）

> 状态：✅ 留存采集能力就绪 · ⏳ 真实数据待采集
> 核心：Mobile MVP 的留存分析管道已完全打通，等待 50 名真实用户 14 天数据

---

## 一、留存模型（Mobile MVP）

```
首次进入（app_install / mobile_opened）
   ↓
录第一张票（mobile_ticket_saved）        ← 建档
   ↓
开启提醒（mobile_reminder_enabled）      ← 留存钩子 1
   ↓
开奖日推送（reminder_sent）
   ↓
打开查看（mobile_draw_viewed）           ← 留存钩子 2（每周 6 次机会）
   ↓
本月统计（asset_viewed）                 ← 周/月回访
   ↓
D1 / D3 / D7 / WALU
```

---

## 二、留存指标定义与目标

| 指标 | 定义 | 目标 | 数据来源 |
|------|------|-----:|---------|
| 首次保存率 | first_ticket_saved / registered | **≥50%** | users 表 |
| 提醒开启率 | reminder_enabled / registered | **≥50%** | users 表 |
| D1 留存 | 第 1 天活跃 / 首日用户 | **≥40%** | behavior_events |
| D7 留存 | 第 7 天活跃 / 首日用户 | **≥30%** | behavior_events |
| 提醒点击率 | reminder_clicked / reminder_sent | **≥30%** | reminders 表 |
| WALU | 本周有彩票行为的用户数 | 记录 | behavior_events |
| Q2 不可替代 | 问卷选 A/B/C 比例 | **≥60%** | 反馈问卷 |

---

## 三、留存计算能力（已就绪）

| 能力 | 实现 | 说明 |
|------|------|------|
| 用户里程碑 | users 表 5 个行为字段 | first_ticket_saved_at 等 |
| 事件漏斗 | service.funnel() | registered → saved → reminder → draw |
| 留存曲线 | engine/user_experiment/retention.py | D1/D3/D7（REAL+MOBILE 口径） |
| 提醒价值 | ReminderRepository.click_rate() | clicked/sent |
| 每日记录 | DailyExperimentLog | 10 字段逐日累加 |
| 来源隔离 | is_real_source() | MOBILE 计入真实，SIM 排除 |

---

## 四、当前留存数据（诚实声明）

| 指标 | 当前值 | 说明 |
|------|-------:|------|
| 真实用户 | **0** | 验证版刚就绪，尚未分发 |
| 首次保存率 / D1 / D7 / Q2 | 无法计算 | 需真实数据 |

> ⚠️ **没有任何模拟留存数据冒充真实结果。** 本次交付的是「能算出这些指标的管道」，不是「指标结果」。

---

## 五、留存风险预判（基于设计，非数据）

| 风险 | 预判 | 应对 |
|------|------|------|
| 用户只录票不开提醒 | 提醒开启率 <50% | 录票成功页强引导开启 |
| 开奖日不回来 | D7 <30% | 推送时机优化（开奖前 24h/3h） |
| 微信可替代 | Q2 <60% | 若 Q2<60% → 停止扩展（判断标准） |
| 录票太麻烦 | 保存率 <50% | 录票页简化 + 连续格式支持 |

---

## 六、决策门槛

| 结果 | 结论 | 动作 |
|------|------|------|
| 保存率≥50% + D7≥30% + Q2≥60% | 需求成立 | 进入小程序增强 + 云账户 |
| 任一核心指标未达标 | 需求不成立 | 停止扩展，回归桌面 |

---

## 七、下一步

- 部署后端 + 注册小程序（A 审核通过后）
- 50 人分发，14 天采集
- T+7 中期判断，T+13 数据封板，T+14 生成最终留存报告
