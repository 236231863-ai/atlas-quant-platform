"""user_experiment.events - 用户实验事件系统（v4.9 P1）。

验证 Sprint 基础设施：为每个用户分配 experiment_id，记录关键行为事件，
并支持里程碑（首次打开/首次保存/首次查看中奖）与 CSV 导出。

事件集（v4.9 P1 + v4.9.1 P1 扩展）：
  app_install              安装完成
  app_open                 打开应用
  onboarding_start         引导开始
  ticket_saved             保存彩票
  reminder_enabled         开启开奖提醒
  reminder_sent            发送开奖提醒
  draw_reminder_clicked    点击开奖提醒
  draw_checked             查看开奖结果
  draw_checked_after_reminder  收到提醒后查看开奖
  claim_checked            查看兑奖结果
  claim_completed          兑奖完成
  asset_viewed             查看资产
  report_viewed            查看报告
  weekly_report_viewed     查看周报
  premium_view             查看 Premium 页
  premium_click            点击付费意愿
  weekly_return            周回访（触发一次=本周活跃）
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# 实验事件集
EXPERIMENT_EVENTS = (
    "app_install", "app_open", "onboarding_start", "ticket_saved",
    "reminder_enabled", "reminder_sent", "draw_reminder_clicked",
    "draw_checked", "draw_checked_after_reminder", "claim_checked",
    "claim_completed", "asset_viewed", "report_viewed",
    "weekly_report_viewed", "premium_view", "premium_click",
    "weekly_return",
)

# 数据来源标记（v4.9 P3：禁止混合统计）
SOURCE_REAL = "REAL"              # 真实用户
SOURCE_SIMULATION = "SIMULATION"  # 模拟用户
SOURCE_DESKTOP_LEGACY = "desktop" # 旧版埋点（视为真实桌面使用）

# 里程碑：首次发生时间
MILESTONES = {
    "first_open_at": "app_open",
    "first_onboarding_at": "onboarding_start",
    "first_ticket_saved_at": "ticket_saved",
    "first_reminder_enabled_at": "reminder_enabled",
    "first_draw_checked_at": "draw_checked",
    "first_prize_checked_at": "claim_checked",
    "first_claim_completed_at": "claim_completed",
    "first_asset_viewed_at": "asset_viewed",
    "first_report_viewed_at": "report_viewed",
    "first_weekly_report_viewed_at": "weekly_report_viewed",
}


def normalize_source(source: str) -> str:
    """统一数据来源标记：REAL / SIMULATION（模块级，供各模块复用）。"""
    if not source:
        return SOURCE_REAL
    if source == SOURCE_SIMULATION:
        return SOURCE_SIMULATION
    return SOURCE_REAL  # desktop 及一切非 SIMULATION 视为真实使用


@dataclass
class ExperimentEvent:
    """一条实验事件。"""

    event_name: str
    experiment_id: str = "default"
    user_id: str = "default"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    source: str = "desktop"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_name": self.event_name,
            "experiment_id": self.experiment_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


class ExperimentTracker:
    """实验事件追踪器（jsonl 追加写 + CSV 导出）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "experiments_v49.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def record(self, event_name: str, user_id: str = "default",
               experiment_id: str = "default", source: str = "desktop",
               metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        """记录一条实验事件（非法事件名返回 None）。"""
        if event_name not in EXPERIMENT_EVENTS:
            return None
        ev = ExperimentEvent(event_name=event_name, user_id=user_id,
                             experiment_id=experiment_id, source=source,
                             metadata=metadata or {})
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return ev

    # ---- 快捷方法 ----
    def install(self, user_id: str, experiment_id: str = "default",
                metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("app_install", user_id, experiment_id, metadata=metadata)

    def open_app(self, user_id: str, experiment_id: str = "default",
                 metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("app_open", user_id, experiment_id, metadata=metadata)

    def save_ticket(self, user_id: str, experiment_id: str = "default",
                    metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("ticket_saved", user_id, experiment_id, metadata=metadata)

    def onboarding_start(self, user_id: str, experiment_id: str = "default",
                         metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("onboarding_start", user_id, experiment_id, metadata=metadata)

    def enable_reminder(self, user_id: str, experiment_id: str = "default",
                        metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("reminder_enabled", user_id, experiment_id, metadata=metadata)

    def reminder_sent(self, user_id: str, experiment_id: str = "default",
                      metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("reminder_sent", user_id, experiment_id, metadata=metadata)

    def reminder_click(self, user_id: str, experiment_id: str = "default",
                       metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("draw_reminder_clicked", user_id, experiment_id, metadata=metadata)

    def check_draw(self, user_id: str, experiment_id: str = "default",
                   metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("draw_checked", user_id, experiment_id, metadata=metadata)

    def checked_after_reminder(self, user_id: str, experiment_id: str = "default",
                               metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("draw_checked_after_reminder", user_id, experiment_id, metadata=metadata)

    def check_claim(self, user_id: str, experiment_id: str = "default",
                    metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("claim_checked", user_id, experiment_id, metadata=metadata)

    def claim_completed(self, user_id: str, experiment_id: str = "default",
                        metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("claim_completed", user_id, experiment_id, metadata=metadata)

    def view_asset(self, user_id: str, experiment_id: str = "default",
                   metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("asset_viewed", user_id, experiment_id, metadata=metadata)

    def view_report(self, user_id: str, experiment_id: str = "default",
                    metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("report_viewed", user_id, experiment_id, metadata=metadata)

    def view_weekly_report(self, user_id: str, experiment_id: str = "default",
                           metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("weekly_report_viewed", user_id, experiment_id, metadata=metadata)

    def premium_view(self, user_id: str, experiment_id: str = "default",
                     metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("premium_view", user_id, experiment_id, metadata=metadata)

    def premium_click(self, user_id: str, experiment_id: str = "default",
                      metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("premium_click", user_id, experiment_id, metadata=metadata)

    def weekly_return(self, user_id: str, experiment_id: str = "default",
                      metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("weekly_return", user_id, experiment_id, metadata=metadata)

    # ---- 读取 ----
    def all(self) -> List[ExperimentEvent]:
        if not os.path.exists(self._path):
            return []
        out = []
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        out.append(ExperimentEvent(**d))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def count(self, event_name: str, experiment_id: Optional[str] = None) -> int:
        evs = self.all()
        if experiment_id:
            evs = [e for e in evs if e.experiment_id == experiment_id]
        return sum(1 for e in evs if e.event_name == event_name)

    def users(self, event_name: Optional[str] = None,
              experiment_id: Optional[str] = None) -> List[str]:
        """触达某事件（或全部事件）的用户集合。"""
        evs = self.all()
        if experiment_id:
            evs = [e for e in evs if e.experiment_id == experiment_id]
        if event_name:
            evs = [e for e in evs if e.event_name == event_name]
        return sorted({e.user_id for e in evs})

    def milestones(self, user_id: str,
                   experiment_id: Optional[str] = None) -> Dict[str, Optional[str]]:
        """用户里程碑（首次发生时间）。"""
        evs = [e for e in self.all() if e.user_id == user_id]
        if experiment_id:
            evs = [e for e in evs if e.experiment_id == experiment_id]
        out: Dict[str, Optional[str]] = {k: None for k in MILESTONES}
        for name, event_key in MILESTONES.items():
            times = [e.timestamp for e in evs if e.event_name == event_key]
            if times:
                out[name] = min(times)
        return out

    # ---- CSV 导出 ----
    def export_csv(self, path: Optional[str] = None,
                   experiment_id: Optional[str] = None) -> str:
        """导出全部事件为 CSV，返回文件路径。"""
        out_path = path or os.path.join(self._dir, "experiments_v49_export.csv")
        evs = self.all()
        if experiment_id:
            evs = [e for e in evs if e.experiment_id == experiment_id]
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "experiment_id", "user_id", "event_name", "timestamp",
                "source", "metadata",
            ])
            writer.writeheader()
            for e in evs:
                writer.writerow({
                    "experiment_id": e.experiment_id,
                    "user_id": e.user_id,
                    "event_name": e.event_name,
                    "timestamp": e.timestamp,
                    "source": e.source,
                    "metadata": json.dumps(e.metadata, ensure_ascii=False),
                })
        return out_path

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass

    # ---- 数据来源标记（v4.9 P3）----
    @staticmethod
    def normalize_source(source: str) -> str:
        """统一数据来源标记：REAL / SIMULATION。"""
        return normalize_source(source)

    def real_events(self, experiment_id: Optional[str] = None) -> List[ExperimentEvent]:
        """仅真实用户事件（REAL，禁止混合 SIMULATION）。"""
        return [e for e in self.all()
                if self.normalize_source(e.source) == SOURCE_REAL
                and (experiment_id is None or e.experiment_id == experiment_id)]

    def simulation_events(self, experiment_id: Optional[str] = None) -> List[ExperimentEvent]:
        """仅模拟用户事件（SIMULATION）。"""
        return [e for e in self.all()
                if self.normalize_source(e.source) == SOURCE_SIMULATION
                and (experiment_id is None or e.experiment_id == experiment_id)]

    def import_real_events(self, jsonl_path: str,
                           experiment_id: str = "real_users") -> int:
        """从真实埋点文件（analytics_v46 / events_v43 jsonl）导入真实用户事件。

        事件名映射：与实验事件集对齐；不认识的旧事件名忽略。
        全部标记 SOURCE_REAL，写入实验存储（不去重，追加真实记录）。
        返回导入条数。
        """
        imported = 0
        if not os.path.exists(jsonl_path):
            return 0
        alias = {
            "app_opened": "app_open",
            "ticket_checked": "claim_checked",
            "reminder_clicked": "draw_reminder_clicked",
            "onboarding_complete": "onboarding_start",
            "draw_checked": "draw_checked",
            "asset_viewed": "asset_viewed",
            "weekly_report_opened": "weekly_report_viewed",
        }
        try:
            with open(jsonl_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                    except (json.JSONDecodeError, TypeError):
                        continue
                    name = alias.get(d.get("event_name"), d.get("event_name"))
                    if name not in EXPERIMENT_EVENTS:
                        continue
                    ev = ExperimentEvent(
                        event_name=name,
                        experiment_id=experiment_id,
                        user_id=d.get("user_id", "default"),
                        timestamp=d.get("timestamp", ""),
                        source=SOURCE_REAL,
                        metadata=d.get("metadata") or {},
                    )
                    with open(self._path, "a", encoding="utf-8") as out:
                        out.write(json.dumps(ev.to_dict(), ensure_ascii=False) + "\n")
                    imported += 1
        except OSError:
            return 0
        return imported
