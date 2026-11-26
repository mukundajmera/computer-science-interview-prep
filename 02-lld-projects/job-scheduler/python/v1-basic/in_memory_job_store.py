from typing import List, Dict, Optional
import threading
try:
    from .job_store import JobStore
    from .job import Job
except ImportError:
    from job_store import JobStore
    from job import Job

class InMemoryJobStore(JobStore):
    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def save_job(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.id] = job

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def get_all_jobs(self) -> List[Job]:
        with self._lock:
            return list(self._jobs.values())
            
    def remove_job(self, job_id: str) -> None:
        with self._lock:
            if job_id in self._jobs:
                del self._jobs[job_id]

    def describe(self) -> str:
        with self._lock:
            return f"InMemoryJobStore: {len(self._jobs)} jobs"
