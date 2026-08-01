# Atlas Quant Platform — Release Checklist

> Sprint E1 · Phase 9 交付物

## Release Checklist

- [x] Git 初始化完成（main + develop 分支）
- [x] README / LICENSE / CHANGELOG 完整
- [x] Requirements 整理（五环境分层 + constraints 锁定）
- [x] Build 系统统一（build.ps1/bat/sh）
- [x] PyInstaller 打包成功（Atlas.exe / Atlas_CLI.exe / Atlas_Worker.exe）
- [x] Atlas_Setup.exe 生成（Inno Setup）
- [x] Atlas_Portable.zip 生成
- [x] Docker Compose 配置（backend/frontend/nginx/postgres/redis）
- [x] GitHub Actions CI/CD 配置
- [x] Documentation 文档体系
- [x] Release Notes 生成

## RC Checklist（发布候选）

- [x] 完整回归测试通过（tests/ 全量）
- [x] 桌面应用可启动、可导航、功能可用
- [x] CLI 可运行
- [x] 安装程序可编译
- [x] 便携包可解压运行
- [x] 版本号一致（pyproject / README / setup.iss / CHANGELOG）

## Version Checklist

- [x] SemVer 版本策略已定义（engineering/Git_Workflow.md）
- [x] 当前版本 v3.5.2
- [x] Tag 规范：v3.5.2-rc1（发布候选）
- [x] CHANGELOG 同步
