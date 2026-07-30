"""Help Center - user assistance, FAQ, diagnostics, support."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class HelpArticle: article_id:str; title:str; category:str; content:str=""; def to_dict(self):return {"id":self.article_id,"title":self.title}

class HelpCenter:
    def __init__(self): self._articles={}; self._register_defaults()
    def _register_defaults(self):
        for a in [HelpArticle("getting_started","Quick Start","guide"),HelpArticle("faq_install","Installation FAQ","faq"),
            HelpArticle("faq_analysis","Analysis FAQ","faq"),HelpArticle("troubleshoot","Troubleshooting","support")]:
            self._articles[a.article_id]=a
    def search(self,q): return [a for a in self._articles.values() if q.lower() in a.title.lower()]
    def get_by_category(self,c): return [a for a in self._articles.values() if a.category==c]
    def export_logs(self): return "Log export complete"
    def contact_support(self,msg): return f"Support request submitted: {msg}"
    def count(self): return len(self._articles)
