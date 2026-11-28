import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-extended')))
from orchestrator_v2 import EventHistory, EventType, Event, ActivityExecutor, TimerService, SagaCoordinator, WorkflowOrchestrator


# ---------- v1 parity: every v1 behavior still holds on the v2 track ----------
# (acquire_lease now returns the task token instead of a boolean, the
# improvement from FOLLOW-UPS.md #2; the lifecycle being asserted is the same)

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

    token = executor.acquire_lease("task-1")
    assert token is not None
    assert executor.acquire_lease("task-1") is None  # Already leased

    assert executor.heartbeat("task-1", token) is True

    time.sleep(0.15)

    assert executor.heartbeat("task-1", token) is False  # Lease expired
    new_token = executor.acquire_lease("task-1")
    assert new_token is not None  # Re-acquire lease
    assert executor.complete("task-1", new_token, "result") is True


def test_saga_coordinator():
    saga = SagaCoordinator()

    compensated = []
    saga.add_compensation(lambda: compensated.append("c1"))
    saga.add_compensation(lambda: compensated.append("c2"))

    saga.compensate()

    assert compensated == ["c2", "c1"]  # Reverse order


def test_workflow_orchestrator():
    executor = ActivityExecutor()
    orchestrator = WorkflowOrchestrator(executor)

    orchestrator.start_workflow("wf-1")
    orchestrator.schedule_activity("task-1", "act1")

    def run_worker():
        token = None
        while token is None:
            token = executor.acquire_lease("task-1")
            time.sleep(0.01)
        executor.complete("task-1", token, "result")

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
        token = None
        while token is None:
            token = executor.acquire_lease("task-1")
            time.sleep(0.01)
        executor.complete("task-1", token, "result1")

    t = threading.Thread(target=run_worker)
    t.start()

    orchestrator.wait_for_activity("task-1", compensation=lambda: compensated.append("comp1"))
    t.join()

    orchestrator.schedule_activity("task-2", "act2")

    def run_worker2():
        token = None
        while token is None:
            token = executor.acquire_lease("task-2")
            time.sleep(0.01)
        executor.fail("task-2", token, Exception("Failed!"))

    t2 = threading.Thread(target=run_worker2)
    t2.start()

    with pytest.raises(Exception):
        orchestrator.wait_for_activity("task-2")

    t2.join()

    orchestrator.fail_workflow("wf-1", Exception("Workflow failed due to act2"))

    assert compensated == ["comp1"]

    events = orchestrator.history.replay()
    assert events[-1].event_type == EventType.WORKFLOW_FAILED


# ---------- v2 improvement 1: task tokens against zombies (FOLLOW-UPS.md #2) ----------

def test_zombie_completion_rejected_after_re_lease():
    executor = ActivityExecutor(lease_timeout_sec=0.1)
    executor.submit("task-1", "act")

    zombie_token = executor.acquire_lease("task-1")
    assert zombie_token is not None

    time.sleep(0.15)  # zombie hangs past its lease

    healthy_token = executor.acquire_lease("task-1")
    assert healthy_token is not None
    assert healthy_token != zombie_token

    # The zombie wakes up and tries to complete: rejected (FOLLOW-UPS.md #2).
    assert executor.complete("task-1", zombie_token, "stale result") is False
    assert executor.complete("task-1", healthy_token, "fresh result") is True
    assert executor.tasks["task-1"].result == "fresh result"


def test_zombie_fail_and_heartbeat_rejected_with_stale_token():
    executor = ActivityExecutor(lease_timeout_sec=0.1)
    executor.submit("task-1", "act")

    zombie_token = executor.acquire_lease("task-1")
    time.sleep(0.15)
    healthy_token = executor.acquire_lease("task-1")

    assert executor.heartbeat("task-1", zombie_token) is False
    assert executor.fail("task-1", zombie_token, Exception("stale failure")) is False
    # The healthy lease is untouched.
    assert executor.heartbeat("task-1", healthy_token) is True


