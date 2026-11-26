import uuid
import heapq
import threading
import time
from enum import Enum
from typing import Callable, Dict, Optional

class JobStatus(Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"

class Job:
    def __init__(self, task: Callable[[], None], periodic: bool, period_ms: int, max_retries: int, initial_backoff_ms: int):
        self.id = str(uuid.uuid4())
        self.task = task
        self.periodic = periodic
        self.period_ms = period_ms
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms

        self.status = JobStatus.SCHEDULED
        self.attempt = 0

class JobExecution:
    def __init__(self, job: Job, scheduled_time_ms: int):
        self.job = job
        self.scheduled_time_ms = scheduled_time_ms

    def __lt__(self, other):
        return self.scheduled_time_ms < other.scheduled_time_ms

class JobSchedulerService:
    def __init__(self):
        self._queue = []
        self._jobs: Dict[str, Job] = {}
        self._is_running = True
        self._lock = threading.Condition()
        self._dispatcher = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._dispatcher.start()

    def submit_one_off_job(self, task: Callable[[], None], delay_ms: int, max_retries: int, initial_backoff_ms: int) -> str:
        job = Job(task, periodic=False, period_ms=0, max_retries=max_retries, initial_backoff_ms=initial_backoff_ms)
        scheduled_time = int(time.time() * 1000) + delay_ms
        return self._schedule_job(job, scheduled_time)

    def submit_periodic_job(self, task: Callable[[], None], initial_delay_ms: int, period_ms: int, max_retries: int, initial_backoff_ms: int) -> str:
        job = Job(task, periodic=True, period_ms=period_ms, max_retries=max_retries, initial_backoff_ms=initial_backoff_ms)
        scheduled_time = int(time.time() * 1000) + initial_delay_ms
        return self._schedule_job(job, scheduled_time)

    def _schedule_job(self, job: Job, scheduled_time_ms: int) -> str:
        with self._lock:
            self._jobs[job.id] = job
            heapq.heappush(self._queue, JobExecution(job, scheduled_time_ms))
            self._lock.notify_all()
        return job.id

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                if job.status not in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED):
                    job.status = JobStatus.CANCELLED
                    return True
        return False

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.status if job else None

    def _dispatch_loop(self):
        while self._is_running:
            with self._lock:
                if not self._queue:
                    self._lock.wait()
                    continue

                now = int(time.time() * 1000)
                execution = self._queue[0]

                if execution.scheduled_time_ms <= now:
                    heapq.heappop(self._queue)
                    self._execute_job(execution.job)
                else:
                    time_to_wait = (execution.scheduled_time_ms - now) / 1000.0
                    self._lock.wait(timeout=time_to_wait)

    def _execute_job(self, job: Job):
        if job.status == JobStatus.CANCELLED:
            return

        def runner():
            if job.status == JobStatus.CANCELLED:
                return

            job.status = JobStatus.RUNNING
            try:
                job.task()
                job.attempt = 0
                if job.periodic:
                    if job.status != JobStatus.CANCELLED:
                        job.status = JobStatus.SCHEDULED
                        next_time = int(time.time() * 1000) + job.period_ms
                        self._schedule_job(job, next_time)
                else:
                    job.status = JobStatus.SUCCEEDED
            except Exception:
                job.attempt += 1
                if job.attempt <= job.max_retries:
                    if job.status != JobStatus.CANCELLED:
                        job.status = JobStatus.RETRYING
                        backoff = job.initial_backoff_ms * (1 << (job.attempt - 1))
                        next_time = int(time.time() * 1000) + backoff
                        self._schedule_job(job, next_time)
                else:
                    job.status = JobStatus.FAILED

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

    def shutdown(self):
        self._is_running = False
        with self._lock:
            self._lock.notify_all()
