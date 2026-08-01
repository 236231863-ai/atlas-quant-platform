# FAQ

### Q1：桌面版启动后页面没数据？
桌面版内置 `data/raw/dlt_2024_sample.csv`（15 期大乐透样例）。如需真实数据，替换该 CSV 并重新打包。

### Q2：为什么导航切换页面后没有功能？
旧版为空壳。E1 后已实现 6 个功能页面。请重新下载最新 `Atlas_Setup.exe` 或 `Atlas_Portable.zip`。

### Q3：AI 助手需要联网/API Key 吗？
不需要。AI 助手基于本地统计的规则问答，离线可用。

### Q4：安装程序支持中文吗？
当前为 English 界面（Inno Setup 官方不含中文语言包，可手动添加）。

### Q5：如何运行测试？
```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

### Q6：如何构建桌面 exe？
```bash
powershell -File packaging/package.ps1 -Desktop
```

### Q7：后端 API 如何启动？
```bash
uvicorn backend.api.v1.app:app --reload --port 8000
```

### Q8：Docker 部署需要什么？
需安装 Docker Desktop，然后 `docker compose -f docker/docker-compose.yml up`。

### Q9：数据是否可复现？
是。`constraints.txt` 锁定依赖上限，保证构建可复现。
