"""Atlas Python SDK - client library for developers."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json, urllib.request

class AtlasClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api/v3"):
        self._api_key = api_key; self._base_url = base_url
    def _request(self, method: str, path: str, data: Optional[Dict]=None) -> Optional[Dict]:
        try:
            url = f"{self._base_url}{path}"
            headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
            req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers=headers, method=method)
            with urllib.request.urlopen(req) as r: return json.loads(r.read().decode())
        except: return None
    def analyze(self, lottery: str="dlt", mode: str="basic") -> Optional[Dict]:
        return self._request("POST", "/analyze", {"lottery_code": lottery, "mode": mode})
    def get_report(self, rid: str) -> Optional[Dict]:
        return self._request("GET", f"/report/{rid}")
