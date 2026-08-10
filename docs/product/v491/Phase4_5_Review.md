# Atlas v4.9.1 — Phase 4.5 Product Review（部署验证）

> 阶段：Phase 4.5 部署验证 · 状态：✅ 全部交付完成 · 等待审核决策
> 原则：冻结功能开发，只做部署验证 / Bug 修复 / 数据链路修复

---

## 一、交付总览

| 任务 | 交付 | 状态 |
|------|------|------|
| ① 部署验证 | 后端 API 可访问 / 持久化 / 隔离 / 异常恢复 | ✅ 4 项全过 |
| ② 微信提醒真实验证 | 授权→提醒→发送→记录事件 全链路 + 验证报告 | ✅ |
| ③ 用户安全基础 | 首次使用协议页（定位/不预测/不保证中奖/自主购彩） | ✅ |
| ④ 真实测试准备 | Beta 测试计划（10人种子7天 + 50人正式14天） | ✅ |
| ⑤ 数据指标冻结 | 只采集 6 项冻结指标，其余拒绝 | ✅ |

---

## 二、详细验证结果

### ① 部署验证（4 项全过）
| 项 | 结果 |
|----|------|
| 后端 API 可访问 | ✅ funnel 接口 200 |
| 数据持久化 | ✅ 写入→新连接读取一致，DB 文件落盘 73KB |
| 用户数据隔离 | ✅ U0001 有票 / U0002 无票 |
| 异常恢复正常 | ✅ 非法号码 422 / 不存在票 404，服务仍 200 |

### ② 微信提醒真实验证（全链路）
```
用户授权(U0001) → 录票(T0001) → 生成提醒
→ dispatch 发送({sent:1,failed:0}) → 记录 reminder_sent 事件
→ 点击回执 → clicked=True → 点击率 1.0
```
**数据链路修复**：`ReminderDispatcher` 发送成功后补录 `reminder_sent` 事件（原缺失）。回归 34 passed。

### ③ 用户安全基础
协议页 `mobile_app/pages/terms/` 设为**启动首页**，含 4 条：
- 📒 彩票记录工具定位
- 🚫 不提供预测
- ⚖️ 不保证中奖（开奖随机，任何号码概率相同）
- 🧠 用户自主购彩（理性购彩，长期期望为负）
onboarding 增加协议守卫（未同意跳回协议页）。

### ④ Beta 测试计划
- **种子测试**：10 人 · 7 天 · 门槛=录票成功率≥80% + 无阻断 Bug
- **正式测试**：50 人 · 14 天 · T+7 D1/D7/Q2 · T+13 封板
- 部署清单 / 每日记录 / 红线 齐备

### ⑤ 数据指标冻结（只采集 6 项）
| 冻结指标 | 实际事件 | 验证 |
|---------|---------|:---:|
| install_completed | app_install | ✅ |
| mobile_opened | mobile_opened | ✅ |
| ticket_saved | mobile_ticket_saved | ✅ |
| reminder_enabled | mobile_reminder_enabled | ✅ |
| draw_viewed | mobile_draw_viewed | ✅ |
| feedback_submitted | mobile_feedback_submitted | ✅ |

非冻结指标（如 location_access）**拒绝采集** ✅

---

## 三、本轮代码改动（3 处数据链路/安全修复）

| 文件 | 改动 |
|------|------|
| `backend/mobile/wechat.py` | Dispatcher 发送成功记录 reminder_sent 事件 |
| `backend/mobile/service.py` | FROZEN_METRICS 6 项冻结清单 + track 映射 |
| `mobile_app/pages/terms/` + onboarding | 首次使用协议页 + 协议守卫 |

**无功能扩展**，符合 Phase 4.5「只允许部署验证 / Bug 修复 / 数据链路修复」。

---

## 四、测试

| 套件 | 结果 |
|------|------|
| test_reminder + test_service_flow | 34 passed（dispatcher 改动） |
| test_service_flow + test_reminder + test_api | 49 passed（track 改动） |
| 冻结指标验证 | 6 项可采集 + 1 项拒绝 ✅ |

---

## 五、诚实声明

- ✅ 微信提醒为 **mock 逻辑验证**；真实微信推送需注册小程序 + 配置模板（产品负责人部署步骤）
- ✅ 真实用户 = 0，留存/保存率等指标**待 Beta 测试采集**
- ✅ 未制造模拟用户数据

---

## 六、决策请求

> **A：通过** → 进入真实测试：产品负责人按 Beta 计划部署后端 + 小程序 + 10 人种子测试
> B：调整（部署 / 协议 / 指标）
> C：暂停（重新评估）

**在收到决策前，停止开发与部署，不进入下一阶段。**
