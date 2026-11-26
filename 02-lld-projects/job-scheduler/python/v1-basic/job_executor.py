import threading
import time
import heapq
from typing import Optional, Callable, List

try:
    from .job import Job
    from .job_status import JobStatus
    from .cron_parser import CronParser
    from .job_store import JobStore
    from .clock import Clock, SystemClock
except ImportError:
    from job import Job
    from job_status import JobStatus
    from cron_parser import CronParser
    from job_store import JobStore
    from clock import Clock, SystemClock

class QueueItem:
    def __init__(self, execution_time: float, job: Job):
        self.execution_time = execution_time
        self.job = job

    def __lt__(self, other):
        if self.execution_time == other.execution_time:
            return self.job.id < other.job.id
        return self.execution_time < other.execution_time

class JobExecutor:
    def __init__(self, job_store: JobStore, clock: Optional[Clock] = None, capacity: int = 1000, max_workers: int = 1):
        self.job_store = job_store
        self.clock = clock or SystemClock()
        self.capacity = capacity
        self.max_workers = max_workers
        self._queue: List[QueueItem] = []
        self._condition = threading.Condition()
        self._running = False
        self._worker_threads: List[threading.Thread] = []
        self._job_completion_callback: Optional[Callable[[Job], None]] = None

    def start(self):
        with self._condition:
            if self._running:
                return
            self._running = True
            for i in range(self.max_workers):
                t = threading.Thread(target=self._worker_loop, daemon=True, name=f"Worker-{i}")
                t.start()
                self._worker_threads.append(t)

    def stop(self):
        with self._condition:
            self._running = False
            self._condition.notify_all()
        for t in self._worker_threads:
            t.join()
        self._worker_threads = []

    def submit(self, job: Job):
        with self._condition:
            if len(self._queue) >= self.capacity:
                raise RuntimeError("Queue is full")
            heapq.heappush(self._queue, QueueItem(job.next_execution_time, job))
            # If this is the new earliest job, notify a worker
            if self._queue[0].job == job:
                self._condition.notify()

    def _worker_loop(self):
        while True:
            with self._condition:
                if not self._running:
                    break

                if not self._queue:
                    self._condition.wait()
                    continue

                now = self.clock.now()
                next_item = self._queue[0]
                
                if next_item.execution_time > now:
                    # Wait until the next job is ready
                    # Wait at most the difference
                    wait_time = next_item.execution_time - now
                    # We might get spurious wakeups or wake up early, which is fine
                    self._condition.wait(wait_time)
                    continue
                
                # Job is ready to execute
                heapq.heappop(self._queue)
                job = next_item.job

                # Prevent executing cancelled jobs
                if job.status == JobStatus.CANCELLED:
                    continue
                
                if job.status not in (JobStatus.SCHEDULED, JobStatus.RETRYING):
                    continue
                
                job.status = JobStatus.RUNNING
                job.add_history(f'Started execution at {self.clock.now()}')
                self.job_store.save_job(job)

            # Execute outside of the lock
            self._execute_job(job)

    def _execute_job(self, job: Job):
        try:
            job.action()
            with self._condition:
                job.status = JobStatus.SUCCEEDED
                job.add_history(f'Execution succeeded at {self.clock.now()}')
                job.reset_retry_count()
        except Exception as e:
            with self._condition:
                job.increment_retry_count()
                if job.retry_count <= job.retry_policy.max_retries:
                    job.status = JobStatus.RETRYING
                    job.add_history(f'Execution failed at {self.clock.now()}, retrying')
                    delay = job.get_backoff_delay()
                    job.next_execution_time = self.clock.now() + delay
                    self.job_store.save_job(job)
                    
                    try:
                        self.submit(job) # Wait this acquires the lock again, which is fine (Reentrant lock? No, self._condition is a Condition which uses RLock). Actually self.submit uses `with self._condition`. It is reentrant.
                    except RuntimeError:
                        # If queue is full, we drop the retry for now (basic implementation limitation)
                        pass 
                    return
                else:
                    job.status = JobStatus.FAILED
                    job.add_history(f'Execution failed permanently at {self.clock.now()}')
        
        self.job_store.save_job(job)

        # Handle Cron rescheduling if successful or max retries reached
        if job.cron_expression and (job.status == JobStatus.SUCCEEDED or job.status == JobStatus.FAILED):
            try:
                next_time = CronParser.get_next_execution_time(job.cron_expression, self.clock.now())
                job.next_execution_time = next_time
                job.status = JobStatus.SCHEDULED
                self.job_store.save_job(job)
                self.submit(job)
            except Exception as e:
                pass # E.g., invalid cron
            except RuntimeError:
                pass # Queue full
                
        if self._job_completion_callback and (job.status == JobStatus.SUCCEEDED or job.status == JobStatus.FAILED):
            self._job_completion_callback(job)

    def set_job_completion_callback(self, callback: Callable[[Job], None]):
        self._job_completion_callback = callback

    def describe(self) -> str:
        return f"JobExecutor: [running={self._running}, queue_size={len(self._queue)}]"
