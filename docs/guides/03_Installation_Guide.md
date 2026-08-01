# Installation Guide

## 方式一：安装程序（Windows 推荐）

1. 下载 `Atlas_Setup.exe`
2. 双击运行，跟随安装向导
3. 可选择创建桌面快捷方式
4. 安装完成后自动启动

**卸载**：通过「开始菜单 → Uninstall Atlas Quant Platform」或「控制面板 → 程序和功能」。

## 方式二：便携版

1. 下载 `Atlas_Portable.zip`
2. 解压到任意目录（如 `D:\Atlas Quant Platform`）
3. 双击 `Atlas.exe` 运行

## 方式三：源码安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt -c constraints.txt
cd desktop && python main.py
```

## 系统要求

- Windows 10/11（x64）
- 或 Linux/macOS（源码运行）
- 内存 4GB+（桌面版含图表渲染）
- 磁盘 500MB+（安装后）
