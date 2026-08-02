# Atlas v3.7.1 Beta 发布报告

> Sprint：Beta Launch Infrastructure
> 版本：v3.7.1-beta
> 日期：2026-08-02
> 结论：**Atlas 已具备邀请真实用户体验的 Beta 产品条件。**

---

## 1. 发布产物

| 产物 | 路径 | 大小 |
|------|------|------|
| 安装包 | `release/AtlasQuant-3.7.1-beta-Setup.exe` | 156 MB |
| 便携包 | `release/AtlasQuant-3.7.1-beta.zip` | 145 MB |
| 桌面 exe | `dist/Atlas.exe` | — |
| 版本 | 窗口标题 `Atlas Quant Platform v3.7.1-beta` | ✅ 实测启动 |

## 2. 完成情况

| Phase | 交付 | 测试 |
|-------|------|------|
| P0 Beta 冻结 | docs/beta/ 3 份（测试计划/用户指南/反馈流程） | — |
| P1 Beta 用户 | engine/beta BetaUserManager | 109 ✅ |
| P2 产品分析 | engine/product_analytics_v2 事件+报告 | 151 ✅ |
| P3 反馈中心 | backend/feedback（4 类型+状态机） | 153 ✅ |
| P4 Release Center | release_center（版本/更新/指南/FAQ） | 115 ✅ |
| P5 体验优化 | 帮助中心 + 反馈入口 + 5 分钟上手 | 集成 ✅ |

**v3.7.1 新增 528 测试**；全量回归 **2129 通过**（v361 859 + v370 742 + v371 528）。

## 3. Beta 能力清单

- ✅ 用户编号/批次/版本记录（BetaUserManager）
- ✅ 产品使用数据：会话/分析完成率/崩溃率/导出/回测（ProductAnalytics）
- ✅ 反馈闭环：Bug/建议/评分 + New→Reviewing→Fixed→Closed
- ✅ 版本中心：版本信息/更新说明/安装指南/FAQ
- ✅ 帮助中心 UI + 反馈提交入口
- ✅ 首次用户 5 分钟完成第一次分析（三步引导 + 自动报告）

## 4. 验收核对

| 验收项 | 结果 |
|--------|------|
| 测试 ≥700 | ✅ 2129 |
| Windows 启动正常 | ✅ v3.7.1-beta 窗口实测 |
| 旧功能全部通过 | ✅ 全量回归 |
| 生成 Release Candidate | ✅ Setup + zip |
| 版本 v3.7.1-beta | ✅ |

## 5. 后续

- Beta 1（10-20 用户）邀请，收集反馈与使用数据。
- 依据反馈迭代 v3.7.2 → v4.0（用户生态）。
