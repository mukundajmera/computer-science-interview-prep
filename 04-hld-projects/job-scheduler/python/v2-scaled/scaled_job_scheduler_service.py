import uuid
import heapq
import threading
import time
from enum import Enum
from typing import Callable, Dict, Optional, List, Set, Any

class JobStatus(Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    DEAD_LETTER = "DEAD_LETTER"
    WAITING_DEPENDENCIES = "WAITING_DEPENDENCIES"

class Job:
    def __init__(self, task: Callable[[], None], periodic: bool, period_ms: int, max_retries: int, initial_backoff_ms: int, dependencies: List[str] = None):
        self.id = str(uuid.uuid4())
        self.task = task
        self.periodic = periodic
        self.period_ms = period_ms
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.dependencies = set(dependencies) if dependencies else set()

        self.status = JobStatus.WAITING_DEPENDENCIES if self.dependencies else JobStatus.SCHEDULED
        self.attempt = 0
        self.lease_owner = None
        self.lease_until = 0
        self.executor_thread = None

class JobExecution:
    def __init__(self, job: Job, scheduled_time_ms: int):
        self.job = job
        self.scheduled_time_ms = scheduled_time_ms

    def __lt__(self, other):
        return self.scheduled_time_ms < other.scheduled_time_ms

class ScaledJobSchedulerService:
    def __init__(self, lease_duration_ms: int = 5000):
        self._queue = []
        self._jobs: Dict[str, Job] = {}
        self._workers = {} # worker_id -> last_heartbeat_ms
        self._is_running = True
        self._lock = threading.Condition()
        self._lease_duration_ms = lease_duration_ms
        self._dead_letter_queue = []
        self._dispatcher = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._coordinator = threading.Thread(target=self._coordinator_loop, daemon=True)
        self._dispatcher.start()
        self._coordinator.start()

    def submit_one_off_job(self, task: Callable[[], None], delay_ms: int, max_retries: int, initial_backoff_ms: int, dependencies: List[str] = None) -> str:
        job = Job(task, periodic=False, period_ms=0, max_retries=max_retries, initial_backoff_ms=initial_backoff_ms, dependencies=dependencies)
        scheduled_time = int(time.time() * 1000) + delay_ms
        with self._lock:
            self._jobs[job.id] = job
            self._check_dependencies_and_schedule(job, scheduled_time)
        return job.id

    def submit_periodic_job(self, task: Callable[[], None], initial_delay_ms: int, period_ms: int, max_retries: int, initial_backoff_ms: int) -> str:
        job = Job(task, periodic=True, period_ms=period_ms, max_retries=max_retries, initial_backoff_ms=initial_backoff_ms)
        scheduled_time = int(time.time() * 1000) + initial_delay_ms
        with self._lock:
            self._jobs[job.id] = job
            self._check_dependencies_and_schedule(job, scheduled_time)
        return job.id

    def _check_dependencies_and_schedule(self, job: Job, scheduled_time_ms: int):
        if not job.dependencies:
            if job.status == JobStatus.WAITING_DEPENDENCIES:
                job.status = JobStatus.SCHEDULED
            heapq.heappush(self._queue, JobExecution(job, scheduled_time_ms))
            self._lock.notify_all()
        else:
            all_met = True
            for dep_id in job.dependencies:
                dep_job = self._jobs.get(dep_id)
                if not dep_job or dep_job.status != JobStatus.SUCCEEDED:
                    all_met = False
                    break
            if all_met:
                job.status = JobStatus.SCHEDULED
                heapq.heappush(self._queue, JobExecution(job, scheduled_time_ms))
                self._lock.notify_all()

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status not in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED):
                job.status = JobStatus.CANCELLED
                return True
        return False

    def pause_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status in (JobStatus.SCHEDULED, JobStatus.WAITING_DEPENDENCIES, JobStatus.RETRYING):
                job.status = JobStatus.PAUSED
                return True
        return False

    def resume_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status == JobStatus.PAUSED:
                if job.dependencies:
                    job.status = JobStatus.WAITING_DEPENDENCIES
                else:
                    job.status = JobStatus.SCHEDULED
                self._check_dependencies_and_schedule(job, int(time.time() * 1000))
                return True
        return False

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        with self._lock:
            job = self._jobs.get(job_id)
            return job.status if job else None

    def get_dead_letter_queue(self):
        with self._lock:
            return list(self._dead_letter_queue)

    def register_worker(self, worker_id: str):
        with self._lock:
            self._workers[worker_id] = int(time.time() * 1000)

    def heartbeat(self, worker_id: str):
        with self._lock:
            if worker_id in self._workers:
                self._workers[worker_id] = int(time.time() * 1000)

    def _coordinator_loop(self):
        while self._is_running:
            time.sleep(0.1)
            now = int(time.time() * 1000)
            with self._lock:
                # Evict dead workers
                dead_workers = [wid for wid, last_hb in self._workers.items() if now - last_hb > self._lease_duration_ms * 2]
                for wid in dead_workers:
                    del self._workers[wid]

                # Reassign expired leases
                for job in self._jobs.values():
                    if job.status == JobStatus.RUNNING and job.lease_owner in dead_workers:
                        job.status = JobStatus.RETRYING
                        job.lease_owner = None
                        heapq.heappush(self._queue, JobExecution(job, now))
                        self._lock.notify_all()
                    elif job.status == JobStatus.RUNNING and job.lease_until < now:
                        job.status = JobStatus.RETRYING
                        job.lease_owner = None
                        # Stop the old executor thread if possible (in this case we just leave it running since Python threads cannot be forcefully killed easily, but we schedule a new one)
                        heapq.heappush(self._queue, JobExecution(job, now))
                        self._lock.notify_all()

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
        if job.status in (JobStatus.CANCELLED, JobStatus.PAUSED, JobStatus.DEAD_LETTER, JobStatus.SUCCEEDED, JobStatus.FAILED):
            return

        worker_id = None
        if self._workers:
            worker_id = list(self._workers.keys())[0]

        job.status = JobStatus.RUNNING
        job.lease_owner = worker_id
        job.lease_until = int(time.time() * 1000) + self._lease_duration_ms

        def runner():
            try:
                job.task()
                with self._lock:
                    if job.status == JobStatus.RUNNING: # Avoid marking successful if cancelled or reassigned
                        job.attempt = 0
                        job.lease_owner = None
                        if job.periodic:
                            job.status = JobStatus.SCHEDULED
                            next_time = int(time.time() * 1000) + job.period_ms
                            self._check_dependencies_and_schedule(job, next_time)
                        else:
                            job.status = JobStatus.SUCCEEDED
                            # Check dependent jobs
                            for dep_job in self._jobs.values():
                                if job.id in dep_job.dependencies and dep_job.status == JobStatus.WAITING_DEPENDENCIES:
                                    self._check_dependencies_and_schedule(dep_job, int(time.time() * 1000))
            except Exception as e:
                with self._lock:
                    if job.status == JobStatus.RUNNING:
                        job.attempt += 1
                        job.lease_owner = None
                        if job.attempt <= job.max_retries:
                            job.status = JobStatus.RETRYING
                            backoff = job.initial_backoff_ms * (1 << (job.attempt - 1))
                            next_time = int(time.time() * 1000) + backoff
                            self._check_dependencies_and_schedule(job, next_time)
                        else:
                            job.status = JobStatus.DEAD_LETTER
                            self._dead_letter_queue.append((job.id, str(e)))

        job.executor_thread = threading.Thread(target=runner, daemon=True)
        job.executor_thread.start()

    def shutdown(self):
        self._is_running = False
        with self._lock:
            self._lock.notify_all()
