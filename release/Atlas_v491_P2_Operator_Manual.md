# Atlas v4.9.1 — P2 产品负责人操作手册（Operator Manual）

> 状态：✅ 采集就绪 · 等待产品负责人分发
> 本手册是 P2 阶段**唯一需要产品负责人执行的日常工作清单**。引擎模块已在 P1 全部就绪，产品负责人只需每日登记，不需要写代码。

---

## 一、每日流程（3 步，约 10 分钟）

### 第 1 步：注册当天新增的真实用户

每位同意体验的种子用户，用引擎注册并分配编号：

```bash
cd "C:/Users/Administrator/Documents/Codex/2026-07-28/lqrp-v0-1-v0-2-v0/AtlasQuant"
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.registry import UserRegistry
r = UserRegistry()
u = r.register(lottery_type='大乐透', purchase_frequency='每周')
print('已注册:', u.user_id)
print('当前用户数:', r.count())
"
```

> `lottery_type`：大乐透 / 双色球 / 两者都有 / 其他
> `purchase_frequency`：每周 / 每月 / 偶尔 / 首次
> 编号自动递增：U0001 → U0002 → ...
> 存储：`C:\Users\Administrator\.atlas\users_v491.jsonl`

### 第 2 步：登记当天实验计数

按「14 天计划」的 10 个字段逐日累加：

```bash
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.daily_log import DailyExperimentLog
log = DailyExperimentLog()
# 示例：今天新增 5 用户、3 人首次打开、1 人保存彩票、2 人开启提醒
log.record(new_users=5, first_open=3, ticket_saved=1, reminder_enabled=2)
print(log.summary())
"
```

> 字段：`new_users / first_open / ticket_saved / reminder_enabled / draw_checked / claim_completed / asset_viewed / weekly_report_viewed / feedback_count`
> 同名 key 重复调用会**累加**；日期缺省为今天。
> 存储：`C:\Users\Administrator\.atlas\daily_log_v491.jsonl`

### 第 3 步：查看当天汇总

```bash
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.daily_log import DailyExperimentLog
log = DailyExperimentLog()
s = log.summary()
print('已记录天数:', s['days'])
print('日期范围:', s['date_range'])
print('累计:', s['totals'])
"
```

---

## 二、反馈问卷收集（第 3–7 天）

通过用户反馈入口（或线下收集）采集 4 问答案，用引擎登记：

```bash
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.feedback import UserFeedbackSurvey
fb = UserFeedbackSurvey()
# Q1 使用原因: A/B/C/D/E/F；Q2 不可替代: A/B/C/D/E；Q3 流失: A/B/C/D/E/F；Q4 付费: 0/3/6/9/12
fb.record(user_id='U0001', q_use='A', q_disappear='A', q_churn='', pay_willing=6)
print('反馈数:', fb.count())
"
```

---

## 三、关键检查节点（14 天节奏）

| 节点 | 检查 | 门槛 | 未达标的动作 |
|------|------|------|------------|
| **T+1** | 首批注册 | ≥10 用户 | 扩大招募 / 群发第二波 |
| **T+3** | 建档率初步 | 首次建档率≥50% | 检查录入是否太麻烦 |
| **T+7** | **D1/D7 留存** | D1≥40% · D7≥30% | 定位流失环节 |
| **T+7** | 提醒点击率 | ≥30% | 检查提醒触达 |
| **T+13** | 数据封板 | ≥50 用户 | 延长采集 / 扩大招募 |
| **T+14** | 进入 P3 分析 | 全部数据导出 | 生成 6 份报告 |

---

## 四、数据导出（P3 分析用，T+13 执行）

```bash
PYTHONIOENCODING=utf-8 python -c "
from engine.user_experiment.registry import UserRegistry
from engine.user_experiment.daily_log import DailyExperimentLog
r = UserRegistry(); log = DailyExperimentLog()
print('用户导出:', r.export_csv())
print('日志导出:', log.export_csv())
"
```

导出文件：
- `C:\Users\Administrator\.atlas\users_v491_export.csv`
- `C:\Users\Administrator\.atlas\daily_log_v491_export.csv`

---

## 五、护栏（fail-fast）

| 护栏 | 触发动作 |
|------|---------|
| 首次建档率 <50% | P2 Review 标记 B（调整建档流程） |
| 用户数 <50 | 延长采集或扩大招募 |
| 提醒点击率 <30% | 定位提醒触达问题 |
| 数据异常 | 检查埋点链路，修复后继续 |

---

## 六、禁止（实验期间）

- ❌ 新增功能 / 优化 UI / 云同步 / 手机端
- ❌ 模拟数据进入真实统计（所有记录必须来自真实用户）
- ❌ 伪实时双色球数据
- ❌ 号码推荐 / 预测 / 提高中奖概率宣传
