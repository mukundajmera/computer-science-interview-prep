from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol


class UploadStatus(str, Enum):
    INITIATED = "initiated"
    PARTIAL = "partial"
    COMPLETING = "completing"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass(frozen=True)
class InitUploadCommand:
    owner_id: str
    title: str
    total_bytes: int
    expected_parts: int


@dataclass(frozen=True)
class UploadSession:
    session_id: str
    video_id: str
    status: UploadStatus
    expected_parts: int
    uploaded_parts: int


@dataclass(frozen=True)
class Video:
    video_id: str
    owner_id: str
    status: UploadStatus


@dataclass(frozen=True)
class Manifest:
    video_id: str
    path: str
    state: str


class VideoService(Protocol):
    def init_upload(self, command: InitUploadCommand) -> UploadSession: ...
    def upload_part(self, session_id: str, part_number: int, etag: str) -> UploadSession: ...
    def complete_upload(self, session_id: str, idempotency_key: str) -> Video: ...
    def get_manifest(self, video_id: str) -> Optional[Manifest]: ...
