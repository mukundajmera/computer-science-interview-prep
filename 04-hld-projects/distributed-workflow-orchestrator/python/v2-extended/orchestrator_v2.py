"""v2-extended workflow orchestrator. The event-sourced history, lease
lifecycle, saga compensation and wait loop are v1 behavior; the step-ups
are the ones the project's own docs call for:

1. Task tokens against zombie workers (FOLLOW-UPS.md #2, PITFALLS.md #4):
   every lease acquisition issues a fresh task_token and the orchestrator
   only accepts complete/fail/heartbeat calls carrying the currently
   valid token. A hung worker whose lease expired and was re-acquired by
   another worker is rejected when it wakes up.
2. Durable timers (FOLLOW-UPS.md #3/#4): timers are persisted rows with
   an expiration; a poll scan turns expired rows into TimerFired events
   that wake the workflow - workers never block a thread sleeping.
3. Continue-As-New with a history limit (FOLLOW-UPS.md #1, PITFALLS.md
   #3): histories cannot grow forever. Scheduling past the configured
   event limit fails loudly, and continue_as_new closes the run and
   spawns a fresh execution with an empty history seeded from the
   workflow's logical state.
"""
import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class EventType(Enum):
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    ACTIVITY_SCHEDULED = "ACTIVITY_SCHEDULED"
    ACTIVITY_COMPLETED = "ACTIVITY_COMPLETED"
    ACTIVITY_FAILED = "ACTIVITY_FAILED"
    TIMER_STARTED = "TIMER_STARTED"
    TIMER_FIRED = "TIMER_FIRED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_CONTINUED_AS_NEW = "WORKFLOW_CONTINUED_AS_NEW"

    @property
    def value(self):
        return self._value_


class Event:
    def __init__(self, event_type: EventType, event_id: str, payload: Any = None):
        self.event_type = event_type
        self.event_id = event_id
        self.payload = payload


class EventHistory:
    def __init__(self):
        self.events: List[Event] = []
        self._lock = threading.RLock()

    def add_event(self, event: Event) -> None:
        with self._lock:
            self.events.append(event)

    def get_events(self) -> List[Event]:
        with self._lock:
            return list(self.events)

    def replay(self) -> List[Event]:
        with self._lock:
            return list(self.events)

    def size(self) -> int:
        with self._lock:
            return len(self.events)


class ActivityTask:
    def __init__(self, task_id: str, activity_name: str, args: tuple, kwargs: dict):
        self.task_id = task_id
        self.activity_name = activity_name
        self.args = args
        self.kwargs = kwargs
        self.status = "PENDING"
        self.result = None
        self.error = None
        self.lease_expires_at: Optional[float] = None
        self.lease_version = 0
        self.lease_token: Optional[str] = None


class ActivityExecutor:
    """v1 lease lifecycle plus task tokens (FOLLOW-UPS.md #2).

    acquire_lease returns the token the worker must present on every
    later call; a new acquisition invalidates every older token."""

    def __init__(self, lease_timeout_sec: float = 5.0, clock: Callable[[], float] = None):
        self.lease_timeout_sec = lease_timeout_sec
        self._clock = clock or time.time
        self.tasks: Dict[str, ActivityTask] = {}
        self._lock = threading.RLock()

    def submit(self, task_id: str, activity_name: str, *args, **kwargs) -> ActivityTask:
        with self._lock:
            task = ActivityTask(task_id, activity_name, args, kwargs)
            self.tasks[task_id] = task
            return task

    def acquire_lease(self, task_id: str) -> Optional[str]:
        """Lease the task and return its task token; None if not leasable."""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            now = self._clock()
            if task.status == "PENDING" or (
                task.status == "LEASED" and task.lease_expires_at and now > task.lease_expires_at
            ):
                task.status = "LEASED"
                task.lease_expires_at = now + self.lease_timeout_sec
                task.lease_version += 1
                task.lease_token = "%s-lease-%d" % (task_id, task.lease_version)
                return task.lease_token
            return None

    def _check_token(self, task: Optional[ActivityTask], token: Optional[str]) -> bool:
        if not task or task.status != "LEASED":
            return False
        if token is None or token != task.lease_token:
            return False
        now = self._clock()
        return not (task.lease_expires_at and now > task.lease_expires_at)

    def heartbeat(self, task_id: str, token: str) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not self._check_token(task, token):
                return False
            task.lease_expires_at = self._clock() + self.lease_timeout_sec
            return True

    def complete(self, task_id: str, token: str, result: Any) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not self._check_token(task, token):
                return False
            task.status = "COMPLETED"
            task.result = result
            return True

    def fail(self, task_id: str, token: str, error: Exception) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not self._check_token(task, token):
                return False
            task.status = "FAILED"
            task.error = error
            return True


