# Phase 4 — 用户账户体系报告

> Atlas Quant Platform v3.6.0 Product Launch
> 日期：2026-08-02

---

## 完成报告

### 交付内容

| 项目 | 路径 | 说明 |
|------|------|------|
| 本地用户档案 | `desktop/user_profile.py` | 用户名/语言/主题，JSON 持久化到 `~/.atlas/profile.json` |
| 首次使用引导 | `desktop/pages/first_run_dialog.py` | 欢迎 + 用户名 + 数据说明 |
| 主窗口集成 | `desktop/windows/main_window.py` | 首次启动自动显示引导 |
| 设置持久化 | `user_profile.save_profile()` | 跨启动保存 |

### 用户数据流

```
首次启动 → FirstRunDialog（欢迎/用户名/数据说明）
              ↓ 点击「开始使用」
          profile.json 保存（~/.atlas/）
              ↓
          下次启动直接进入，不再引导
```

### 设计说明
- **纯本地**：无服务器账户，数据存用户主目录，隐私安全
- **首次引导**：回答「用户如何第一次使用」——引导用户设置称呼 + 了解数据导入
- **可扩展**：后续可对接云端账户（Phase 6 Web 版规划）

## 测试报告

| 测试项 | 结果 |
|--------|------|
| 档案加载/保存 | ✅ 持久化到 ~/.atlas/profile.json |
| 首次运行标记 | ✅ first_run_completed 控制 |
| 首次引导触发 | ✅ 未完成时显示对话框 |
| 完成后跳过 | ✅ 二次启动直接进入 |
| MainWindow 集成 | ✅ 正常加载 |

## 使用说明（用户角度）

### 1. 用户在哪里下载？
随桌面软件提供，首次启动自动出现引导。

### 2. 用户如何安装？
无需额外安装，首次启动即引导。

### 3. 用户如何第一次使用？
1. 首次启动 → 欢迎向导
2. 输入您的称呼 → 点击「开始使用」
3. 进入 6 大功能页面
4. 可导入真实数据（Phase 3 工具）

### 4. 用户获得什么价值？
- 个性化：称呼定制
- 首次上手零门槛：引导说明
- 数据隐私：本地存储，不泄露

## 实际产物

```
desktop/user_profile.py            本地档案 + 持久化
desktop/pages/first_run_dialog.py  首次引导对话框
desktop/windows/main_window.py     集成（首次触发）
~/.atlas/profile.json              用户档案（运行时生成）
```
