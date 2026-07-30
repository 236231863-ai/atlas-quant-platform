"""Atlas Quant Platform - Production Configuration.
Extends the base settings with environment-specific overrides.
"""
from __future__ import annotations
import os
from config.settings import AppSettings

class ProductionSettings(AppSettings):
    def __init__(self):
        super().__init__()
        self.environment = os.getenv("ATLAS_ENVIRONMENT", "production")
        if self.environment == "production":
            self.debug = False
            self.db.url = os.getenv("ATLAS_DB__URL", self.db.url)
            self.logging.level = os.getenv("ATLAS_LOG__LEVEL", "INFO")

def get_settings() -> AppSettings:
    env = os.getenv("ATLAS_ENVIRONMENT", "development")
    if env == "production":
        return ProductionSettings()
    return AppSettings()
