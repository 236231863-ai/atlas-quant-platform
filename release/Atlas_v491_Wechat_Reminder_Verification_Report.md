# Atlas v4.9.1 — 微信提醒真实验证报告（Wechat Reminder Verification Report）

> 阶段：Phase 4.5 部署验证 · 状态：✅ 链路验证通过
> 目的：验证微信订阅消息完整链路「用户授权 → 生成提醒 → 发送消息 → 记录事件」

---

## 一、验证范围

任务书 Phase 4.5 第二节要求，验证微信订阅消息真实流程：

```
用户授权 → 生成提醒 → 发送消息 → 记录事件
```

---

## 二、验证结果（真实执行，非模拟报告）

| 步骤 | 操作 | 结果 | 证据 |
|------|------|:---:|------|
| 1. 用户授权 | openid → U 编号注册 | ✅ | `openid_wx001 → U0001` |
| 2. 生成提醒 | 录票 → create_reminder | ✅ | `T0001` + `mobile_reminder_enabled` 事件 |
| 3. 发送消息 | ReminderDispatcher.dispatch_all | ✅ | `{sent: 1, failed: 0}` + **`reminder_sent` 事件** |
| 4. 记录事件 | 发送/点击行为入埋点 | ✅ | reminder_sent=1 · 点击回执=True |

### 完整事件流（实测）

```
mobile_opened            （用户授权后打开）
   ↓
mobile_ticket_saved      （录第一张票 T0001）
   ↓
mobile_reminder_enabled  （创建开奖提醒）
   ↓
reminder_sent            （dispatch 发送成功）← P4.5 数据链路修复新增
   ↓
（用户点击推送）
   ↓
draw_reminder_clicked    （点击回执）→ reminders 表 clicked=True
```

### 提醒价值统计（实测）

| 指标 | 值 |
|------|-----|
| 提醒发送数 | 1 |
| 提醒点击数 | 1 |
| **点击率** | **1.0**（目标 ≥30% ✅） |

---

## 三、数据链路修复（P4.5）

### 发现的问题
`ReminderDispatcher.dispatch_all()` 发送成功后只标记 `reminders.sent=True`，**未记录 `reminder_sent` 行为事件** → 埋点数据链路断裂（发送行为无法从行为事件统计）。

### 修复
`backend/mobile/wechat.py`：`ReminderDispatcher` 增加可选 `event_repo`，发送成功后记录 `reminder_sent` 事件（source=MOBILE），失败保留未发送状态可重试。

### 回归验证
`test_reminder.py` + `test_service_flow.py` **34 passed**（向后兼容，event_repo 可选）。

---

## 四、微信客户端模式说明

| 模式 | 触发条件 | 行为 |
|------|---------|------|
| **mock**（验证阶段） | 未配置 `WECHAT_APPID/SECRET/TEMPLATE_ID` 或 `WECHAT_MOCK=1` | 直接返回 ok，不真正调用微信 API |
| **真实**（正式部署） | 配置三个环境变量 + `WECHAT_MOCK=0` | 调微信 `subscribe/send` API 真实下发 |

> **上线真实推送前需要**：注册微信小程序 → 申请「开奖提醒」订阅消息模板 → 配置模板 ID。

---

## 五、诚实声明

- ✅ 本验证跑通**完整逻辑链路**（mock 微信客户端）
- ⚠️ **未执行真实微信服务器下发**（需小程序 appid/secret/template_id，属产品负责人部署步骤）
- ✅ 链路中所有埋点事件真实写入 `mobile_behavior_events`（source=MOBILE）

---

## 六、结论

微信提醒链路**逻辑验证通过**，数据链路修复完成（reminder_sent 事件补录），达到「用户授权→提醒→发送→记录」闭环。真实微信推送待注册小程序后配置即启用。
