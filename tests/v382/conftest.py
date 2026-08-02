"""v3.8.0 日期升级测试配置。"""
import os, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (ROOT, os.path.join(ROOT, "desktop")):
    if p not in sys.path:
        sys.path.insert(0, p)