def test_calls_without_token_never_accepted():
    executor = ActivityExecutor()
    executor.submit("task-1", "act")
    executor.acquire_lease("task-1")

    assert executor.complete("task-1", None, "result") is False
    assert executor.complete("task-1", "forged-token", "result") is False


# ---------- v2 improvement 2: durable timers (FOLLOW-UPS.md #3/#4) ----------

def test_timers_fire_exactly_once_in_order():
    service = TimerService()
    service.start_timer("timer-2", 1010.0)
    service.start_timer("timer-1", 1005.0)

    assert service.poll_expired(1000.0) == []
    assert service.poll_expired(1006.0) == ["timer-1"]
    assert service.poll_expired(1006.0) == []  # already fired, not re-emitted
    assert service.poll_expired(1011.0) == ["timer-2"]
    assert service.is_fired("timer-1") is True
    assert service.is_fired("timer-2") is True


def test_orchestrator_records_timer_events():
    orchestrator = WorkflowOrchestrator(ActivityExecutor())
    orchestrator.start_workflow("wf-1")
    orchestrator.start_timer("timer-1", 1005.0)

    fired = orchestrator.poll_timers(1006.0)
    assert fired == ["timer-1"]

    event_types = [e.event_type for e in orchestrator.history.replay()]
    assert event_types == [
        EventType.WORKFLOW_STARTED,
        EventType.TIMER_STARTED,
        EventType.TIMER_FIRED,
    ]


# ---------- v2 improvement 3: continue-as-new + history limit (FOLLOW-UPS.md #1) ----------

def test_continue_as_new_resets_history_and_carries_state():
    orchestrator = WorkflowOrchestrator(ActivityExecutor())
    orchestrator.start_workflow("wf-cron")
    orchestrator.schedule_activity("task-1", "act1")
    orchestrator.schedule_activity("task-2", "act2")

    new_run = orchestrator.continue_as_new("wf-cron", {"iterations": 2})

    assert orchestrator.workflow_status == "CONTINUED_AS_NEW"
    old_events = orchestrator.history.replay()
    assert old_events[-1].event_type == EventType.WORKFLOW_CONTINUED_AS_NEW
    assert old_events[-1].payload == {"iterations": 2}

    assert new_run.run_id == orchestrator.run_id + 1
    assert new_run.carried_state == {"iterations": 2}
    new_events = new_run.history.replay()
    assert len(new_events) == 1  # empty history, just the new start
    assert new_events[0].event_type == EventType.WORKFLOW_STARTED


def test_history_limit_enforced():
    orchestrator = WorkflowOrchestrator(ActivityExecutor(), max_history_events=3)
    orchestrator.start_workflow("wf-1")       # event 1
    orchestrator.schedule_activity("t1", "a")  # event 2
    orchestrator.schedule_activity("t2", "b")  # event 3

    with pytest.raises(RuntimeError):
        orchestrator.schedule_activity("t3", "c")  # would be event 4


def test_new_run_continues_working_after_continue_as_new():
    executor = ActivityExecutor()
    orchestrator = WorkflowOrchestrator(executor, max_history_events=2)
    orchestrator.start_workflow("wf-cron")      # event 1
    orchestrator.schedule_activity("t1", "a")    # event 2, limit reached

    new_run = orchestrator.continue_as_new("wf-cron", {"done": ["t1"]})

    # The fresh run has room to schedule again and completes end to end.
    new_run.schedule_activity("t2", "b")

    def run_worker():
        token = None
        while token is None:
            token = executor.acquire_lease("t2")
            time.sleep(0.01)
        executor.complete("t2", token, "result2")

    t = threading.Thread(target=run_worker)
    t.start()
    assert new_run.wait_for_activity("t2") == "result2"
    t.join()

    new_run.complete_workflow("wf-cron")
    assert new_run.workflow_status == "COMPLETED"
