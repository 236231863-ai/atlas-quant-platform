"""backend.mobile.db - SQLite engine / session 工厂（同步，测试友好）。

支持：
- 默认文件数据库：~/.atlas/mobile_mvp.db
- 测试用内存数据库：:memory:（通过 MobileDB(url=":memory:")）
"""
from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.mobile.models import MobileBase


def default_db_path() -> str:
    """默认数据库路径：~/.atlas/mobile_mvp.db。"""
    d = os.environ.get("ATLAS_STORAGE_DIR") or os.path.join(os.path.expanduser("~"), ".atlas")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "mobile_mvp.db")


class MobileDB:
    """Mobile MVP 数据库句柄：engine + session 工厂 + 建表。"""

    def __init__(self, url: Optional[str] = None):
        self._url = url or f"sqlite:///{default_db_path()}"
        engine_kwargs = {"connect_args": {"check_same_thread": False}}
        if ":memory:" in self._url:
            # 内存库必须用 StaticPool，让所有连接共享同一份内存数据
            engine_kwargs["poolclass"] = StaticPool
        self.engine = create_engine(self._url, **engine_kwargs)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_all(self) -> None:
        MobileBase.metadata.create_all(self.engine)

    def drop_all(self) -> None:
        MobileBase.metadata.drop_all(self.engine)

    def session(self):
        return self.SessionLocal()

    @classmethod
    def in_memory(cls) -> "MobileDB":
        """内存数据库（测试用）。"""
        db = cls(url="sqlite:///:memory:")
        db.create_all()
        return db

    @classmethod
    def file_based(cls) -> "MobileDB":
        """默认文件数据库，建表就绪。"""
        db = cls()
        db.create_all()
        return db
