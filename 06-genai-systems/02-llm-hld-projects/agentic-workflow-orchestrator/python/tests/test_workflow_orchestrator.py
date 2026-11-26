import pytest
import sys
import os

# Insert v1-basic path to avoid hyphenated directory import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from workflow_orchestrator import WorkflowOrchestrator, Node, StepResult, WorkflowState

def test_linear_execution():
    orchestrator = WorkflowOrchestrator()

    def step1(state: WorkflowState):
        state.update("step1", True)
        return StepResult(status='SUCCESS', next_step='step2')

    def step2(state: WorkflowState):
        state.update("step2", True)
        return StepResult(status='SUCCESS', next_step='END')

    orchestrator.add_node(Node("step1", step1), is_start=True)
    orchestrator.add_node(Node("step2", step2))

    status, final_state = orchestrator.execute()
    assert status == 'COMPLETED'
    assert final_state.get('step1') is True
    assert final_state.get('step2') is True

def test_conditional_branching():
    orchestrator = WorkflowOrchestrator()

    def decision_step(state: WorkflowState):
        value = state.get("value", 0)
        if value > 10:
            return StepResult(status='SUCCESS', next_step='high_branch')
        else:
            return StepResult(status='SUCCESS', next_step='low_branch')

    def high_branch(state: WorkflowState):
        state.update("branch", "high")
        return StepResult(status='SUCCESS', next_step='END')

    def low_branch(state: WorkflowState):
        state.update("branch", "low")
        return StepResult(status='SUCCESS', next_step='END')

    orchestrator.add_node(Node("decision", decision_step), is_start=True)
    orchestrator.add_node(Node("high_branch", high_branch))
    orchestrator.add_node(Node("low_branch", low_branch))

    status, final_state = orchestrator.execute({"value": 15})
    assert status == 'COMPLETED'
    assert final_state.get('branch') == 'high'

    status2, final_state2 = orchestrator.execute({"value": 5})
    assert status2 == 'COMPLETED'
    assert final_state2.get('branch') == 'low'

def test_retry_fallback_handler():
    orchestrator = WorkflowOrchestrator()

    attempts = 0
    def failing_step(state: WorkflowState):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Temporary failure")
        return StepResult(status='SUCCESS', next_step='END')

    orchestrator.add_node(Node("flaky", failing_step, max_retries=3), is_start=True)

    status, final_state = orchestrator.execute()
    assert status == 'COMPLETED'
    assert attempts == 3

def test_permanent_failure():
    orchestrator = WorkflowOrchestrator()

    def permanent_fail(state: WorkflowState):
        raise ValueError("Permanent failure")

    orchestrator.add_node(Node("fail", permanent_fail, max_retries=1), is_start=True)

    status, final_state = orchestrator.execute()
    assert status == 'FAILED'

def test_max_step_budget_guard():
    orchestrator = WorkflowOrchestrator(max_steps=5)

    def loop_step(state: WorkflowState):
        count = state.get("count", 0)
        state.update("count", count + 1)
        return StepResult(status='SUCCESS', next_step='loop_step')

    orchestrator.add_node(Node("loop_step", loop_step), is_start=True)

    status, final_state = orchestrator.execute()
    assert status == 'MAX_STEPS_EXCEEDED'
    assert final_state.get('count') == 5
