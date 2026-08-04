# Atlas v4.5 产品报告（Product Report）

版本：v4.5.0 · 可信开奖数据与用户留存系统 · 2026-08-04

## 定位

**Atlas 帮用户管理每一张彩票：开奖自动提醒、自动兑奖、长期复盘。**

## 修改内容

| Phase | 内容 | 文件 |
|-------|------|------|
| P1 | 数据可信中心（Provider 链 + 校验 + 健康报告） | engine/data_center/ |
| P2 | 自动开奖监控（开奖日检测 + draw_updated 事件） | engine/draw_monitor/monitor.py |
| P3 | Windows 后台提醒（Toast→msg→日志 降级链） | engine/draw_monitor/notifier.py + worker |
| P4 | 兑奖信任升级（来源/期号/更新时间/校验状态） | engine/claim_center/claim.py |
| P5 | 用户行为埋点 + User Behavior Report | engine/user_events/report.py |

## 用户价值

1. **数据可信**：官方源 + 校验 + 「已验证」标注 + 健康报告可见
2. **提醒可靠**：关闭软件后台仍通知（开奖/中奖/待兑奖）
3. **回来理由**：自动兑奖闭环 + 长期复盘 + 行为洞察

## 验收标准

1. ✅ 关闭软件后仍能收到开奖提醒（后台计划任务 worker + WindowsNotifier）
2. ✅ 开奖数据更新后自动触发兑奖（draw_updated → AutoClaimLink）
3. ✅ 错误数据不能覆盖正确数据（DrawValidator + no_new + _valid_remote）
4. ✅ 大乐透/双色球分别使用正确数据源（gameNo 85/235，235 降级内置）
5. ✅ 「我昨天的彩票中奖了没有？」自动判断→查询→报告

## 已知限制

- 双色球官方 API（gameNo=235）当前返回 0 条，双色球保持内置 500 期
- 后台 Toast 通知依赖 Windows 通知服务，不可用降级 msg/日志

## 红线

- 无彩票预测、无推荐中奖号码、无提高中奖概率表达
