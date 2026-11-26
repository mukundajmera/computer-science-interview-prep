import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
from orchestrator import EventHistory, EventType, Event, ActivityExecutor, SagaCoordinator, WorkflowOrchestrator

def test_event_history():
    history = EventHistory()
    history.add_event(Event(EventType.WORKFLOW_STARTED, "wf-1"))
    history.add_event(Event(EventType.ACTIVITY_SCHEDULED, "task-1"))
    events = history.replay()
    assert len(events) == 2
    assert events[0].event_type == EventType.WORKFLOW_STARTED
    assert events[1].event_type == EventType.ACTIVITY_SCHEDULED

def test_activity_executor_lease():
    executor = ActivityExecutor(lease_timeout_sec=0.1)
    task = executor.submit("task-1", "my_activity")
    
    assert executor.acquire_lease("task-1") is True
    assert executor.acquire_lease("task-1") is False # Already leased
    
    assert executor.heartbeat("task-1") is True
    
    time.sleep(0.15)
    
    assert executor.heartbeat("task-1") is False # Lease expired
    assert executor.acquire_lease("task-1") is True # Re-acquire lease
    assert executor.complete("task-1", "result") is True

def test_saga_coordinator():
    saga = SagaCoordinator()
    
    compensated = []
    saga.add_compensation(lambda: compensated.append("c1"))
    saga.add_compensation(lambda: compensated.append("c2"))
    
    saga.compensate()
    
    assert compensated == ["c2", "c1"] # Reverse order

def test_workflow_orchestrator():
    executor = ActivityExecutor()
    orchestrator = WorkflowOrchestrator(executor)
    
    orchestrator.start_workflow("wf-1")
    orchestrator.schedule_activity("task-1", "act1")
    
    def run_worker():
        while not executor.acquire_lease("task-1"):
            time.sleep(0.01)
        executor.complete("task-1", "result")
        
    t = threading.Thread(target=run_worker)
    t.start()
    
    result = orchestrator.wait_for_activity("task-1")
    t.join()
    
    assert result == "result"
    orchestrator.complete_workflow("wf-1")
    
    events = orchestrator.history.replay()
    assert len(events) == 4
    assert events[-1].event_type == EventType.WORKFLOW_COMPLETED

def test_workflow_saga_on_failure():
    executor = ActivityExecutor()
    orchestrator = WorkflowOrchestrator(executor)
    
    compensated = []
    
    orchestrator.start_workflow("wf-1")
    orchestrator.schedule_activity("task-1", "act1")
    
    def run_worker():
        while not executor.acquire_lease("task-1"):
            time.sleep(0.01)
        executor.complete("task-1", "result1")
        
    t = threading.Thread(target=run_worker)
    t.start()
    
    orchestrator.wait_for_activity("task-1", compensation=lambda: compensated.append("comp1"))
    t.join()
    
    orchestrator.schedule_activity("task-2", "act2")
    
    def run_worker2():
        while not executor.acquire_lease("task-2"):
            time.sleep(0.01)
        executor.fail("task-2", Exception("Failed!"))
        
    t2 = threading.Thread(target=run_worker2)
    t2.start()
    
    with pytest.raises(Exception):
        orchestrator.wait_for_activity("task-2")
        
    t2.join()
    
    orchestrator.fail_workflow("wf-1", Exception("Workflow failed due to act2"))
    
    assert compensated == ["comp1"]
    
    events = orchestrator.history.replay()
    assert events[-1].event_type == EventType.WORKFLOW_FAILED
