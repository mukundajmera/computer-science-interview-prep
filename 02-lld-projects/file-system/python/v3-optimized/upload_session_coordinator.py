"""Upload session coordinator skeleton for resumable multipart uploads."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List
import uuid


class UploadSessionStatus(Enum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    READY_TO_FINALIZE = "READY_TO_FINALIZE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


@dataclass
class UploadInstruction:
    chunk_index: int
    upload_url: str
    expires_at: datetime


@dataclass
class UploadSessionProgress:
    uploaded_chunks: int
    total_chunks: int
    uploaded_bytes: int


@dataclass
class UploadSessionRecord:
    session_id: str
    user_id: str
    logical_path: str
    total_bytes: int
    chunk_size_bytes: int
    expected_chunk_hashes: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    uploaded_checksums: Dict[int, str] = field(default_factory=dict)
    uploaded_etags: Dict[int, str] = field(default_factory=dict)
    status: UploadSessionStatus = UploadSessionStatus.PENDING
    failure_reason: str = ""

    def total_chunks(self) -> int:
        return len(self.expected_chunk_hashes)


class UploadSessionCoordinator:
    """Coordinates resumable upload state and finalization readiness."""

    def __init__(self) -> None:
        self._sessions: Dict[str, UploadSessionRecord] = {}

    def start_session(
        self,
        user_id: str,
        logical_path: str,
        total_bytes: int,
        chunk_size_bytes: int,
        expected_chunk_hashes: List[str],
    ) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = UploadSessionRecord(
            session_id=session_id,
            user_id=user_id,
            logical_path=logical_path,
            total_bytes=total_bytes,
            chunk_size_bytes=chunk_size_bytes,
            expected_chunk_hashes=expected_chunk_hashes,
        )
        return session_id

    def get_chunk_upload_instruction(self, session_id: str, chunk_index: int) -> UploadInstruction:
        record = self._require_session(session_id)
        record.status = UploadSessionStatus.UPLOADING
        return UploadInstruction(
            chunk_index=chunk_index,
            upload_url=f"https://blob.example/upload/{session_id}/{chunk_index}",
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )

    def mark_chunk_uploaded(self, session_id: str, chunk_index: int, checksum: str, e_tag: str) -> None:
        record = self._require_session(session_id)
        record.uploaded_checksums[chunk_index] = checksum
        record.uploaded_etags[chunk_index] = e_tag
        if self.can_finalize(session_id):
            record.status = UploadSessionStatus.READY_TO_FINALIZE

    def get_session_progress(self, session_id: str) -> UploadSessionProgress:
        record = self._require_session(session_id)
        uploaded_chunks = len(record.uploaded_checksums)
        uploaded_bytes = min(record.total_bytes, uploaded_chunks * record.chunk_size_bytes)
        return UploadSessionProgress(
            uploaded_chunks=uploaded_chunks,
            total_chunks=record.total_chunks(),
            uploaded_bytes=uploaded_bytes,
        )

    def list_missing_chunks(self, session_id: str) -> List[int]:
        record = self._require_session(session_id)
        return [index for index in range(record.total_chunks()) if index not in record.uploaded_checksums]

    def can_finalize(self, session_id: str) -> bool:
        record = self._require_session(session_id)
        return len(record.uploaded_checksums) == record.total_chunks()

    def finalize_session(self, session_id: str) -> str:
        record = self._require_session(session_id)
        if not self.can_finalize(session_id):
            raise ValueError("Upload session is incomplete")
        record.status = UploadSessionStatus.COMPLETED
        return f"blob://{record.user_id}/{record.logical_path}"

    def abort_session(self, session_id: str, reason: str) -> None:
        record = self._require_session(session_id)
        record.status = UploadSessionStatus.FAILED
        record.failure_reason = reason

    def expire_sessions(self, now: datetime) -> int:
        expired = 0
        for record in self._sessions.values():
            if record.status in {UploadSessionStatus.COMPLETED, UploadSessionStatus.FAILED}:
                continue
            if record.created_at + timedelta(hours=24) < now:
                record.status = UploadSessionStatus.EXPIRED
                expired += 1
        return expired

    def _require_session(self, session_id: str) -> UploadSessionRecord:
        record = self._sessions.get(session_id)
        if record is None:
            raise ValueError(f"Unknown session: {session_id}")
        return record
