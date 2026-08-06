"""user_experiment.simulator - 真实数据模拟环境（v4.9 P1）。

可导入测试用户（数量 / 行为概率），生成用户行为路径（事件流），
并输出漏斗 + 留存曲线 + Q1-Q4 指标。用于在真实用户数据到来前，
验证实验系统采集/计算正确，并建立基准预期。

用途边界（诚实声明）：
  本模拟器输出的是「基于假设概率的合成数据」，用于验证实验管道，
  不能替代真实用户数据。真实用户验证需 P6 Red Team 与后续实盘采集。
"""
from __future__ import annotations

import csv
import json
import os
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from engine.user_experiment.events import ExperimentEvent, ExperimentTracker
from engine.user_experiment.funnel import ExperimentFunnel, ExperimentFunnelReport
from engine.user_experiment.metrics import ValidationMetrics, ValidationMetricsBuilder
from engine.user_experiment.retention import (
    ExperimentRetention,
    ExperimentRetentionBuilder,
)


@dataclass
class SimConfig:
    """模拟行为概率。"""

    install_complete: float = 0.80      # 安装后首次打开
    first_save: float = 0.60            # 安装用户中保存首张票（≥50% 目标）
    reminder_click: float = 0.40        # 保存后点开奖提醒
    claim_check: float = 0.55           # 提醒后查兑奖
    report_view: float = 0.70           # 兑奖后看报告
    daily_open: float = 0.35            # 每日再次打开概率（D1 驱动）
    premium_view_rate: float = 0.25     # 打开中查看 Premium 页
    premium_click_rate: float = 0.15    # 查看后点击付费意愿
    days: int = 7                       # 模拟天数


