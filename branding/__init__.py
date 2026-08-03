"""Branding - product identity, logos, version info."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ProductInfo:
    name: str = "Atlas Quant Platform"
    version: str = "4.2.0"
    edition: str = "Community"
    build: str = "20260730"
    license: str = "MIT"
    description: str = "Quantitative Research Platform"

class Branding:
    LOGO_SIZES = [16,32,48,64,128,256,512]; FORMATS = ["svg","png","ico","icns"]
    @staticmethod
    def get_app_name():
        return ProductInfo.name
    @staticmethod
    def get_version():
        return ProductInfo.version
    @staticmethod
    def get_edition():
        return ProductInfo.edition
