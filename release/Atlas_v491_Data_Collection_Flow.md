# Atlas v4.9.1 — 数据回收流程（Data Collection Flow）

> 目的：7 天周期内真实回收 10 名用户的 8 项行为数据，供 Beta-0 分析
> 存储：`~/.atlas/mobile_mvp.db`（SQLite）· 导出：CSV

---

## 一、采集事件（8 项）

| # | 事件 | 含义 | 采集点 |
|---|------|------|--------|
| 1 | `install_completed` | 安装完成 | 首次授权 |
| 2 | `mobile_opened` | 打开小程序 | 每次进入 |
| 3 | `ticket_saved` | 录票 | 保存成功 |
| 4 | `reminder_enabled` | 开启提醒 | 订阅授权 |
| 5 | `reminder_sent` | 提醒已发 | 后端 dispatch |
| 6 | `reminder_clicked` | 点击提醒 | 点击回执 |
| 7 | `draw_viewed` | 查看开奖 | 打开结果页 |
| 8 | `claim_completed` | 兑奖完成 | 兑奖动作 |

---

## 二、数据流向

```
小程序埋点 → POST /api/mobile/v1/events → mobile_behavior_events 表
   ↓
后端提醒 → reminder_sent / reminder_clicked → mobile_reminders 表 + 事件
   ↓
产品负责人每日 → DailyExperimentLog → daily_log_v491.jsonl
   ↓
导出 CSV → 分析 → Beta0 报告
```

---

## 三、每日回收（产品负责人，3 分钟）

### 查看用户与事件数
```bash
cd "C:/Users/Administrator/Documents/Codex/2026-07-28/lqrp-v0-1-v0-2-v0/AtlasQuant"
PYTHONIOENCODING=utf-8 python -c "
import sqlite3, os
db = os.path.join(os.path.expanduser('~'), '.atlas', 'mobile_mvp.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM mobile_users'); print('用户数:', cur.fetchone()[0])
cur.execute('SELECT event_name, COUNT(*) FROM mobile_behavior_events GROUP BY event_name')
for r in cur.fetchall(): print(' ', r)
conn.close()
"
```

### 每日记录（DailyExperimentLog）
```bash
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.daily_log import DailyExperimentLog
# 例：今天新增2人、1人录票、1人开提醒
DailyExperimentLog().record(new_users=2, first_open=2, ticket_saved=1, reminder_enabled=1)
"
```

---

## 四、数据导出（Day7 封板）

```bash
PYTHONIOENCODING=utf-8 python -c "
import sqlite3, csv, os
db = os.path.join(os.path.expanduser('~'), '.atlas', 'mobile_mvp.db')
out = os.path.join(os.path.expanduser('~'), '.atlas', 'beta0_events_export.csv')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT user_id, event_name, source, timestamp FROM mobile_behavior_events ORDER BY timestamp')
rows = cur.fetchall()
with open(out, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f); w.writerow(['user_id','event_name','source','timestamp']); w.writerows(rows)
print('导出事件:', len(rows), '→', out)
conn.close()
"
```

---

## 五、数据核对清单

| 检查 | 方法 | 正常 |
|------|------|------|
| 用户数 = 10 | users 表 | 10 |
| 每用户有 mobile_opened | 事件统计 | ≥1 |
| 录票用户数 | ticket_saved 去重用户 | 记录 |
| 提醒开启数 | reminder_enabled | 记录 |
| 无模拟数据 | source 全为 MOBILE | 无 SIMULATION |

---

## 六、数据安全

- ✅ 数据存本机 `~/.atlas`，不上传第三方
- ✅ 用户匿名（U 编号 + openid 哈希），不存姓名/手机号
- ✅ 7 天结束导出后，可清理或归档

---

## 七、异常处理

| 问题 | 处理 |
|------|------|
| 事件缺失（某用户无 opened） | 检查小程序埋点调用 |
| 数据库损坏 | 用备份 `mobile_mvp.db.bak` 恢复 |
| 重复事件 | 按 user_id+event_name+timestamp 去重分析 |
