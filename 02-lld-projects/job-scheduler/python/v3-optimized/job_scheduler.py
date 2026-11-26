"""JobScheduler for job-scheduler (v3-optimized)."""

import enum
import threading
import time
import heapq
from typing import Callable, Any, List, Dict, Optional

class TaskState(enum.Enum):
    PENDING = 0
    SCHEDULED = 1
    RUNNING = 2
    COMPLETED = 3
    FAILED = 4

class DAGTask:
    def __init__(self, task_id: str, action: Callable[[], Any], dependencies: List[str] = None, priority: int = 0):
        self.task_id = task_id
        self.action = action
        self.dependencies = dependencies or []
        self.priority = priority
        self.state = TaskState.PENDING
        self.state_lock = threading.Lock()
        self.completion_condition = threading.Condition(self.state_lock)
        self.result = None
        self.error = None

    def transition_state(self, expected_current: TaskState, next_state: TaskState) -> bool:
        with self.state_lock:
            if self.state == expected_current:
                self.state = next_state
                if next_state in (TaskState.COMPLETED, TaskState.FAILED):
                    self.completion_condition.notify_all()
                return True
            return False

    def wait_for_completion(self, timeout: float = None) -> TaskState:
        with self.state_lock:
            while self.state not in (TaskState.COMPLETED, TaskState.FAILED):
                self.completion_condition.wait(timeout)
            return self.state

class ScheduledTask:
    def __init__(self, execute_at: float, task: DAGTask):
        self.execute_at = execute_at
        self.task = task
        self._id = id(self)

    def __lt__(self, other):
        if self.execute_at == other.execute_at:
            return self.task.priority < other.task.priority
        return self.execute_at < other.execute_at

class PriorityBlockingQueue:
    def __init__(self):
        self._heap: List[ScheduledTask] = []
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._shutdown = False

    def put(self, item: ScheduledTask):
        with self._lock:
            if self._shutdown:
                return
            heapq.heappush(self._heap, item)
            if self._heap[0] is item:
                self._not_empty.notify_all()

    def take(self, timeout: float = None) -> Optional[ScheduledTask]:
        with self._lock:
            while True:
                if self._shutdown and not self._heap:
                    return None

                if not self._heap:
                    if timeout is not None:
                        self._not_empty.wait(timeout)
                        if not self._heap:
                            return None
                    else:
                        self._not_empty.wait()
                    continue

                now = time.time()
                top_item = self._heap[0]
                delay = top_item.execute_at - now

                if delay <= 0:
                    return heapq.heappop(self._heap)
                else:
                    if timeout is not None:
                        wait_time = min(timeout, delay)
                        self._not_empty.wait(wait_time)
                        if time.time() - now >= timeout:
                            return None
                    else:
                        self._not_empty.wait(delay)

    def shutdown(self):
        with self._lock:
            self._shutdown = True
            self._not_empty.notify_all()

class ScheduledThreadPoolExecutor:
    def __init__(self, max_workers: int):
        self.max_workers = max_workers
        self.queue = PriorityBlockingQueue()
        self.threads: List[threading.Thread] = []
        self._is_running = False

    def start(self):
        self._is_running = True
        for i in range(self.max_workers):
            t = threading.Thread(target=self._worker_loop, name=f"Worker-{i}")
            t.daemon = True
            t.start()
            self.threads.append(t)

    def stop(self):
        self._is_running = False
        self.queue.shutdown()
        for t in self.threads:
            t.join()

    def schedule(self, task: DAGTask, delay_seconds: float):
        if task.transition_state(TaskState.PENDING, TaskState.SCHEDULED):
            execute_at = time.time() + delay_seconds
            self.queue.put(ScheduledTask(execute_at, task))

    def _worker_loop(self):
        while self._is_running or not getattr(self.queue, '_shutdown', False):
            scheduled_task = self.queue.take()
            if scheduled_task is None:
                if getattr(self.queue, '_shutdown', False) and not self.queue._heap:
                    break
                continue

            task = scheduled_task.task
            if task.transition_state(TaskState.SCHEDULED, TaskState.RUNNING):
                try:
                    task.result = task.action()
                    task.transition_state(TaskState.RUNNING, TaskState.COMPLETED)
                except Exception as e:
                    task.error = e
                    task.transition_state(TaskState.RUNNING, TaskState.FAILED)

class CompletionBarrier:
    """Topological completion barrier for DAG dependencies."""
    def __init__(self, count: int, on_complete: Callable[[], None]):
        self.count = count
        self.lock = threading.Lock()
        self.on_complete = on_complete

    def count_down(self):
        with self.lock:
            self.count -= 1
            if self.count == 0:
                self.on_complete()

class DAGScheduler:
    def __init__(self, executor: ScheduledThreadPoolExecutor):
        self.executor = executor
        self.tasks: Dict[str, DAGTask] = {}
        self.dependents: Dict[str, List[DAGTask]] = {}
        self.barriers: Dict[str, CompletionBarrier] = {}
        self.lock = threading.Lock()

    def add_task(self, task: DAGTask):
        with self.lock:
            self.tasks[task.task_id] = task
            if task.task_id not in self.dependents:
                self.dependents[task.task_id] = []

            for dep_id in task.dependencies:
                if dep_id not in self.dependents:
                    self.dependents[dep_id] = []
                self.dependents[dep_id].append(task)

    def submit_dag(self):
        with self.lock:
            tasks_list = list(self.tasks.values())
            
            # Wrap actions first so it's visible before scheduling
            for task in tasks_list:
                original_action = task.action
                def make_wrapped(t=task, orig=original_action):
                    def wrapped_action():
                        try:
                            res = orig()
                            self._on_task_completed(t, True)
                            return res
                        except Exception as e:
                            self._on_task_completed(t, False)
                            raise e
                    return wrapped_action
                task.action = make_wrapped()

            for task in tasks_list:
                in_degree = len(task.dependencies)
                if in_degree == 0:
                    self._schedule_task(task)
                else:
                    def make_callback(t=task):
                        return lambda: self._schedule_task(t)
                    self.barriers[task.task_id] = CompletionBarrier(in_degree, make_callback())

    def _schedule_task(self, task: DAGTask):
        self.executor.schedule(task, 0)

    def _on_task_completed(self, task: DAGTask, success: bool):
        if not success:
            return
            
        with self.lock:
            dependents = self.dependents.get(task.task_id, [])
            deps = list(dependents)
            
        for dep in deps:
            self.barriers[dep.task_id].count_down()

class JobScheduler:
    def __init__(self) -> None:
        self.id = "JobScheduler"
        self.executor = ScheduledThreadPoolExecutor(max_workers=4)
        self.executor.start()
        self.dag_scheduler = DAGScheduler(self.executor)

    def describe(self) -> str:
        return f"JobScheduler:{self.id}"
