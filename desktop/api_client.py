import json, urllib.request
from typing import Any, Dict, Optional

class DesktopAPIClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
    def _get(self, path):
        try:
            with urllib.request.urlopen(f"{self.base_url}{path}") as r:
                return json.loads(r.read().decode())
        except: return None
    def get_dashboard(self): return self._get("/dashboard/summary")
    def get_draws(self, lottery="dlt", limit=50): return self._get(f"/{lottery}/draws?limit={limit}")
    def get_stats(self, lottery="dlt"): return self._get(f"/{lottery}/statistics")
