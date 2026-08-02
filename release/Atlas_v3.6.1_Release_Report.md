# Atlas v3.6.1 Release Report

> 版本：v3.6.1（Product Trust & Real Usage Upgrade）
> 日期：2026-08-02
> 状态：**Release Candidate 就绪**

---

## 1. 发布产物

| 产物 | 路径 | 大小 | 校验 |
|------|------|------|------|
| Windows 安装包 | `release/AtlasQuant-3.6.1-Setup.exe` | 156 MB | ✅ 编译成功 |
| 便携包 | `release/AtlasQuant-3.6.1.zip` | 154 MB | ✅ 生成成功 |
| 桌面可执行 | `dist/Atlas.exe` | 137 MB | ✅ 实测启动，窗口 v3.6.1 |
| CLI 可执行 | `dist/Atlas_CLI.exe` | 8.9 MB | ✅ |
| Worker 可执行 | `dist/Atlas_Worker.exe` | 8.9 MB | ✅ |

---

## 2. 版本一致性

| 位置 | 值 |
|------|-----|
| pyproject.toml | 3.6.1 |
| 窗口标题 | Atlas Quant Platform v3.6.1 |
| setup.iss | 3.6.1 |
| CHANGELOG | v3.6.1 条目 |

---

## 3. 回归验证

| 项目 | 结果 |
|------|------|
| 启动（桌面快捷方式/exe） | ✅ 窗口 `Atlas Quant Platform v3.6.1` |
| Dashboard 数据 | ✅ 520 期真实数据 · 2023-02-22 ~ 2026-08-01 |
| 数据可信等级 | ✅ A（可信） |
| 6 页面导航 | ✅ 全部正常 |
| 回测（样本内外 + 随机基准） | ✅ 517 期回测 + 诚实结论 |
| 报告/回测导出 | ✅ MD/CSV/PNG/PDF |
| 工程测试 | ✅ **859 passed** |
| 崩溃恢复 | ✅ 标记→检测→清理 |

---

## 4. 更新内容（vs v3.6.0）

1. **数据**：15 期样例 → 520 期官方真实数据（体彩 API）。
2. **回测**：可信化（样本划分 / 随机基准 / 免责）。
3. **引导**：三步向导，30 秒上手。
4. **导出**：四格式输出。
5. **稳定性**：全局异常 / 崩溃恢复 / 日志 / 健康检查。
6. **测试**：859 个工程测试（tests/v361）。

---

## 5. 已知事项

- 双色球仅样例数据（福彩源待扩展）。
- 旧 engine 概念模块冻结（v3.7 归档）。
- 安装包未做代码签名（SmartScreen 可能提示"未知发布者"，建议后续购买证书）。

---

## 6. 发布建议

1. 上传 `AtlasQuant-3.6.1-Setup.exe` + `AtlasQuant-3.6.1.zip` 到 GitHub Releases，tag `v3.6.1-rc1`。
2. 附 RELEASE_NOTES（见 CHANGELOG v3.6.1）。
3. 收集用户反馈后定版 v3.6.1。

*本报告基于 2026-08-02 实测产物与验证。*
