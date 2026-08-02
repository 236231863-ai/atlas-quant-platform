# Atlas Quant Platform — v3.6.0 Release Notes

> Product Launch Release Candidate
> 发布日期：2026-08-02

## 版本亮点

Atlas Quant Platform 从「开发项目」正式升级为「用户产品」：

### 🎯 产品化（P0-P7）
- **P0 产品冻结**：锁定 6 大功能模块，专注用户体验
- **P1 正式安装包**：双语安装向导（简体中文 + English）
- **P2 品牌系统**：专业 Logo / 配色 / 规范，全端应用
- **P3 真实数据体系**：多彩种（大乐透/双色球）+ 用户数据导入，来源透明
- **P4 用户账户**：本地档案 + 首次使用引导
- **P5 AI 助手升级**：可配置 API 接入真实大模型，离线模式保留
- **P6 Web 规划**：API + 前端 + Docker 全就绪（v3.7.0 方向）

### 📦 交付产物

| 产物 | 大小 | 说明 |
|------|------|------|
| `Atlas_Setup.exe` | ~150 MB | 正式安装包（双语） |
| `Atlas_Portable.zip` | ~120 MB | 便携版 |
| `Atlas.exe` | ~131 MB | 桌面软件 |
| `Atlas_CLI.exe` / `Atlas_Worker.exe` | 8.9 MB | 命令行 / 后台服务 |

## 快速开始

1. 下载 `Atlas_Setup.exe` → 双击安装（或解压便携版）
2. 首次启动 → 欢迎向导 → 开始使用
3. 6 大模块：数据看板 / 数据分析 / 策略实验 / 回测中心 / AI 助手 / 研究报告
4. 可选：导入真实数据（`tools/import_data.py`）+ 配置 AI API

## 技术栈

Python 3.11+ / PySide6 / matplotlib / FastAPI / SQLAlchemy / Docker

## 已知事项

- 桌面版默认内置演示数据（15 期），真实数据通过导入工具接入
- AI 在线模式需用户自行配置 DeepSeek API Key
- Web 版为规划阶段（v3.7.0）

## 免责声明

学术研究工具。不预测、不推荐、不承诺。
