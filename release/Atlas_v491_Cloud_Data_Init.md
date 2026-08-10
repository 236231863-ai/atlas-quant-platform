# Atlas v4.9.1 — 云端数据初始化方案（Cloud Data Init）

> 阶段：Phase C.3 · 目的：生产环境首次启动的数据初始化
> 原则：保留开奖数据，清空测试用户数据，Beta 从真实登录重新建档

---

## 一、初始化策略

| 表 | 处理 | 原因 |
|----|------|------|
| `mobile_draws`（开奖数据） | ✅ **保留** | 1702 期真实开奖（dlt 1202 + ssq 500），直接复用 |
| `mobile_users` | ❌ **清空** | 含 demo_openid 测试用户，污染留存统计 |
| `mobile_tickets` | ❌ **清空** | demo 测试票 |
| `mobile_reminders` | ❌ **清空** | 测试提醒 |
| `mobile_behavior_events` | ❌ **清空** | 测试埋点 |
| feedback（若有） | ❌ **清空** | 测试反馈 |

---

## 二、初始化脚本（服务器首次启动前执行）

```bash
# 在服务器 /opt/atlas/data 目录，数据库首次上传后执行
cd /opt/atlas
source venv/bin/activate
PYTHONIOENCODING=utf-8 python -c "
import os, sqlite3
db = os.path.join(os.environ.get('DATABASE_PATH', '/opt/atlas/data'), 'mobile_mvp.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
# 保留 draws，清空其余
cur.execute('DELETE FROM mobile_users')
cur.execute('DELETE FROM mobile_tickets')
cur.execute('DELETE FROM mobile_reminders')
cur.execute('DELETE FROM mobile_behavior_events')
conn.commit()
cur.execute('SELECT COUNT(*) FROM mobile_draws')
print('保留开奖数据:', cur.fetchone()[0])
for t in ['mobile_users','mobile_tickets','mobile_reminders','mobile_behavior_events']:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(f'{t} 清空后:', cur.fetchone()[0])
conn.close()
"
```

---

## 三、首次启动检查清单

| # | 检查 | 预期 |
|---|------|------|
| 1 | `/healthz` 返回 200 | `{"status":"ok"}` |
| 2 | `GET /api/mobile/v1/funnel` | `{"registered":0,...}`（用户已清空） |
| 3 | `GET /api/mobile/v1/draws/latest?lottery=dlt` | 返回最新期 26088（开奖保留） |
| 4 | 真机登录 `wx.login` | 返回 `user_id=U0001, is_new=True` |
| 5 | 再次登录同一微信 | `user_id=U0001, is_new=False`（稳定身份） |
| 6 | 录一张票 | `ticket_saved` 事件落库 |

---

## 四、注意事项

- ⚠️ 初始化**只执行一次**（Beta 开始前）。Beta 开始后禁止清空（会丢真实用户数据）
- ✅ 若需重来：用备份恢复 `mobile_mvp_YYYY-MM-DD.db` 后再清
- ✅ 开奖数据 1702 期在任何清空操作中保留

---

## 五、回滚

- 清空前先 `cp mobile_mvp.db mobile_mvp_pre_beta.db`
- 出错时恢复备份即可
