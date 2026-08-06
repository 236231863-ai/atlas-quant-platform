"""user_experiment.events - 用户实验事件系统（v4.9 P1）。

验证 Sprint 基础设施：为每个用户分配 experiment_id，记录关键行为事件，
并支持里程碑（首次打开/首次保存/首次查看中奖）与 CSV 导出。

事件集（v4.9 P1 验收口径）：
  app_install            安装完成
  app_open               打开应用
  ticket_saved           保存彩票
  draw_reminder_clicked  点击开奖提醒
  claim_checked          查看兑奖结果
  report_viewed          查看报告
  premium_view           查看 Premium 页
  premium_click          点击付费意愿
  weekly_return          周回访（触发一次=本周活跃）
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
    "app_install", "app_open", "ticket_saved", "draw_reminder_clicked",
    "claim_checked", "report_viewed", "premium_view", "premium_click",
    "weekly_return",
)

# 里程碑：首次发生时间
MILESTONES = {
    "first_open_at": "app_open",
    "first_ticket_saved_at": "ticket_saved",
    "first_prize_checked_at": "claim_checked",
    "first_report_viewed_at": "report_viewed",
}


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

    def reminder_click(self, user_id: str, experiment_id: str = "default",
                       metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("draw_reminder_clicked", user_id, experiment_id, metadata=metadata)

    def check_claim(self, user_id: str, experiment_id: str = "default",
                    metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("claim_checked", user_id, experiment_id, metadata=metadata)

    def view_report(self, user_id: str, experiment_id: str = "default",
                    metadata: Optional[dict] = None) -> Optional[ExperimentEvent]:
        return self.record("report_viewed", user_id, experiment_id, metadata=metadata)

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
