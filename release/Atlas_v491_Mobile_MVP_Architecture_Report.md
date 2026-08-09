# Atlas v4.9.1 — Mobile MVP 架构报告（Architecture Report）

> 版本：Mobile MVP v0.1 · 架构原则：最低成本、可验证、不破坏现有桌面

---

## 一、总体架构

```
┌─────────────────────────────────────────────┐
│  微信小程序（mobile_app/）                    │
│  引导 → 我的票 → 录票 → 开奖结果 → 提醒 → 统计 │
│  utils/api.js（REST 客户端 + 埋点上报）        │
└──────────────────┬──────────────────────────┘
                   │ HTTPS JSON
┌──────────────────▼──────────────────────────┐
│  FastAPI（backend/mobile/api.py）            │
│  /api/mobile/v1/{users,tickets,draws,       │
│                  reminders,events,funnel}    │
├─────────────────────────────────────────────┤
│  Service 层（backend/mobile/service.py）     │
│  录票解析/兑奖核对/提醒/漏斗/埋点              │
├─────────────────────────────────────────────┤
│  Repository 层（backend/mobile/repositories）│
│  UserRepo / TicketRepo / DrawRepo /         │
│  ReminderRepo / EventRepo                    │
├─────────────────────────────────────────────┤
│  SQLite（backend/mobile/db.py · MobileDB）   │
│  五张表：mobile_users / mobile_tickets /     │
│  mobile_draws / mobile_reminders /          │
│  mobile_behavior_events                     │
└─────────────────────────────────────────────┘
        ┌──────────────────────────┐
        │ 微信订阅消息（wechat.py）  │
        │ WeChatReminderClient      │
        │ ReminderDispatcher        │
        └──────────────────────────┘
```

---

## 二、分层职责（强制 Repository 模式）

| 层 | 文件 | 职责 | 数据库操作 |
|----|------|------|-----------|
| ORM 模型 | `models.py` | 5 张表定义（SQLAlchemy 2.x） | 否 |
| DB 工厂 | `db.py` | engine/session/建表 | 否 |
| **Repository** | `repositories.py` | 所有 SQL 操作（增删查改） | **唯一允许触库层** |
| Service | `service.py` | 业务规则（解析/兑奖/漏斗/提醒） | 否（只调 Repository） |
| API | `api.py` | REST 路由 + schema 校验 | 否 |
| 微信 | `wechat.py` | 订阅消息下发 | 否 |

> **业务代码禁止直接操作数据库**：`service.py` / `api.py` 只依赖 Repository 接口，符合设计任务书要求。

---

## 三、五张核心表

| 表 | 主键 | 关键字段 | 关系 |
|----|------|---------|------|
| mobile_users | user_id(U0001) | openid(唯一) · registered_at · first_ticket_saved_at · 里程碑字段 | 1—N tickets |
| mobile_tickets | ticket_id(T0001) | user_id · lottery · front(JSON) · back(JSON) · issue · claimed | N—1 draws(issue) |
| mobile_draws | issue | lottery · front · back · draw_date | — |
| mobile_reminders | id(uuid) | user_id · ticket_id · issue · sent · clicked | 1—N users |
| mobile_behavior_events | id(uuid) | event_name · user_id · source · timestamp · data(JSON) | 1—N users |

---

## 四、埋点架构（复用 + 扩展）

```
engine/user_experiment/events.py
  EXPERIMENT_EVENTS（17 旧 + 5 新 = 22）
  SOURCE_REAL / SOURCE_MOBILE / SOURCE_SIMULATION
  normalize_source()：MOBILE 独立，非 SIM → REAL
  is_real_source()：REAL 或 MOBILE = 真实
  real_events()：REAL + MOBILE（simulation 排除）

funnel/metrics/retention：source=SOURCE_REAL 时按 is_real_source 过滤
  → MOBILE 自动并入真实统计，桌面/移动统一口径
```

**关键改动**：`real_events()` 与三个统计模块的 REAL 过滤从 `== SOURCE_REAL` 改为 `is_real_source(...)`，MOBILE 计入真实但来源可区分。

---

## 五、提醒架构

```
create_reminder() → mobile_reminders 行（去重）
  → 用户标记 reminder_enabled
  → ReminderDispatcher.dispatch_all()
      → WeChatReminderClient.send_draw_reminder(openid, issue, date)
          → mock（验证模式）/ 微信 API（真实模式）
      → mark_sent
  → 用户点推送 → /reminders/click → mark_clicked
  → 点击率 = clicked / sent（目标 ≥30%）
```

---

## 六、隔离与安全

| 关注点 | 方案 |
|--------|------|
| 测试隔离 | `MobileDB.in_memory()` + StaticPool（内存库跨连接共享） |
| 真实数据保护 | 测试 conftest 设 `ATLAS_STORAGE_DIR=tmp_path`，不触碰 `~/.atlas` |
| 与现有桌面隔离 | `backend/mobile/` 独立 Base，不依赖现有 async backend |
| 号码校验 | 越界/重复/数量错误全部拒绝（DataQuality 红线） |
| 红线 | 无预测/推荐/社区/商城 |

---

## 七、诚实限制

- 后端为**验证版**：单 SQLite、无用户密码、无云同步、微信 openid 即身份
- 订阅消息为 mock 优先，真实模板需注册小程序后配置
- 当前**无真实用户数据**，架构验证通过不代表产品验证通过
