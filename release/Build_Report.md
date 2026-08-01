# Atlas Quant Platform — Build Report

> Sprint E1 · Phase 9 交付物 · 2026-08-02

## 构建产物

| 产物 | 大小 | 时间 | 说明 |
|------|------|------|------|
| `dist/Atlas.exe` | 102 MB | 01:14 | PySide6 桌面客户端（含数据） |
| `dist/Atlas_CLI.exe` | 8.9 MB | 01:12 | 命令行工具 |
| `dist/Atlas_Worker.exe` | 8.9 MB | 01:12 | 后台服务 |
| `release/Atlas_Setup.exe` | 121 MB | 01:14 | Inno Setup 安装程序 |
| `release/Atlas_Portable.zip` | 118 MB | 01:15 | 便携免安装版 |
| `release/Atlas_Debug.zip` | 118 MB | 01:16 | 调试包 |

## Installer Report

- **工具**：Inno Setup 6.7.3（ISCC.exe）
- **脚本**：`installer/setup.iss`
- **功能**：安装向导 / 桌面快捷方式（可选）/ 开始菜单 / 卸载 / 版本升级
- **多语言**：English（官方中文语言包需额外安装，默认英文）
- **编译结果**：Successful compile (15.0 sec)

## Portable Report

- `Atlas_Portable.zip` 含：Atlas.exe + Atlas_CLI.exe + Atlas_Worker.exe
- 免安装，解压即用
- 桌面版内置数据，不依赖后端服务

## Artifacts Report

- 构建产物不入 Git（dist/build/release 二进制被 .gitignore 排除）
- 源码与 spec 入 Git，可在任意环境用 `packaging/package.ps1` 复现构建
- GitHub Actions 发布时自动生成全部产物并上传 Release

## 验证结果

| 验证项 | 结果 |
|--------|------|
| Atlas.exe 启动 | ✅ |
| Atlas.exe 6 功能页 | ✅ |
| Atlas_CLI.exe | ✅ `status` 命令正常 |
| Atlas_Worker.exe | ✅ 数据检查加载 15 期 |
| Atlas_Setup.exe 编译 | ✅ |
| CI/CD workflows | ✅ yaml 语法有效 |
