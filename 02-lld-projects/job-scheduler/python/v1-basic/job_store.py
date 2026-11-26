from abc import ABC, abstractmethod
from typing import List, Optional
try:
    from .job import Job
except ImportError:
    from job import Job

class JobStore(ABC):
    @abstractmethod
    def save_job(self, job: Job) -> None:
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Job]:
        pass

    @abstractmethod
    def get_all_jobs(self) -> List[Job]:
        pass
        
    @abstractmethod
    def remove_job(self, job_id: str) -> None:
        pass
