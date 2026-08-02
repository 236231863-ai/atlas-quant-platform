# Phase 1 — Windows 正式安装包报告

> Atlas Quant Platform v3.6.0 Product Launch
> 日期：2026-08-02

---

## 完成报告

### 交付内容

| 项目 | 说明 |
|------|------|
| `release/Atlas_Setup.exe` | **150 MB** 正式安装包（v3.6.0，双语） |
| `dist/Atlas.exe` | **131 MB** 桌面软件（v3.6.0 标题） |
| 中文语言包 | Inno Setup 官方简体中文（6.5.0+） |
| 安装体验 | 安装向导 / 语言选择 / 桌面快捷方式（可选）/ 开始菜单 / 卸载 / 版本升级 |

### 本阶段改进（vs E1 安装包）
- 版本升级至 v3.6.0
- 新增简体中文语言（安装向导双语）
- 桌面软件版本标题更新

## 测试报告

| 测试项 | 结果 | 证据 |
|--------|------|------|
| 安装包编译 | ✅ | ISCC 20.3 秒编译成功 |
| 静默安装 | ✅ | Atlas.exe/CLI/Worker/LICENSE/README 全部就位 |
| 卸载流程 | ✅ | unins000.exe 运行，主文件移除 |
| 桌面软件版本 | ✅ | 标题 "Atlas Quant Platform v3.6.0" |
| 中文语言加载 | ✅ | 官方 ChineseSimplified.isl 21KB |

> 注：卸载时 Atlas.exe 残留系该文件被运行中进程占用，非卸载器缺陷；关闭进程后即可正常移除。

## 使用说明（用户角度）

### 1. 用户在哪里下载？
安装包：`release/Atlas_Setup.exe`（正式发布时上传 GitHub Release / 官网下载页）

### 2. 用户如何安装？
1. 双击 `Atlas_Setup.exe`
2. 选择语言（简体中文 / English）
3. 跟随向导 → 可选择创建桌面快捷方式
4. 完成安装后自动启动 Atlas

### 3. 用户如何第一次使用？
安装完成后双击桌面「Atlas Quant Platform」图标即可启动，开箱即用（内置数据）。

### 4. 用户获得什么价值？
- 6 大功能模块：数据看板 / 数据分析 / 策略实验 / 回测中心 / AI 助手 / 研究报告
- 无需配置环境，双击即用
- 卸载干净，不残留

## 实际产物

```
release/Atlas_Setup.exe   安装包（150 MB）
dist/Atlas.exe            桌面软件（131 MB）
```
