"""data_center_v2.updater - 开奖数据增量更新器（v4.3.1）。

解决「开奖信息不实时更新」：桌面启动时静默拉取官方最新开奖，
与本地数据按期号合并去重，写回用户缓存目录 ~/.atlas/raw/。

设计原则：
  - 静默失败：无网/API 异常不影响软件启动与已有数据
  - 限频：24h 内只更新一次（meta 文件记录）
  - 用户缓存优先：data_loader 优先读 ~/.atlas/raw/，回退内置
  - 只增量：不覆盖本地期号，只追加更新的期
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional

# 官方体彩 API（与 sources.APIDatasource 一致）
from engine.data_center_v2.sources import APIDatasource, CSVDatasource

DEFAULT_MAX_AGE_HOURS = 24


class IncrementalUpdater:
    """开奖数据增量更新器。"""

    def __init__(self, lottery: str = "dlt", storage_dir: Optional[str] = None):
        self.lottery = lottery
        self.storage_dir = storage_dir or os.path.join(os.path.expanduser("~"), ".atlas")
        self.raw_dir = os.path.join(self.storage_dir, "raw")
        self.meta_path = os.path.join(self.storage_dir, f"data_last_update_{lottery}.json")

    # ---------- 路径 ----------
    def cache_path(self) -> str:
        """用户缓存 CSV 路径。"""
        return os.path.join(self.raw_dir, f"{self.lottery}_history.csv")

    def _last_update(self) -> Optional[str]:
        if not os.path.exists(self.meta_path):
            return None
        try:
            with open(self.meta_path, encoding="utf-8") as f:
                return json.load(f).get("updated_at")
        except (json.JSONDecodeError, OSError):
            return None

    def _mark_updated(self, total: int, added: int) -> None:
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            with open(self.meta_path, "w", encoding="utf-8") as f:
                json.dump({
                    "lottery": self.lottery,
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                    "total": total,
                    "added": added,
                }, f, ensure_ascii=False)
        except OSError:
            pass

    def should_update(self, max_age_hours: int = DEFAULT_MAX_AGE_HOURS) -> bool:
        """24h 内是否已更新过（限频）。"""
        last = self._last_update()
        if not last:
            return True
        try:
            dt = datetime.fromisoformat(last)
            return datetime.now() - dt > timedelta(hours=max_age_hours)
        except ValueError:
            return True

    # ---------- 读写本地 ----------
    def load_local(self) -> List[dict]:
        """读取用户缓存（若存在）为 dict 列表。"""
        path = self.cache_path()
        if not os.path.exists(path):
            return []
        out = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    num = (row.get("issue") or "").strip()
                    if not num:
                        continue
                    out.append({
                        "issue": num,
                        "date": (row.get("date") or "").strip(),
                        "numbers": (row.get("numbers") or "").strip(),
                        "pool": (row.get("pool") or "").strip(),
                    })
        except OSError:
            return []
        return out

    def save_local(self, rows: List[dict]) -> int:
        """写回用户缓存 CSV（统一格式 issue,date,numbers,pool）。"""
        os.makedirs(self.raw_dir, exist_ok=True)
        with open(self.cache_path(), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["issue", "date", "numbers", "pool"])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        return len(rows)

    @staticmethod
    def _merge(local: List[dict], remote: List[dict]) -> List[dict]:
        """按期号去重合并（远程新期追加），按期号排序。"""
        by_issue: dict = {r["issue"]: r for r in local}
        for r in remote:
            by_issue[r["issue"]] = r  # 远程覆盖（奖池可能更新）
        merged = sorted(by_issue.values(), key=lambda r: int(r["issue"]))
        return merged

    def _load_builtin(self) -> List[dict]:
        """读取内置历史数据作为首次更新的 base（避免丢历史）。"""
        candidates = []
        base = getattr(sys, "_MEIPASS", None)
        if base:
            candidates.append(os.path.join(base, "data", "raw", f"{self.lottery}_history.csv"))
        candidates.append(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "raw", f"{self.lottery}_history.csv"))
        for p in candidates:
            if not os.path.exists(p):
                continue
            try:
                recs = CSVDatasource(p, lottery=self.lottery).load()
                return [{
                    "issue": str(r.number), "date": r.draw_date,
                    "numbers": " ".join(f"{n:02d}" for n in r.front) + "|" +
                               " ".join(f"{n:02d}" for n in r.back),
                    "pool": f"{r.pool:.2f}",
                } for r in recs]
            except Exception:
                continue
        return []

    # ---------- 更新 ----------
    def update(self, force: bool = False, pages: int = 1) -> dict:
        """增量更新：拉取官方最近开奖 → 合并 → 写缓存。

        返回 {updated, added, total, error}。任何异常静默降级（error 记录）。
        """
        if not force and not self.should_update():
            return {"updated": False, "added": 0, "total": len(self.load_local()),
                    "error": None, "reason": "within_age"}
        try:
            local = self.load_local()
            if not local:
                local = self._load_builtin()  # 首次以内置历史为 base，避免丢历史
            local_issues = {r["issue"] for r in local}
            src = APIDatasource(lottery=self.lottery, pages=pages, page_size=30)
            remote_records = src.load()
            remote = []
            for rec in remote_records:
                numbers = " ".join(f"{n:02d}" for n in rec.front) + "|" + \
                          " ".join(f"{n:02d}" for n in rec.back)
                remote.append({
                    "issue": str(rec.number), "date": rec.draw_date,
                    "numbers": numbers,
                    "pool": f"{rec.pool:.2f}",
                })
            if not remote:
                return {"updated": False, "added": 0, "total": len(local),
                        "error": "api_empty", "reason": "no_remote_data"}
            merged = self._merge(local, remote)
            added = len([r for r in merged if r["issue"] not in local_issues])
            self.save_local(merged)
            self._mark_updated(len(merged), added)
            return {"updated": True, "added": added, "total": len(merged),
                    "error": None}
        except Exception as e:  # noqa: BLE001 静默降级
            return {"updated": False, "added": 0, "total": len(self.load_local()),
                    "error": str(e), "reason": "exception"}


def maybe_update_draws(lottery: str = "dlt", force: bool = False) -> dict:
    """便捷函数：尝试增量更新（供启动时后台调用）。"""
    return IncrementalUpdater(lottery).update(force=force)


def latest_issues(lottery: str = "dlt") -> List[str]:
    """当前用户缓存的最新期号（供调试/测试）。"""
    rows = IncrementalUpdater(lottery).load_local()
    return [r["issue"] for r in rows][-5:]
