import time
from typing import Callable, Optional, List
try:
    from .job_status import JobStatus
except ImportError:
    from job_status import JobStatus

class RetryPolicy:
    def __init__(self, max_retries: int = 0, initial_backoff_ms: int = 1000, multiplier: float = 2.0):
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.multiplier = multiplier

class Job:
    def __init__(self, id: str, action: Callable[[], None], 
                 cron_expression: Optional[str] = None,
                 retry_policy: Optional[RetryPolicy] = None,
                 dependencies: Optional[List[str]] = None):
        self.id = id
        self.action = action
        self.cron_expression = cron_expression
        self.retry_policy = retry_policy or RetryPolicy()
        self.dependencies = dependencies or []
        self.status = JobStatus.CREATED
        self.next_execution_time = 0.0
        self.retry_count = 0
        self.execution_history = []

    def increment_retry_count(self) -> None:
        self.retry_count += 1

    def reset_retry_count(self) -> None:
        self.retry_count = 0
        self.execution_history = []

    def get_backoff_delay(self) -> float:
        if self.retry_count == 0:
            return 0.0
        return (self.retry_policy.initial_backoff_ms * (self.retry_policy.multiplier ** (self.retry_count - 1))) / 1000.0

    def add_history(self, entry: str) -> None:
        self.execution_history.append(entry)

    def describe(self) -> str:
        return f"Job:{self.id} [status={self.status.name}]"