@dataclass
class SimUser:
    """一个模拟用户。"""

    user_id: str = "default"
    installed: bool = False
    opened: bool = False
    saved: bool = False
    reminded: bool = False
    claimed: bool = False
    reviewed: bool = False
    premium_viewed: bool = False
    premium_clicked: bool = False

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class UserBehaviorSimulator:
    """真实数据模拟环境：导入用户数 + 生成行为路径 + 事件流。"""

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._day0 = date(2026, 8, 3)  # 模拟起点（周一）

    def _ts(self, d: date, hour: int = 20) -> str:
        return datetime(d.year, d.month, d.day, hour, self._rng.randint(0, 59)).isoformat(timespec="seconds")

    # ---- 导入用户 ----
    def import_users(self, user_ids: List[str]) -> List[SimUser]:
        """导入测试用户（初始状态）。"""
        return [SimUser(user_id=str(uid)) for uid in user_ids]

    def import_csv(self, path: str) -> List[SimUser]:
        """从 CSV 导入测试用户（列: user_id, 可选 install/save 等 0/1）。"""
        users = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                uid = row.get("user_id", "").strip()
                if not uid:
                    continue
                u = SimUser(user_id=uid)
                for key in ("installed", "opened", "saved", "reminded",
                            "claimed", "reviewed", "premium_viewed",
                            "premium_clicked"):
                    v = row.get(key, "").strip()
                    if v:
                        setattr(u, key, v in ("1", "true", "True", "yes"))
                users.append(u)
        return users

    # ---- 行为路径生成 ----
    def generate_path(self, user: SimUser, config: SimConfig,
                      experiment_id: str = "default") -> List[ExperimentEvent]:
        """按概率生成一个用户 7 天的行为路径（返回事件流）。"""
        events: List[ExperimentEvent] = []
        # D0：安装（强制）
        events.append(ExperimentEvent(
            event_name="app_install", experiment_id=experiment_id,
            user_id=user.user_id, timestamp=self._ts(self._day0, 12)))
        user.installed = True

        if self._rng.random() >= config.install_complete:
            return events  # 安装未打开，流失

        events.append(ExperimentEvent(
            event_name="app_open", experiment_id=experiment_id,
            user_id=user.user_id, timestamp=self._ts(self._day0, 12)))
        user.opened = True

        # 首次保存
        if self._rng.random() < config.first_save:
            events.append(ExperimentEvent(
                event_name="ticket_saved", experiment_id=experiment_id,
                user_id=user.user_id, timestamp=self._ts(self._day0, 19)))
            user.saved = True
            # 保存后提醒点击
            if self._rng.random() < config.reminder_click:
                events.append(ExperimentEvent(
                    event_name="draw_reminder_clicked", experiment_id=experiment_id,
                    user_id=user.user_id, timestamp=self._ts(self._day0, 20)))
                user.reminded = True
                # 开奖后查兑奖
                if self._rng.random() < config.claim_check:
                    events.append(ExperimentEvent(
                        event_name="claim_checked", experiment_id=experiment_id,
                        user_id=user.user_id, timestamp=self._ts(self._day0, 21)))
                    user.claimed = True
                    # 看报告
                    if self._rng.random() < config.report_view:
                        events.append(ExperimentEvent(
                            event_name="report_viewed", experiment_id=experiment_id,
                            user_id=user.user_id, timestamp=self._ts(self._day0, 21)))
                        user.reviewed = True

        # D1-D7 每日打开（open 计入留存）
        for offset in range(1, config.days + 1):
            d = self._day0 + timedelta(days=offset)
            if self._rng.random() < config.daily_open:
                events.append(ExperimentEvent(
                    event_name="app_open", experiment_id=experiment_id,
                    user_id=user.user_id, timestamp=self._ts(d, 12)))
                # Premium 兴趣
                if user.saved and self._rng.random() < config.premium_view_rate:
                    events.append(ExperimentEvent(
                        event_name="premium_view", experiment_id=experiment_id,
                        user_id=user.user_id, timestamp=self._ts(d, 12)))
                    user.premium_viewed = True
                    if self._rng.random() < config.premium_click_rate:
                        events.append(ExperimentEvent(
                            event_name="premium_click", experiment_id=experiment_id,
                            user_id=user.user_id, timestamp=self._ts(d, 12)))
                        user.premium_clicked = True
                # 周回访（周六/周日出现=每周回来）
                if offset in (6, 7):
                    events.append(ExperimentEvent(
                        event_name="weekly_return", experiment_id=experiment_id,
                        user_id=user.user_id, timestamp=self._ts(d, 12)))
        return events

    # ---- 全流程 ----
    def run(self, users: List[SimUser], config: Optional[SimConfig] = None,
            experiment_id: str = "default") -> dict:
        """生成全部用户行为路径并写回 tracker，返回指标汇总。

        返回 dict：{events, funnel, retention, metrics, users}
        """
        config = config or SimConfig()
        tracker = ExperimentTracker()
        all_events: List[ExperimentEvent] = []
        for u in users:
            all_events.extend(self.generate_path(u, config, experiment_id))
            # 写入持久化（模拟真实采集）
            for e in all_events:
                tracker.record(e.event_name, e.user_id, e.experiment_id,
                               e.source, e.metadata)

        funnel = ExperimentFunnel.build(all_events)
        retention = ExperimentRetentionBuilder.build(all_events)
        metrics = ValidationMetricsBuilder.build(all_events, retention=retention,
                                                 funnel=funnel)
        return {
            "events": all_events,
            "funnel": funnel,
            "retention": retention,
            "metrics": metrics,
            "users": users,
        }

    # ---- 导出 ----
    def export_paths(self, out_dir: str, result: dict) -> List[str]:
        """导出事件路径 CSV + 用户画像 CSV + 指标 JSON。"""
        os.makedirs(out_dir, exist_ok=True)
        paths = []
        # 事件流
        ev_path = os.path.join(out_dir, "user_paths.csv")
        with open(ev_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "event_name", "timestamp", "experiment_id"])
            for e in result["events"]:
                writer.writerow([e.user_id, e.event_name, e.timestamp, e.experiment_id])
        paths.append(ev_path)
        # 用户画像
        us_path = os.path.join(out_dir, "user_profiles.csv")
        with open(us_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=SimUser().to_dict().keys())
            writer.writeheader()
            for u in result["users"]:
                writer.writerow(u.to_dict())
        paths.append(us_path)
        # 指标 JSON
        m_path = os.path.join(out_dir, "validation_metrics.json")
        with open(m_path, "w", encoding="utf-8") as f:
            json.dump(result["metrics"].to_dict(), f, ensure_ascii=False, indent=2)
        paths.append(m_path)
        return paths
