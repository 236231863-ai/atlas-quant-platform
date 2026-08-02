# Atlas v3.8.0 发布报告

> Sprint：User Value Validation & Commercial Intelligence
> 版本：v3.8.0
> 日期：2026-08-02

---

## 1. 发布产物

| 产物 | 路径 | 大小 |
|------|------|------|
| 安装包 | `release/AtlasQuant-3.8.0-Setup.exe` | 156 MB |
| 便携包 | `release/AtlasQuant-3.8.0.zip` | 136 MB |
| 桌面 exe | `dist/Atlas.exe` | ✅ 启动 v3.8.0 |

## 2. 完成情况

| Phase | 交付 | 状态 |
|-------|------|------|
| P0 冻结 | docs/product 4 份地图 | ✅ |
| P1 行为智能 | user_intelligence/v3（6 类事件）| ✅ |
| P2 价值分 | value_score（五维评分）| ✅ |
| P3 功能价值 | product_value（usage/duration/satisfaction/conversion）| ✅ |
| P4 订阅验证 | subscription/v2（FREE/PRO/ENTERPRISE）| ✅ |
| P5 反馈智能 | feedback_intelligence（分类/趋势/优先级）| ✅ |
| P6 产品总监 | product_director_v2（评估/问题/路线图）| ✅ |
| P7 桌面 UX | 个人中心（价值分/等级/AI 建议/历史）| ✅ |
| P8 商业报告 | docs/business 3 份 | ✅ |

## 3. 测试

- v3.8.0 新增 **1008 测试**（tests/v380）
- 全量回归 **3137 通过**（v361 859 + v370 742 + v371 528 + v380 1008）
- 旧功能零回归

## 4. 验收核对

| 项 | 结果 |
|----|------|
| 新增测试 ≥1000 | ✅ 1008 |
| 旧测试全过 | ✅ 3137 |
| Windows 启动正常 | ✅ v3.8.0 |
| 新功能有 UI 入口 | ✅ 个人中心面板 |
| 生成 RC | ✅ Setup + zip |

## 5. 关键能力

- 用户价值可量化（价值分 + 研究等级）
- 功能价值可归因（product_value）
- 产品决策有据（ProductDirectorV2 输出路线图）
- 商业可验证（subscription/v2 门槛 + 转化跟踪）
