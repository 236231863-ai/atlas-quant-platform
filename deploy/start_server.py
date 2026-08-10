"""Atlas Mobile MVP - 生产启动入口（腾讯云部署）。

环境变量（部署约定）：
  WX_APPID        微信小程序 AppID
  WX_APPSECRET    微信小程序 AppSecret（严禁写入代码/Git）
  DATABASE_PATH   SQLite 数据库文件所在目录（如 /opt/atlas/data）
  WECHAT_LOGIN_MOCK  登录 mock 开关（生产置 0）
  WECHAT_MOCK         订阅消息 mock 开关（生产置 0）

安全：
  - 密钥仅从环境变量读取，禁止硬编码
  - uvicorn 监听 127.0.0.1:8000（不暴露公网，由 Nginx 反向代理 HTTPS）
  - 启动时加载 CORS（供浏览器调试；小程序原生请求不受 CORS 限制）

FastAPI 启动入口与本地验证版保持一致（include_router 同一路由）。
"""
from __future__ import annotations

import os


def _env_map() -> None:
    """部署环境变量 → backend.mobile 兼容环境变量映射（在 import backend 前执行）。"""
    wx_appid = os.environ.get("WX_APPID", "")
    wx_secret = os.environ.get("WX_APPSECRET", "")
    db_path = os.environ.get("DATABASE_PATH", "")

    if wx_appid:
        os.environ.setdefault("WECHAT_APPID", wx_appid)
    if wx_secret:
        os.environ.setdefault("WECHAT_APPSECRET", wx_secret)
    if db_path:
        os.makedirs(db_path, exist_ok=True)
        os.environ.setdefault("ATLAS_STORAGE_DIR", db_path)
    # 生产默认关闭 mock（除非显式设置）
    os.environ.setdefault("WECHAT_LOGIN_MOCK", "0")
    os.environ.setdefault("WECHAT_MOCK", "0")


_env_map()

import uvicorn  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from backend.mobile.api import auth_router, router  # noqa: E402


def create_app() -> FastAPI:
    app = FastAPI(title="Atlas Mobile MVP API (prod)", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # 浏览器调试；生产可按需收紧
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router)  # /api/auth
    app.include_router(router)       # /api/mobile/v1
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
