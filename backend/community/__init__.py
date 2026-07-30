"""Strategy Community - sharing and collaboration platform."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

@dataclass
class StrategyPost: id: str; creator: str; strategy: str; description: str; backtest_summary: str=""; created_at: str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat()); def to_dict(self): return asdict(self)
@dataclass
class StrategyComment: id: str; post_id: str; author: str; content: str; created_at: str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat()); def to_dict(self): return asdict(self)

class StrategyCommunity:
    def __init__(self): self._posts: Dict[str,StrategyPost]={}; self._comments: List[StrategyComment]=[]
    def publish(self, post: StrategyPost): self._posts[post.id]=post; return post
    def comment(self, comment: StrategyComment): self._comments.append(comment); return comment
    def get_post(self, pid: str) -> Optional[StrategyPost]: return self._posts.get(pid)
    def list_posts(self) -> List[StrategyPost]: return list(self._posts.values())
    def get_comments(self, post_id: str) -> List[StrategyComment]:
        return [c for c in self._comments if c.post_id==post_id]
    def count_posts(self) -> int: return len(self._posts)