class TimerService:
    """Durable timer rows plus an expiry scan (FOLLOW-UPS.md #3/#4). A
    fired timer is marked, so a poll never emits the same timer twice."""

    def __init__(self):
        self._timers: Dict[str, float] = {}
        self._fired: set = set()
        self._lock = threading.RLock()

    def start_timer(self, timer_id: str, fire_at: float) -> None:
        with self._lock:
            self._timers[timer_id] = fire_at

    def poll_expired(self, now: float) -> List[str]:
        """Timer ids that expired since the last poll, in fire-time order."""
        with self._lock:
            expired = [tid for tid, fire_at in self._timers.items()
                       if fire_at <= now and tid not in self._fired]
            expired.sort(key=lambda tid: self._timers[tid])
            for tid in expired:
                self._fired.add(tid)
            return expired

    def is_fired(self, timer_id: str) -> bool:
        with self._lock:
            return timer_id in self._fired


class SagaCoordinator:
    def __init__(self):
        self.compensations: List[Callable[[], None]] = []
        self._lock = threading.RLock()

    def add_compensation(self, compensation: Callable[[], None]) -> None:
        with self._lock:
            self.compensations.append(compensation)

    def compensate(self) -> None:
        with self._lock:
            while self.compensations:
                comp = self.compensations.pop()
                try:
                    comp()
                except Exception:
                    pass


class WorkflowOrchestrator:
    def __init__(self, activity_executor: ActivityExecutor,
                 timer_service: Optional[TimerService] = None,
                 max_history_events: int = 50000,
                 run_id: int = 1, carried_state: Any = None):
        self.history = EventHistory()
        self.executor = activity_executor
        self.timer_service = timer_service or TimerService()
        self.saga = SagaCoordinator()
        self.workflow_status = "PENDING"
        self.max_history_events = max_history_events
        self.run_id = run_id
        # Logical state handed over by the previous run (Continue-As-New).
        self.carried_state = carried_state
        self._lock = threading.RLock()

    def _enforce_history_limit(self) -> None:
        if self.history.size() >= self.max_history_events:
            raise RuntimeError(
                "history limit %d reached; continue_as_new required" % self.max_history_events)

    def start_workflow(self, workflow_id: str) -> None:
        with self._lock:
            self.history.add_event(Event(EventType.WORKFLOW_STARTED, workflow_id))
            self.workflow_status = "RUNNING"

    def schedule_activity(self, task_id: str, activity_name: str, *args, **kwargs) -> None:
        with self._lock:
            self._enforce_history_limit()
            self.history.add_event(Event(EventType.ACTIVITY_SCHEDULED, task_id, activity_name))
            self.executor.submit(task_id, activity_name, *args, **kwargs)

    def start_timer(self, timer_id: str, fire_at: float) -> None:
        """Persist a durable timer and record it; the workflow suspends
        instead of blocking a thread (FOLLOW-UPS.md #4)."""
        with self._lock:
            self._enforce_history_limit()
            self.timer_service.start_timer(timer_id, fire_at)
            self.history.add_event(Event(EventType.TIMER_STARTED, timer_id, fire_at))

    def poll_timers(self, now: float) -> List[str]:
        """Turn expired timer rows into TimerFired events (FOLLOW-UPS.md #3)."""
        fired = self.timer_service.poll_expired(now)
        with self._lock:
            for timer_id in fired:
                self.history.add_event(Event(EventType.TIMER_FIRED, timer_id))
        return fired

    def wait_for_activity(self, task_id: str, compensation: Optional[Callable[[], None]] = None) -> Any:
        while True:
            with self.executor._lock:
                task = self.executor.tasks.get(task_id)
                if task and task.status == "COMPLETED":
                    with self._lock:
                        self.history.add_event(Event(EventType.ACTIVITY_COMPLETED, task_id, task.result))
                        if compensation:
                            self.saga.add_compensation(compensation)
                    return task.result
                elif task and task.status == "FAILED":
                    with self._lock:
                        self.history.add_event(Event(EventType.ACTIVITY_FAILED, task_id, str(task.error)))
                    raise Exception(f"Activity failed: {task.error}")
            time.sleep(0.01)

    def complete_workflow(self, workflow_id: str) -> None:
        with self._lock:
            self.history.add_event(Event(EventType.WORKFLOW_COMPLETED, workflow_id))
            self.workflow_status = "COMPLETED"

    def fail_workflow(self, workflow_id: str, error: Exception) -> None:
        with self._lock:
            self.history.add_event(Event(EventType.WORKFLOW_FAILED, workflow_id, str(error)))
            self.workflow_status = "FAILED"
            self.saga.compensate()

    def continue_as_new(self, workflow_id: str, state: Any) -> 'WorkflowOrchestrator':
        """Close this run and spawn a fresh execution with an empty
        history seeded from the workflow's logical state (FOLLOW-UPS.md #1)."""
        with self._lock:
            self.history.add_event(Event(EventType.WORKFLOW_CONTINUED_AS_NEW, workflow_id, state))
            self.workflow_status = "CONTINUED_AS_NEW"
        new_run = WorkflowOrchestrator(
            self.executor, self.timer_service, self.max_history_events,
            run_id=self.run_id + 1, carried_state=state)
        new_run.start_workflow(workflow_id)
        return new_run
