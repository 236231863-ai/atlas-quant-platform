# Atlas Quant Platform — Release Notes

## v3.5.2 (Engineering Sprint E1 RC1)

**发布日期**：2026-08-02

### 工程化里程碑（Engineering Sprint E1）

本次为工程化 Sprint，不含新增业务功能，聚焦将 Atlas 从"开发文件夹"升级为可发布软件工程：

- **Git 工程化**：标准分支策略（main/develop/release/feature/hotfix）+ Commit/Tag/Version 规范
- **VSCode 工程**：F5 一键调试（Desktop/Backend/CLI/Pytest）+ 推荐插件
- **依赖管理**：requirements 五环境分层 + constraints.txt 版本锁定
- **统一构建**：build.ps1/bat/sh 一键 Build Pipeline
- **可执行打包**：Atlas.exe（桌面）/ Atlas_CLI.exe / Atlas_Worker.exe
- **安装程序**：Atlas_Setup.exe（Inno Setup 安装向导）
- **Docker 编排**：backend/frontend/nginx/postgres/redis 5 服务
- **GitHub 工程**：CI（lint+test+coverage+build）+ CD（Release artifacts）
- **发布工程**：Atlas_Portable.zip / Atlas_Debug.zip / Release Notes

### 下载

| 产物 | 说明 |
|------|------|
| `Atlas_Setup.exe` | 安装程序（推荐） |
| `Atlas_Portable.zip` | 免安装便携版 |
| `Atlas_Debug.zip` | 调试包（含 README/License） |

### 已知限制

- 桌面版使用内置大乐透样例数据（15 期），真实数据接入见后续 Sprint
- Docker 需在装有 Docker 的环境中执行 `docker compose up`
