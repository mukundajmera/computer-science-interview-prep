"""Long-running job tracker skeleton with idempotency, retries, and DLQ."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import uuid


class JobStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"


class JobType(Enum):
    VIRUS_SCAN = "file-fast"
    THUMBNAIL_GEN = "file-slow"
    METADATA_EXTRACT = "file-fast"


@dataclass
class JobRecord:
    job_id: str
    idempotency_key: str
    job_type: JobType
    payload_ref: str
    attempt: int = 0
    max_attempts: int = 5
    status: JobStatus = JobStatus.QUEUED
    claimed_by: str = ""
    next_visible_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result_ref: str = ""
    last_error_code: str = ""
    dead_letter_reason: str = ""


class LongRunningJobTracker:
    """Tracks async jobs and exposes queue-health primitives."""

    def __init__(self) -> None:
        self._jobs_by_id: Dict[str, JobRecord] = {}
        self._jobs_by_key: Dict[str, str] = {}
        self._queues: Dict[str, List[str]] = {}
        self._dead_letter: List[str] = []

    def submit_job(self, idempotency_key: str, job_type: JobType, payload_ref: str) -> str:
        existing = self.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return existing.job_id

        job_id = str(uuid.uuid4())
        record = JobRecord(job_id=job_id, idempotency_key=idempotency_key, job_type=job_type, payload_ref=payload_ref)
        self._jobs_by_id[job_id] = record
        self._jobs_by_key[idempotency_key] = job_id
        self._queues.setdefault(job_type.value, []).append(job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        return self._jobs_by_id.get(job_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[JobRecord]:
        job_id = self._jobs_by_key.get(idempotency_key)
        return self._jobs_by_id.get(job_id) if job_id else None

    def claim_next(self, worker_id: str, queue_name: str, visibility_timeout_sec: int) -> Optional[JobRecord]:
        queue = self._queues.get(queue_name, [])
        if not queue:
            return None

        job_id = queue.pop(0)
        record = self._require_job(job_id)
        record.status = JobStatus.RUNNING
        record.claimed_by = worker_id
        record.next_visible_at = datetime.utcnow() + timedelta(seconds=visibility_timeout_sec)
        record.last_heartbeat_at = datetime.utcnow()
        return record

    def heartbeat(self, job_id: str, worker_id: str) -> None:
        record = self._require_job(job_id)
        if record.claimed_by != worker_id:
            raise ValueError("Worker does not own this job")
        record.last_heartbeat_at = datetime.utcnow()

    def mark_succeeded(self, job_id: str, result_ref: str) -> None:
        record = self._require_job(job_id)
        record.status = JobStatus.SUCCEEDED
        record.result_ref = result_ref
        record.finished_at = datetime.utcnow()

    def mark_failed(self, job_id: str, error_code: str, retryable: bool) -> None:
        record = self._require_job(job_id)
        record.last_error_code = error_code
        record.attempt += 1

        if (not retryable) or record.attempt >= record.max_attempts:
            self.move_to_dead_letter(job_id, "retry-limit-or-non-retryable")
            return

        record.status = JobStatus.QUEUED
        record.next_visible_at = datetime.utcnow() + timedelta(seconds=5 * record.attempt)
        self._queues.setdefault(record.job_type.value, []).append(job_id)

    def retry_timed_out_claims(self, now: datetime) -> int:
        requeued = 0
        for record in self._jobs_by_id.values():
            if record.status == JobStatus.RUNNING and record.next_visible_at and record.next_visible_at < now:
                record.status = JobStatus.QUEUED
                record.claimed_by = ""
                self._queues.setdefault(record.job_type.value, []).append(record.job_id)
                requeued += 1
        return requeued

    def move_to_dead_letter(self, job_id: str, reason: str) -> None:
        record = self._require_job(job_id)
        record.status = JobStatus.DEAD_LETTER
        record.dead_letter_reason = reason
        self._dead_letter.append(job_id)

    def queue_depth(self, queue_name: str) -> int:
        return len(self._queues.get(queue_name, []))

    def _require_job(self, job_id: str) -> JobRecord:
        record = self._jobs_by_id.get(job_id)
        if record is None:
            raise ValueError(f"Unknown job: {job_id}")
        return record
