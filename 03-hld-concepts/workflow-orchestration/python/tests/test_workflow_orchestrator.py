"""Unit Tests for Workflow Orchestration Implementations."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))

from saga_step_runner import SagaStepRunner
from workflow_state_machine import WorkflowStateMachine, WorkflowState
from durable_workflow_orchestrator import DurableWorkflowOrchestrator

class MockStep:
    def __init__(self, name, should_fail=False):
        self._name = name
        self.executed = False
        self.compensated = False
        self.should_fail = should_fail
        
    def name(self):
        return self._name
        
    def execute(self):
        if self.should_fail:
            raise RuntimeError("Failed")
        self.executed = True
        
    def compensate(self):
        self.compensated = True

class TestWorkflowOrchestrator(unittest.TestCase):
    
    # v1-simple
    def test_saga_runner_success(self):
        runner = SagaStepRunner()
        step1 = MockStep("step1")
        step2 = MockStep("step2")
        result = runner.run([step1, step2])
        
        self.assertTrue(result.success)
        self.assertTrue(step1.executed)
        self.assertTrue(step2.executed)
        
    def test_saga_runner_failure_compensation(self):
        runner = SagaStepRunner()
        step1 = MockStep("step1")
        step2 = MockStep("step2", should_fail=True)
        result = runner.run([step1, step2])
        
        self.assertFalse(result.success)
        self.assertTrue(step1.executed)
        self.assertFalse(step2.executed)
        self.assertTrue(step1.compensated)
        self.assertEqual(result.compensated_steps, ["step1"])

    # v2-realistic
    def test_state_machine_transitions(self):
        machine = WorkflowStateMachine()
        machine.create("wf-1")
        self.assertEqual(machine.get("wf-1"), WorkflowState.CREATED)
        machine.mark_running("wf-1")
        self.assertEqual(machine.get("wf-1"), WorkflowState.RUNNING)
        machine.mark_succeeded("wf-1")
        self.assertEqual(machine.get("wf-1"), WorkflowState.SUCCEEDED)
        
    def test_state_machine_failure(self):
        machine = WorkflowStateMachine()
        machine.create("wf-2")
        machine.mark_failed("wf-2")
        self.assertEqual(machine.get("wf-2"), WorkflowState.FAILED)

    # v3-production
    def test_durable_orchestrator_start_idempotency(self):
        orch = DurableWorkflowOrchestrator()
        wf_id1 = orch.start("idemp-1", "wf-A")
        wf_id2 = orch.start("idemp-1", "wf-B")
        
        self.assertEqual(wf_id1, "wf-A")
        self.assertEqual(wf_id2, "wf-A")
        
    def test_durable_orchestrator_resume_checkpoint(self):
        orch = DurableWorkflowOrchestrator()
        orch.start("idemp-2", "wf-C")
        orch.checkpoint("wf-C", 5)
        
        resumed_checkpoint = None
        def handler(wf_id, cp):
            nonlocal resumed_checkpoint
            resumed_checkpoint = cp
            
        orch.resume("wf-C", handler)
        self.assertEqual(resumed_checkpoint, 5)

if __name__ == '__main__':
    unittest.main()
