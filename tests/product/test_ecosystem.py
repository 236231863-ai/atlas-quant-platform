"""Tests for Ecosystem Platform."""
from __future__ import annotations
import pytest
from backend.open_api import APIGateway
from engine.plugin_market import PluginRegistry, PluginManifest
from backend.community.marketplace import StrategyMarketplace, StrategyAsset
from data_market import DataMarketplace, DataAsset
from engine.agent_market import AgentMarketplace, AgentAsset
from backend.enterprise import EnterpriseWorkspace, Organization, Team
from engine.dashboard.v9 import EcosystemDashboard, EcosystemData

class TestAPI:
    def test_create_key(self): g=APIGateway(); k=g.create_key("u1"); assert k.user_id=="u1"
    def test_validate(self): g=APIGateway(); k=g.create_key("u1"); assert g.validate_key(k.key_hash)
    def test_count(self): g=APIGateway(); g.create_key("u1"); g.create_key("u2"); assert g.count_keys()==2
class TestPlugin:
    def test_register(self): r=PluginRegistry(); r.register(PluginManifest("p1","Test","1","a","analysis")); assert r.count()==1
    def test_install(self): r=PluginRegistry(); r.register(PluginManifest("p1","T","1","a","analysis")); assert r.install("p1")
class TestStratMarket:
    def test_publish(self): m=StrategyMarketplace(); m.publish(StrategyAsset("s1","Alice")); assert m.count()==1
class TestDataMarket:
    def test_upload(self): m=DataMarketplace(); m.upload(DataAsset("d1","Alice","historical","test")); assert m.count()==1
class TestAgentMarket:
    def test_register(self): m=AgentMarketplace(); m.register(AgentAsset("a1","Alice",["analysis"])); assert m.count()==1
class TestEnterprise:
    def test_create_org(self): e=EnterpriseWorkspace(); e.create_org(Organization("o1","Atlas","admin")); assert e.count_orgs()==1
class TestEcoDash:
    def test_summary(self): d=EcosystemDashboard(); d.update(EcosystemData(developer_count=10,plugin_count=5)); s=d.summary(); assert s["developers"]==10
