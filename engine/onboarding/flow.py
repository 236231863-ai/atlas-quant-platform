"""onboarding - 首次成功体验流程（FirstSuccessFlow）。

目标：首次用户 5 分钟内完成第一次分析，获得"我能用、它有用"的成就感。

流程：
  欢迎 → 数据介绍 → 自动生成第一份报告 → 展示分析结果 → 保存历史
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional


@dataclass
class FirstSuccessFlow:
    """首次成功引导流程（状态机）。

    steps 按序推进，每步可注入回调（on_step），
    UI 层监听状态驱动界面。
    """

    lottery: str = "dlt"
    steps: List[str] = field(default_factory=lambda: [
        "welcome",
        "data_intro",
        "generate_report",
        "show_result",
        "save_history",
    ])
    current: int = 0
    completed: bool = False
    result: dict = field(default_factory=dict)
    _callbacks: Dict[str, Callable] = field(default_factory=dict)

    # ---- 步骤定义 ----
    @property
    def current_step(self) -> str:
        if self.current < len(self.steps):
            return self.steps[self.current]
        return "done"

    @property
    def progress(self) -> float:
        return self.current / len(self.steps)

    def register(self, step: str, callback: Callable) -> None:
        """注册步骤回调（返回 dict 写入 result）。"""
        self._callbacks[step] = callback

    def next(self) -> str:
        """推进到下一步，执行该步回调（若有）。"""
        if self.completed:
            return "done"
        step = self.steps[self.current]
        cb = self._callbacks.get(step)
        if cb:
            try:
                self.result[step] = cb()
            except Exception as e:
                self.result[step] = {"error": str(e)}
        self.current += 1
        if self.current >= len(self.steps):
            self.completed = True
            return "done"
        return self.current_step

    def run_all(self) -> dict:
        """自动跑完全流程。"""
        while not self.completed:
            self.next()
        return self.result

    def first_report(self) -> Optional[dict]:
        """获取自动生成的第一份报告。"""
        return self.result.get("generate_report")

    def summary(self) -> dict:
        return {
            "lottery": self.lottery,
            "completed": self.completed,
            "current_step": self.current_step,
            "progress": self.progress,
            "steps_done": self.current,
            "steps_total": len(self.steps),
        }


# ---------------- 便捷工厂 ----------------
def default_report_generator(draws: list, lottery_name: str = "大乐透") -> Callable:
    """生成默认的第一份报告回调。"""

    def _gen() -> dict:
        total = len(draws)
        if total == 0:
            return {"title": "暂无数据", "lines": ["请先导入数据"]}
        last = draws[-1]
        return {
            "title": f"我的第一份 {lottery_name} 分析报告",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_draws": total,
            "latest_issue": last.number,
            "latest_date": last.draw_date,
            "latest_numbers": f"{last.format_front()} + {last.format_back()}",
            "lines": [
                f"· 数据范围：{draws[0].draw_date} ~ {last.draw_date}，共 {total} 期",
                f"· 最新期号：{last.number}（{last.draw_date}）",
                f"· 最新号码：{last.format_front()} + {last.format_back()}",
            ],
            "disclaimer": "彩票开奖为随机事件，本报告仅供研究参考。",
        }

    return _gen


def default_history_saver(history_dir: Optional[str] = None) -> Callable:
    """保存报告历史的回调。"""
    import json

    def _save(report: Optional[dict]) -> dict:
        if not report or not report.get("title"):
            return {"saved": False}
        base = history_dir or os.path.join(os.path.expanduser("~"), ".atlas", "history")
        os.makedirs(base, exist_ok=True)
        # 文件名含微秒，避免同一秒多次保存冲突
        fname = f"report_{datetime.now():%Y%m%d_%H%M%S_%f}.json"
        path = os.path.join(base, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return {"saved": True, "path": path}

    return _save
