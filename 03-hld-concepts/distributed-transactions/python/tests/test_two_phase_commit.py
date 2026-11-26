import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

import pytest
from two_phase_commit_coordinator import Participant, TwoPhaseCommitCoordinator, SagaStep, SagaOrchestrator

class MockParticipant(Participant):
    def __init__(self, prepare_res=True, commit_res=True, abort_res=True, prepare_exc=False):
        self.prepare_res = prepare_res
        self.commit_res = commit_res
        self.abort_res = abort_res
        self.prepare_exc = prepare_exc
        self.prepared = False
        self.committed = False
        self.aborted = False

    def prepare(self) -> bool:
        if self.prepare_exc:
            raise Exception("Prepare timeout/error")
        if self.prepare_res:
            self.prepared = True
            return True
        return False

    def commit(self) -> bool:
        if self.commit_res:
            self.committed = True
            return True
        return False

    def abort(self) -> bool:
        if self.abort_res:
            self.aborted = True
            return True
        return False

class MockSagaStep(SagaStep):
    def __init__(self, exec_res=True, comp_res=True, exec_exc=False):
        self.exec_res = exec_res
        self.comp_res = comp_res
        self.exec_exc = exec_exc
        self.executed = False
        self.compensated = False

    def execute(self) -> bool:
        if self.exec_exc:
            raise Exception("Execute error")
        if self.exec_res:
            self.executed = True
            return True
        return False

    def compensate(self) -> bool:
        if self.comp_res:
            self.compensated = True
            return True
        return False

def test_2pc_all_prepare_and_commit():
    p1 = MockParticipant()
    p2 = MockParticipant()
    coordinator = TwoPhaseCommitCoordinator([p1, p2])

    result = coordinator.execute_transaction()

    assert result is True
    assert p1.prepared is True and p1.committed is True and p1.aborted is False
    assert p2.prepared is True and p2.committed is True and p2.aborted is False
    assert "TX_COMMITTED" in coordinator.wal

def test_2pc_one_prepare_fails_causes_abort():
    p1 = MockParticipant(prepare_res=True)
    p2 = MockParticipant(prepare_res=False)
    coordinator = TwoPhaseCommitCoordinator([p1, p2])

    result = coordinator.execute_transaction()

    assert result is False
    assert p1.prepared is True and p1.committed is False and p1.aborted is True
    assert p2.prepared is False and p2.committed is False and p2.aborted is False
    assert "TX_ABORTED" in coordinator.wal

def test_2pc_timeout_causes_abort():
    p1 = MockParticipant(prepare_res=True)
    p2 = MockParticipant(prepare_exc=True)
    coordinator = TwoPhaseCommitCoordinator([p1, p2])

    result = coordinator.execute_transaction()

    assert result is False
    assert p1.prepared is True and p1.committed is False and p1.aborted is True
    assert p2.prepared is False and p2.committed is False and p2.aborted is False
    assert "TX_ABORTED" in coordinator.wal

def test_saga_all_steps_succeed():
    s1 = MockSagaStep()
    s2 = MockSagaStep()
    orchestrator = SagaOrchestrator([s1, s2])

    result = orchestrator.execute()

    assert result is True
    assert orchestrator.state == "COMPLETED"
    assert s1.executed is True and s1.compensated is False
    assert s2.executed is True and s2.compensated is False

def test_saga_step_fails_causes_compensation():
    s1 = MockSagaStep(exec_res=True)
    s2 = MockSagaStep(exec_res=False)
    orchestrator = SagaOrchestrator([s1, s2])

    result = orchestrator.execute()

    assert result is False
    assert orchestrator.state == "COMPENSATED"
    assert s1.executed is True and s1.compensated is True
    assert s2.executed is False and s2.compensated is False

def test_saga_step_exception_causes_compensation():
    s1 = MockSagaStep(exec_res=True)
    s2 = MockSagaStep(exec_exc=True)
    orchestrator = SagaOrchestrator([s1, s2])

    result = orchestrator.execute()

    assert result is False
    assert orchestrator.state == "COMPENSATED"
    assert s1.executed is True and s1.compensated is True
    assert s2.executed is False and s2.compensated is False
