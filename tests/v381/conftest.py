"""v3.8.1 测试套件共享配置。"""
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (ROOT, os.path.join(ROOT, "desktop")):
    if p not in sys.path:
        sys.path.insert(0, p)
