"""Mobile Preparation - React Native framework foundation."""
from __future__ import annotations
MOBILE_VERSION = "0.1.0"
PLATFORMS = ["iOS", "Android"]
API_LAYER = "Atlas API v3"
AUTH_METHOD = "JWT Token"
NOTIFICATION_TYPE = ["push", "email", "in_app"]

def get_mobile_config() -> Dict[str, Any]:
    return {"version": MOBILE_VERSION, "platforms": PLATFORMS, "api": API_LAYER, "auth": AUTH_METHOD, "notifications": NOTIFICATION_TYPE}
