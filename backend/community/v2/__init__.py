"""Community Platform v2 - strategy sharing, publications, reputation."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

@dataclass
class CommunityPost:
    post_id:str
    author:str
    post_type:str="strategy"
    title:str=""
    content:str=""
    tags:List[str]=field(default_factory=list)
    rating:float=0.0
    forks:int=0
    def to_dict(self):
        return asdict(self)
@dataclass
class ResearchPublication:
    pub_id:str
    author:str
    pub_type:str="research_note"
    title:str=""
    abstract:str=""
    citations:int=0
    def to_dict(self):
        return asdict(self)

class CommunityPlatformV2:
    def __init__(self):
        self._posts: Dict[str, CommunityPost] = {}
        self._pubs: Dict[str, ResearchPublication] = {}
    def publish_post(self, post: CommunityPost):
        self._posts[post.post_id] = post
        return post
    def publish_research(self, pub: ResearchPublication):
        self._pubs[pub.pub_id] = pub
        return pub
    def fork_post(self, pid: str, new_author: str) -> Optional[CommunityPost]:
        orig = self._posts.get(pid)
        if not orig: return None
        new = CommunityPost(post_id=f"fork_{pid}_{new_author}", author=new_author, title=f"Fork of {orig.title}", content=orig.content)
        self._posts[new.post_id] = new; orig.forks += 1; return new
    def list_posts(self) -> List[CommunityPost]: return list(self._posts.values())
    def list_pubs(self) -> List[ResearchPublication]: return list(self._pubs.values())
    def count_posts(self) -> int: return len(self._posts)
