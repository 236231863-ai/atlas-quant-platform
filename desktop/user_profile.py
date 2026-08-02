"""Atlas 本地用户档案与设置持久化。

将用户档案（用户名/语言/主题/首次运行标记）保存到用户主目录，
跨启动持久化。无服务器账户，纯本地。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Optional

APP_DIR_NAME = ".atlas"
PROFILE_FILE = "profile.json"


@dataclass
class UserProfile:
    """本地用户档案。"""

    username: str = "量化研究者"
    language: str = "zh-CN"
    theme: str = "light"
    first_run_completed: bool = False
    data_lottery: str = "dlt"
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)


def profile_dir() -> str:
    """用户档案目录：用户主目录/.atlas。"""
    home = os.path.expanduser("~")
    d = os.path.join(home, APP_DIR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def profile_path() -> str:
    return os.path.join(profile_dir(), PROFILE_FILE)


def load_profile() -> UserProfile:
    """加载用户档案；不存在则返回默认（首次运行）。"""
    p = profile_path()
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return UserProfile.from_dict(json.load(f))
        except (json.JSONDecodeError, OSError):
            pass
    return UserProfile()


def save_profile(profile: UserProfile) -> None:
    """保存用户档案。"""
    from datetime import datetime

    profile.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(profile_path(), "w", encoding="utf-8") as f:
        json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)


def is_first_run() -> bool:
    """是否首次运行（未完成引导）。"""
    return not load_profile().first_run_completed
