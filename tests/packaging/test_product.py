"""Tests for Sprint FP1 Packaging."""
from __future__ import annotations
import pytest
from branding import Branding, ProductInfo
from launcher import DesktopLauncher
from installer import InstallerWizard
from first_run import FirstRunWizard
from help_center import HelpCenter
from updater import AutoUpdater

class TestBranding:
    def test_name(self):
        assert "Atlas" in Branding.get_app_name()
    def test_version(self):
        assert Branding.get_version()=="3.5.1"
class TestLauncher:
    def test_detect(self):
        l=DesktopLauncher()
        d=l.detect_environment()
        assert "os" in d
    def test_platforms(self):
        l=DesktopLauncher()
        assert len(l.get_supported_platforms())==3
class TestInstaller:
    def test_steps(self):
        i=InstallerWizard()
        s=i.next()
        assert s=="welcome"
    def test_progress(self):
        i=InstallerWizard()
        i.next()
        assert i.get_progress()>0
class TestFirstRun:
    def test_steps(self):
        f=FirstRunWizard()
        assert f.current()=="welcome"
    def test_complete(self):
        f=FirstRunWizard()
        [f.next() for _ in range(6)]
        assert f.is_completed()
class TestHelp:
    def test_search(self):
        h=HelpCenter()
        r=h.search("Quick")
        assert len(r)==1
    def test_categories(self):
        h=HelpCenter()
        assert len(h.get_by_category("faq"))>=1
class TestUpdater:
    def test_check(self):
        u=AutoUpdater()
        i=u.check_update()
        assert not i.update_available
    def test_version(self):
        u=AutoUpdater()
        assert u.get_current_version()=="3.5.1"
