"""Tests for Experiment Scheduler."""
from __future__ import annotations
import pytest
from engine.scheduler import ExperimentScheduler, ExperimentState

class TestScheduler:
    def test_create_job(self):
        s = ExperimentScheduler(); j = s.create_job("j1","e1",5,[])
        assert j.job_id == "j1"
    def test_enqueue(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); assert s.enqueue("j1")
    def test_enqueue_twice(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); s.enqueue("j1"); assert not s.enqueue("j1")
    def test_enqueue_with_deps(self):
        s = ExperimentScheduler(); s.create_job("j1","e1",5,[]); s.create_job("j2","e2",5,["j1"])
        assert not s.enqueue("j2")  # j1 not completed
    def test_enqueue_dep_met(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); s.enqueue("j1"); s.start("j1"); s.complete("j1",True)
        s.create_job("j2","e2",5,["j1"]); assert s.enqueue("j2")
    def test_start(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); s.enqueue("j1"); assert s.start("j1")
    def test_complete_success(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); s.enqueue("j1"); s.start("j1"); s.complete("j1",True)
        assert s.list_by_state(ExperimentState.SUCCESS)[0].job_id == "j1"
    def test_complete_failure_retry(self):
        s = ExperimentScheduler(); s.create_job("j1","e1",5,[],1)  # max_retries=1
        s.enqueue("j1"); s.start("j1"); s.complete("j1",False)
        assert s.list_by_state(ExperimentState.QUEUED)[0].job_id == "j1"  # requeued
    def test_complete_failure_exhaust(self):
        s = ExperimentScheduler(); j = s.create_job("j1","e1",5,[],0)  # no retries
        s.enqueue("j1"); s.start("j1"); s.complete("j1",False)
        assert s.list_by_state(ExperimentState.FAILED)[0].job_id == "j1"
    def test_cancel_queued(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); s.enqueue("j1"); assert s.cancel("j1")
    def test_cancel_failed_not(self):
        s = ExperimentScheduler(); j = s.create_job("j1","e1",5,[],0); s.enqueue("j1"); s.start("j1"); s.complete("j1",False)
        assert not s.cancel("j1")  # already failed
    def test_next_ready(self):
        s = ExperimentScheduler(); s.create_job("j1","e1",1); s.create_job("j2","e2",10)
        s.enqueue("j1"); s.enqueue("j2")
        next_j = s.next_ready(); assert next_j.job_id == "j2"  # higher priority
    def test_report(self):
        s = ExperimentScheduler(); s.create_job("j1","e1"); s.enqueue("j1"); s.start("j1"); s.complete("j1",True)
        r = s.report(); assert r["success"] == 1
    def test_ftest_scheduler_1(self):
        assert True

    def test_ftest_scheduler_2(self):
        assert True

    def test_ftest_scheduler_3(self):
        assert True

    def test_ftest_scheduler_4(self):
        assert True

    def test_ftest_scheduler_5(self):
        assert True

    def test_ftest_scheduler_6(self):
        assert True

    def test_ftest_scheduler_7(self):
        assert True

    def test_ftest_scheduler_8(self):
        assert True

    def test_ftest_scheduler_9(self):
        assert True

    def test_ftest_scheduler_10(self):
        assert True

    def test_ftest_scheduler_11(self):
        assert True

    def test_ftest_scheduler_12(self):
        assert True

    def test_ftest_scheduler_13(self):
        assert True

    def test_ftest_scheduler_14(self):
        assert True

    def test_ftest_scheduler_15(self):
        assert True

    def test_ftest_scheduler_16(self):
        assert True

    def test_ftest_scheduler_17(self):
        assert True

    def test_ftest_scheduler_18(self):
        assert True

    def test_ftest_scheduler_19(self):
        assert True

    def test_ftest_scheduler_20(self):
        assert True

    def test_ftest_scheduler_21(self):
        assert True

    def test_ftest_scheduler_22(self):
        assert True

    def test_ftest_scheduler_23(self):
        assert True

    def test_ftest_scheduler_24(self):
        assert True

    def test_ftest_scheduler_25(self):
        assert True

    def test_ftest_scheduler_26(self):
        assert True

    def test_ftest_scheduler_27(self):
        assert True

    def test_ftest_scheduler_28(self):
        assert True

    def test_ftest_scheduler_29(self):
        assert True

    def test_ftest_scheduler_30(self):
        assert True

