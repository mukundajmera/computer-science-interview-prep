from typing import Optional, List, Set, Dict
import threading
try:
    from .job import Job
    from .job_status import JobStatus
    from .job_store import JobStore
    from .in_memory_job_store import InMemoryJobStore
    from .job_executor import JobExecutor
    from .cron_parser import CronParser
    from .clock import Clock, SystemClock
except ImportError:
    from job import Job
    from job_status import JobStatus
    from job_store import JobStore
    from in_memory_job_store import InMemoryJobStore
    from job_executor import JobExecutor
    from cron_parser import CronParser
    from clock import Clock, SystemClock

class JobScheduler:
    def __init__(self, job_store: Optional[JobStore] = None, clock: Optional[Clock] = None, executor_capacity: int = 1000, executor_workers: int = 1, executor: Optional[JobExecutor] = None):
        self.job_store = job_store or InMemoryJobStore()
        self.clock = clock or SystemClock()
        self.executor = executor or JobExecutor(self.job_store, clock=self.clock, capacity=executor_capacity, max_workers=executor_workers)
        self.executor.set_job_completion_callback(self._on_job_completed)
        self._lock = threading.Lock()
        
        # Keep track of jobs that depend on a specific job ID
        self._dependent_jobs: Dict[str, List[str]] = {}

    def start(self):
        self.executor.start()

    def stop(self):
        self.executor.stop()

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self.job_store.get_job(job_id)
            if not job:
                return False
            
            # Can only cancel jobs that are not currently running/succeeded
            if job.status in [JobStatus.CREATED, JobStatus.SCHEDULED, JobStatus.RETRYING]:
                job.status = JobStatus.CANCELLED
                job.add_history(f'Cancelled at {self.clock.now()}')
                self.job_store.save_job(job)
                
                # Cascade cancel to dependents? The design doc says if parent fails permanently, child is stuck in CREATED. 
                # Let's let it remain in CREATED or CANCELLED based on later manual intervention, as per DESIGN.md: "remaining stuck in CREATED or manually CANCELLED".
                return True
            return False

    def schedule_job(self, job: Job) -> None:
        with self._lock:
            # 1. Validate dependencies exist
            for dep_id in job.dependencies:
                if not self.job_store.get_job(dep_id):
                    raise ValueError(f"Missing dependency: {dep_id}")
            
            # 2. Cycle detection via DFS
            self.job_store.save_job(job) # Temporarily save to check cycles
            if self._has_cycle(job.id):
                self.job_store.remove_job(job.id)
                raise ValueError("Cycle detected in job dependencies")
                
            # Update inverse dependency map
            for dep_id in job.dependencies:
                if dep_id not in self._dependent_jobs:
                    self._dependent_jobs[dep_id] = []
                if job.id not in self._dependent_jobs[dep_id]:
                    self._dependent_jobs[dep_id].append(job.id)

            if job.cron_expression:
                job.next_execution_time = CronParser.get_next_execution_time(job.cron_expression, self.clock.now())
            else:
                if job.next_execution_time == 0.0:
                    job.next_execution_time = self.clock.now()
            
            self.job_store.save_job(job)

            # Check if parents are all SUCCEEDED
            if self._are_dependencies_met(job):
                job.status = JobStatus.SCHEDULED
                self.job_store.save_job(job)
                self.executor.submit(job)
            else:
                job.status = JobStatus.CREATED
                self.job_store.save_job(job)

    def _has_cycle(self, start_job_id: str) -> bool:
        visited = set()
        stack = set()

        def dfs(job_id: str) -> bool:
            if job_id in stack:
                return True
            if job_id in visited:
                return False

            visited.add(job_id)
            stack.add(job_id)

            job = self.job_store.get_job(job_id)
            if job:
                for dep_id in job.dependencies:
                    if dfs(dep_id):
                        return True
            
            stack.remove(job_id)
            return False

        # Check for all jobs to be safe, or just from start_job_id
        # Actually checking from all jobs is safer
        for job in self.job_store.get_all_jobs():
            if dfs(job.id):
                return True
        return False

    def _are_dependencies_met(self, job: Job) -> bool:
        for dep_id in job.dependencies:
            dep_job = self.job_store.get_job(dep_id)
            if not dep_job or dep_job.status != JobStatus.SUCCEEDED:
                return False
        return True

    def _on_job_completed(self, completed_job: Job) -> None:
        if completed_job.status == JobStatus.SUCCEEDED:
            with self._lock:
                dependents = self._dependent_jobs.get(completed_job.id, [])
                for child_id in dependents:
                    child_job = self.job_store.get_job(child_id)
                    if child_job and child_job.status == JobStatus.CREATED:
                        if self._are_dependencies_met(child_job):
                            child_job.status = JobStatus.SCHEDULED
                            self.job_store.save_job(child_job)
                            self.executor.submit(child_job)

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.job_store.get_job(job_id)

    def describe(self) -> str:
        return f"JobScheduler: [store={self.job_store.describe()}, executor={self.executor.describe()}]"
