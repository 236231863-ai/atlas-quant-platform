# Quick Start

## 方式一：桌面应用（推荐）

1. 下载 `Atlas_Setup.exe`（或解压 `Atlas_Portable.zip`）
2. 安装并启动 `Atlas.exe`
3. 桌面版内置数据，开箱即用（Dashboard / 分析 / 策略 / 回测 / AI / 报告）

## 方式二：源码开发

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements-dev.txt -c constraints.txt

# 3. 运行测试
pytest tests/ -q

# 4. 启动桌面
cd desktop && python main.py
```

## 方式三：Docker

```bash
docker compose -f docker/docker-compose.yml up
```

## 方式四：CLI

```bash
# 源码运行
python tools/atlas-cli/main.py status

# 打包版
Atlas_CLI.exe status
```
