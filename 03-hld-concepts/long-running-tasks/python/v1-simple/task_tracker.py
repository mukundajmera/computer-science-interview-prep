import threading
import uuid
import time
from enum import Enum
from typing import Callable, Dict, Optional, Any

class TaskStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskInfo:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = TaskStatus.QUEUED
        self.progress = 0  # 0-100
        self.result = None
        self.error = None

class TaskContext:
    def __init__(self, task_info: TaskInfo, stop_event: threading.Event):
        self.task_info = task_info
        self.stop_event = stop_event

    def set_progress(self, progress: int):
        if not (0 <= progress <= 100):
            raise ValueError("Progress must be between 0 and 100")
        self.task_info.progress = progress

    def is_cancelled(self) -> bool:
        return self.stop_event.is_set() or self.task_info.status == TaskStatus.CANCELLED

class TaskTracker:
    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self.stop_events: Dict[str, threading.Event] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self._lock = threading.Lock()

    def submit_task(self, action: Callable[[TaskContext], Any], callback: Optional[Callable[[TaskInfo], None]] = None) -> str:
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(task_id)
        stop_event = threading.Event()

        with self._lock:
            self.tasks[task_id] = task_info
            self.stop_events[task_id] = stop_event

        def worker():
            context = TaskContext(task_info, stop_event)
            try:
                if context.is_cancelled():
                    return

                with self._lock:
                    if task_info.status == TaskStatus.CANCELLED:
                        return
                    task_info.status = TaskStatus.RUNNING

                result = action(context)

                with self._lock:
                    if context.is_cancelled():
                        task_info.status = TaskStatus.CANCELLED
                    else:
                        task_info.result = result
                        task_info.progress = 100
                        task_info.status = TaskStatus.COMPLETED
            except Exception as e:
                with self._lock:
                    task_info.error = str(e)
                    task_info.status = TaskStatus.FAILED
            finally:
                with self._lock:
                    self.stop_events.pop(task_id, None)
                    self.threads.pop(task_id, None)
                if callback:
                    callback(task_info)

        thread = threading.Thread(target=worker, daemon=True)
        with self._lock:
            self.threads[task_id] = thread

        thread.start()
        return task_id

    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        with self._lock:
            return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return False

            if task_info.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                return False

            task_info.status = TaskStatus.CANCELLED
            stop_event = self.stop_events.get(task_id)
            if stop_event:
                stop_event.set()
            return True

    def shutdown(self):
        with self._lock:
            for stop_event in self.stop_events.values():
                stop_event.set()

        # Wait for threads to finish
        threads = list(self.threads.values())
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=2.0)