"""Tests for Runtime & Packaging."""
from __future__ import annotations
import pytest
from tools.launcher import ApplicationLauncher
from tools.packaging import DesktopPackager
from tools.web_starter import WebStarter
from tools.installer import Installer
from tools.config_wizard import ConfigWizard
from tools.first_run import FirstRunExperience
from tools.error_recovery import ErrorRecovery
from tools.release import ReleasePackage

class TestLauncher:
    def test_modes(self):
        l=ApplicationLauncher()
        assert len(l.MODES)==4
    def test_set(self):
        l=ApplicationLauncher()
        assert l.set_mode("web")
    def test_invalid(self):
        l=ApplicationLauncher()
        assert not l.set_mode("invalid")
class TestPackager:
    def test_configure(self):
        p=DesktopPackager()
        c=p.configure("Atlas","1.0","main.py")
        assert c["app_name"]=="Atlas"
class TestWeb:
    def test_start(self):
        w=WebStarter()
        assert "8000" in w.start()
class TestInstaller:
    def test_next(self):
        i=Installer()
        s=i.next_step()
        assert s=="welcome"
class TestWizard:
    def test_validate(self):
        w=ConfigWizard()
        assert w.validate()
class TestFirstRun:
    def test_steps(self):
        f=FirstRunExperience()
        assert f.current_step()=="welcome"
class TestRecovery:
    def test_diagnose(self):
        e=ErrorRecovery()
        d=e.diagnose()
        assert d["status"]=="ok"
class TestRelease:
    def test_build(self):
        r=ReleasePackage()
        r.build("1.0.0")
        assert len(r.list_artifacts())==1
