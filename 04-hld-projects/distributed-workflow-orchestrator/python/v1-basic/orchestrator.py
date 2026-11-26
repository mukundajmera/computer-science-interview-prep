import time
import threading
from typing import List, Dict, Any, Callable, Optional
from enum import Enum


class EventType(Enum):
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    ACTIVITY_SCHEDULED = "ACTIVITY_SCHEDULED"
    ACTIVITY_COMPLETED = "ACTIVITY_COMPLETED"
    ACTIVITY_FAILED = "ACTIVITY_FAILED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"

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


class ActivityExecutor:
    def __init__(self, lease_timeout_sec: float = 5.0):
        self.lease_timeout_sec = lease_timeout_sec
        self.tasks: Dict[str, ActivityTask] = {}
        self._lock = threading.RLock()

    def submit(self, task_id: str, activity_name: str, *args, **kwargs) -> ActivityTask:
        with self._lock:
            task = ActivityTask(task_id, activity_name, args, kwargs)
            self.tasks[task_id] = task
            return task

    def acquire_lease(self, task_id: str) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
            now = time.time()
            if task.status == "PENDING" or (
                task.status == "LEASED" and task.lease_expires_at and now > task.lease_expires_at
            ):
                task.status = "LEASED"
                task.lease_expires_at = now + self.lease_timeout_sec
                return True
            return False

    def heartbeat(self, task_id: str) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task or task.status != "LEASED":
                return False
            now = time.time()
            if task.lease_expires_at and now > task.lease_expires_at:
                return False
            task.lease_expires_at = now + self.lease_timeout_sec
            return True

    def complete(self, task_id: str, result: Any) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task or task.status != "LEASED":
                return False
            now = time.time()
            if task.lease_expires_at and now > task.lease_expires_at:
                return False
            task.status = "COMPLETED"
            task.result = result
            return True

    def fail(self, task_id: str, error: Exception) -> bool:
        with self._lock:
            task = self.tasks.get(task_id)
            if not task or task.status != "LEASED":
                return False
            now = time.time()
            if task.lease_expires_at and now > task.lease_expires_at:
                return False
            task.status = "FAILED"
            task.error = error
            return True


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
                except Exception as e:
                    pass


class WorkflowOrchestrator:
    def __init__(self, activity_executor: ActivityExecutor):
        self.history = EventHistory()
        self.executor = activity_executor
        self.saga = SagaCoordinator()
        self.workflow_status = "PENDING"
        self._lock = threading.RLock()
        
    def start_workflow(self, workflow_id: str) -> None:
        with self._lock:
            self.history.add_event(Event(EventType.WORKFLOW_STARTED, workflow_id))
            self.workflow_status = "RUNNING"

    def schedule_activity(self, task_id: str, activity_name: str, *args, **kwargs) -> None:
        with self._lock:
            self.history.add_event(Event(EventType.ACTIVITY_SCHEDULED, task_id, activity_name))
            self.executor.submit(task_id, activity_name, *args, **kwargs)

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
