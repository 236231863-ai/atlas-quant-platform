# Atlas v4.9.1 — Mobile MVP 用户手册（User Manual）

> 适用：验证版（Mobile MVP v0.1）· 给产品负责人/种子用户的操作指引

---

## 一、运行前提

| 项 | 说明 |
|----|------|
| 后端 | 需运行 FastAPI 服务（见「启动后端」） |
| 小程序 | 微信开发者工具导入 `mobile_app/` 目录 |
| 订阅消息 | 验证阶段 mock（无需真实 appid/secret） |

---

## 二、启动后端

```bash
cd "C:/Users/Administrator/Documents/Codex/2026-07-28/lqrp-v0-1-v0-2-v0/AtlasQuant"
PYTHONIOENCODING=utf-8 python -c "
import uvicorn
from backend.mobile.api import router
from fastapi import FastAPI
app = FastAPI(title='Atlas Mobile MVP API')
app.include_router(router)
uvicorn.run(app, host='127.0.0.1', port=8000)
"
```

启动后：
- 健康检查：`GET http://127.0.0.1:8000/api/mobile/v1/funnel`
- 数据库：`C:\Users\Administrator\.atlas\mobile_mvp.db`（自动创建）

---

## 三、小程序使用（种子用户流程）

1. **打开小程序** → 引导页 3 屏 → 点「开始使用 Atlas」
2. **微信授权** → 自动分配编号（U0001+），无需注册
3. **录第一张票** → 粘贴号码（如 `06 16 21 30 34 + 06 12`）→ 保存
4. **开奖提醒** → 开启订阅消息（开奖前微信通知）
5. **查看结果** → 开奖后自动核对，中奖显示奖级/金额
6. **本月统计** → 投入/中奖/净额一目了然

---

## 四、号码输入格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 普通 | `06 16 21 30 34 + 06 12` | 大乐透前5+后2 |
| 连续 | `06162130340612` | 10 位数字连续写 |
| 逗号/竖线 | `06,16,21,30,34\|06,12` | 分隔符自适应 |
| 双色球 | `03 08 15 22 26 33 + 09` | 红6+蓝1 |

**自动校验**：号码越界（>35 等）、重复、数量错误会被拒绝并提示。

---

## 五、管理员操作（产品负责人）

### 查看用户数与漏斗
```bash
curl http://127.0.0.1:8000/api/mobile/v1/funnel
```

### 手动登记每日记录（沿用 v4.9.1）
```bash
cd "C:/Users/Administrator/Documents/Codex/2026-07-28/lqrp-v0-1-v0-2-v0/AtlasQuant"
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.daily_log import DailyExperimentLog
DailyExperimentLog().record(new_users=5, first_open=3, ticket_saved=2)
"
```

### 导出
- 用户清单：`~/.atlas/users_v491_export.csv`
- 每日记录：`~/.atlas/daily_log_v491_export.csv`
- 埋点事件：存于 `~/.atlas/mobile_mvp.db`（mobile_behavior_events 表）

---

## 六、14 天验证节奏（管理员）

| 天 | 动作 | 检查 |
|----|------|------|
| T+1 | 首批 ≥10 人进入，录票 | 首次保存率初步 |
| T+3 | 累计 ≥30，触达未录票用户 | 建档率 ≥50% |
| T+5 | 首个开奖日，推送全量 | 提醒→打开率 |
| T+7 | **D1/D7 + Q2 问卷** | D1≥40% · D7≥30% · Q2≥60% |
| T+13 | 数据封板 | ≥50 用户 |
| T+14 | 生成验证报告 | 判断 A/B/C |

---

## 七、免责声明

- 本验证版不提供号码推荐/预测，开奖结果随机，任何号码理论概率相同
- 彩票长期期望为负，请理性购彩
- 订阅消息为验证用途（mock 下发），真实推送需注册小程序后配置模板
