"""Tests for Sprint P4 Commercial Platform."""
from __future__ import annotations
import pytest
from engine.commerce import LicenseManager, SubscriptionManager, RevenueAnalyzer, LicenseType
from engine.data_center import DataIngestionPipeline, DataQualityEngine, DataQualityScore
from engine.model_hub import ModelHub, ModelRecord
from sdk.python.atlas_client import AtlasClient
from apps.admin import AdminCenter, AdminUser, AuditLog
from deployment import DeploymentManager, DeploymentConfig

class TestCommerce:
    def test_license(self): m=LicenseManager(); l=m.generate("u1",LicenseType.PRO,["advanced"]); assert m.validate(l.id)
    def test_subscription(self): s=SubscriptionManager(); s.create("u1","pro"); assert s.get_plan("u1")=="pro"
    def test_revenue(self): r=RevenueAnalyzer(); r.record(100,"pro"); assert r.mrr()==100

class TestDataCenter:
    def test_ingestion(self): p=DataIngestionPipeline(); r=p.ingest("api",[{"id":1}]); assert r["status"]=="success"
    def test_quality(self): q=DataQualityEngine.compute(0.9,0.8,0.7,0.6,0.5); assert q.overall()==0.7

class TestModelHub:
    def test_register(self): h=ModelHub(); h.register(ModelRecord("m1","test")); assert h.count()==1

class TestSDK:
    def test_client(self): c=AtlasClient("test-key"); assert c._api_key=="test-key"

class TestAdmin:
    def test_manage(self): a=AdminCenter(); a.manage_user(AdminUser("u1","Alice")); assert a.count_users()==1

class TestDeploy:
    def test_config(self): d=DeploymentManager(); assert d.get_config().docker_version=="24.0"
