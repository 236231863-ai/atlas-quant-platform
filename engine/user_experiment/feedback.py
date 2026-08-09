"""user_experiment.feedback - 真实用户反馈问卷（v4.9 P3 → v4.9.1 P1 升级为 4 问）。

问卷（任务书 v4.9.1 P1 ②）：
  Q1 你为什么使用 Atlas？        （使用原因）
  Q2 如果 Atlas 消失，会不会不方便？（不可替代性验证，重点）
  Q3 你可能为什么停止使用 Atlas？  （流失原因）
  Q4 如果提供高级服务，愿意支付？  （付费意愿）

数据标记 REAL_USER（真实用户），禁止与模拟混用。
存储：~/.atlas/feedback_v49.jsonl
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# Q1 使用原因（新 6 项 + 旧项兼容）
USE_REASONS = (
    "防止忘记兑奖", "自动查看中奖", "管理彩票投入", "查看历史购买",
    "数据分析", "其他",
    "自动提醒", "自动兑奖", "管理投入", "查看历史",  # 旧项兼容
)
Q1_REASONS = ("防止忘记兑奖", "自动查看中奖", "管理彩票投入",
              "查看历史购买", "数据分析", "其他")

# Q2 不可替代性（重点指标）
INDISPENSABLE_REASONS = (
    "会，因为怕忘记兑奖", "会，因为需要管理彩票记录", "会，因为需要历史资产分析",
    "不会，微信搜索开奖即可", "不会，没有明显价值",
)

# Q3 流失原因（新 6 项 + 旧项兼容）
UNINSTALL_REASONS = (
    "不买彩票了", "输入彩票麻烦", "提醒没有价值", "数据不可信", "微信已经够用", "其他",
    "没必要", "操作复杂", "没中奖", "提醒无用", "数据问题",  # 旧项兼容
)
Q3_UNINSTALL_REASONS = ("不买彩票了", "输入彩票麻烦", "提醒没有价值",
                        "数据不可信", "微信已经够用", "其他")

# Q4 付费意愿
PAY_LEVELS = ("不愿意", "3元/月", "6元/月", "9元/月", "12元/月")


@dataclass
class UserFeedback:
    """一条真实用户反馈（4 问）。"""

    user_id: str
    use_reason: str
    uninstall_reason: str = ""
    indispensable_reason: str = ""  # Q2
    pay_level: str = ""             # Q4
    experiment_id: str = "real_users"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


class UserFeedbackSurvey:
    """真实用户反馈问卷采集与统计（4 问）。"""

    def __init__(self, storage_dir: Optional[str] = None):
        self._dir = (storage_dir
                     or os.environ.get("ATLAS_STORAGE_DIR")
                     or os.path.join(os.path.expanduser("~"), ".atlas"))
        self._path = os.path.join(self._dir, "feedback_v49.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def submit(self, user_id: str, use_reason: str,
               uninstall_reason: str = "",
               experiment_id: str = "real_users") -> Optional[UserFeedback]:
        """旧版 2 问提交（兼容 P3 调用方）。内部转为完整 4 问记录。"""
        return self.submit_full(user_id=user_id, use_reason=use_reason,
                                uninstall_reason=uninstall_reason,
                                experiment_id=experiment_id)

    def submit_full(self, user_id: str, use_reason: str,
                    indispensable_reason: str = "",
                    uninstall_reason: str = "",
                    pay_level: str = "",
                    experiment_id: str = "real_users") -> Optional[UserFeedback]:
        """完整 4 问提交（真实用户专用，非空必填项校验）。"""
        if use_reason not in USE_REASONS:
            return None
        if indispensable_reason and indispensable_reason not in INDISPENSABLE_REASONS:
            return None
        if uninstall_reason and uninstall_reason not in UNINSTALL_REASONS:
            return None
        if pay_level and pay_level not in PAY_LEVELS:
            return None
        fb = UserFeedback(user_id=user_id, use_reason=use_reason,
                          indispensable_reason=indispensable_reason,
                          uninstall_reason=uninstall_reason,
                          pay_level=pay_level,
                          experiment_id=experiment_id)
        try:
            os.makedirs(self._dir, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(json.dumps(fb.to_dict(), ensure_ascii=False) + "\n")
        except OSError:
            pass
        return fb

    def all(self) -> List[UserFeedback]:
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
                        out.append(UserFeedback(**json.loads(line)))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            return []
        return out

    def count(self) -> int:
        return len(self.all())

    def distribution(self, field_name: str) -> Dict[str, int]:
        """统计某字段分布（use_reason / indispensable_reason / uninstall_reason / pay_level）。"""
        out: Dict[str, int] = {}
        for fb in self.all():
            val = getattr(fb, field_name, "")
            if val:
                out[val] = out.get(val, 0) + 1
        return out

    def top_use_reason(self) -> str:
        d = self.distribution("use_reason")
        return max(d, key=d.get) if d else "（暂无反馈）"

    def top_indispensable_reason(self) -> str:
        d = self.distribution("indispensable_reason")
        return max(d, key=d.get) if d else "（暂无反馈）"

    def top_uninstall_reason(self) -> str:
        d = self.distribution("uninstall_reason")
        return max(d, key=d.get) if d else "（暂无反馈）"

    def pay_willing_rate(self) -> float:
        """付费意愿 = 选"3元/月"及以上人数 / 已作答付费意愿人数（默认 0）。"""
        d = self.distribution("pay_level")
        answered = sum(d.values())
        if answered == 0:
            return 0.0
        willing = sum(v for k, v in d.items() if k != "不愿意")
        return willing / answered

    def summary(self) -> dict:
        return {
            "total": self.count(),
            "use_reasons": self.distribution("use_reason"),
            "indispensable_reasons": self.distribution("indispensable_reason"),
            "uninstall_reasons": self.distribution("uninstall_reason"),
            "pay_levels": self.distribution("pay_level"),
            "top_use": self.top_use_reason(),
            "top_indispensable": self.top_indispensable_reason(),
            "top_uninstall": self.top_uninstall_reason(),
            "pay_willing_rate": round(self.pay_willing_rate(), 4),
        }

    def clear(self) -> None:
        try:
            if os.path.exists(self._path):
                os.remove(self._path)
        except OSError:
            pass
