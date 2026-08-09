# Atlas v4.9.1 — 用户编号体系（User ID System）

> 模块：`engine/user_experiment/registry.py` · 状态：✅ 完成
> 目标：禁止匿名统计，为每位真实用户分配稳定编号 U0001–U0050+

---

## 一、编号规则

```
U + 4 位序号
U0001, U0002, ..., U0050, ...
```

- 自动分配：基于现有最大编号 +1
- 重复注册安全：从持久化文件读取，重启不重复
- 校验正则：`^U\d{4,}$`

---

## 二、用户字段（11 项，任务书固定）

| 字段 | 类型 | 说明 |
|------|------|------|
| `user_id` | str | 编号 U0001 |
| `registered_at` | str | 注册时间（ISO） |
| `first_open_at` | str | 首次打开时间 |
| `first_ticket_saved_at` | str | 首次保存彩票时间 |
| `lottery_type` | str | 大乐透 / 双色球 / 两者都有 / 其他 |
| `purchase_frequency` | str | 每周 / 每月 / 偶尔 / 首次 |
| `reminder_enabled` | bool | 是否开启提醒 |
| `draw_checked` | bool | 是否查看开奖 |
| `claim_completed` | bool | 是否兑奖 |
| `asset_viewed` | bool | 是否查看资产 |
| `weekly_report_viewed` | bool | 是否查看周报 |

---

## 三、核心方法

| 方法 | 说明 |
|------|------|
| `register()` | 注册新用户，自动分配编号 |
| `allocate_next_id()` | 计算下一个编号 |
| `get(user_id)` | 查询用户 |
| `count()` | 用户总数 |
| `mark(user_id, field)` | 置行为里程碑为 True（提醒/开奖/兑奖/资产/周报） |
| `set_first_ticket_at()` | 记录首次保存时间 |
| `export_csv()` | 导出用户清单（UTF-8 BOM） |

---

## 四、数据流

```
种子用户招募 → register() 分配 U0001 → 行为埋点
  → mark() 更新里程碑 → export_csv() 导出分析
```

存储：`~/.atlas/users_v491.jsonl`（追加写）
导出：`~/.atlas/users_v491_export.csv`

---

## 五、验收

- ✅ 50 用户编号测试通过（U0001–U0050）
- ✅ 重启后续号正确（U0050 后分配 U0051）
- ✅ 非法字段规范化（未知彩种→其他）
- ✅ 11 字段 CSV 导出完整
