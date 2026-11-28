"""v2-extended multipart upload manager.

Improvement over v1-basic (named per the repo rule v1-basic -> v2-extended):
3. Multipart lifecycle expiry (FOLLOW-UPS #2): an abandoned multipart upload
   leaks its uploaded parts forever. v2 stamps every upload with a creation
   time from an injectable clock and adds a configurable TTL plus
   sweep_expired_uploads(), the simulation of the background GC daemon that
   reclaims uploads older than the threshold and reports the bytes freed.

Items 1 (chunks-before-metadata) and 2 (integrity + scrubber) live in
s3_storage_service_v2.py; completion goes through that service's
chunks-first commit path, so assembled objects get the same guarantees.
"""

import hashlib
import time
import uuid
from typing import Dict, List, Optional, Tuple
try:
    from .s3_storage_service_v2 import S3StorageService
except ImportError:
    from s3_storage_service_v2 import S3StorageService


class Part:
    def __init__(self, part_number: int, data: bytes, etag: str):
        self.part_number = part_number
        self.data = data
        self.etag = etag


class MultipartUpload:
    def __init__(self, upload_id: str, bucket_name: str, key: str, created_at: float):
        self.upload_id = upload_id
        self.bucket_name = bucket_name
        self.key = key
        self.created_at = created_at
        self.parts: Dict[int, Part] = {}

    def stored_bytes(self) -> int:
        return sum(len(p.data) for p in self.parts.values())


class CompletedPart:
    def __init__(self, part_number: int, etag: str):
        self.part_number = part_number
        self.etag = etag


class MultipartUploadManager:
    def __init__(self, storage_service: S3StorageService,
                 upload_ttl_seconds: Optional[float] = None, clock=None):
        if upload_ttl_seconds is not None and upload_ttl_seconds <= 0:
            raise ValueError("upload_ttl_seconds must be positive or None")
        self.storage_service = storage_service
        self.upload_ttl_seconds = upload_ttl_seconds
        self._clock = clock if clock is not None else time.time
        self.uploads: Dict[str, MultipartUpload] = {}

    def initiate_multipart_upload(self, bucket_name: str, key: str) -> str:
        upload_id = str(uuid.uuid4())
        self.uploads[upload_id] = MultipartUpload(upload_id, bucket_name, key, self._clock())
        return upload_id

    def upload_part(self, upload_id: str, part_number: int, data: bytes) -> str:
        upload = self._live_upload(upload_id)
        if part_number < 1 or part_number > 10000:
            raise ValueError("Invalid part number")

        etag = self._calculate_md5_etag(data)
        upload.parts[part_number] = Part(part_number, data, etag)

        return etag

    def complete_multipart_upload(self, upload_id: str, parts_to_complete: List[CompletedPart]) -> str:
        upload = self._live_upload(upload_id)

        previous_part_number = 0
        total_size = 0
        ordered_parts: List[Part] = []

        for completed_part in parts_to_complete:
            part_number = completed_part.part_number
            if part_number <= previous_part_number:
                raise ValueError("Part numbers must be in ascending order")

            if part_number not in upload.parts:
                raise ValueError(f"Part number {part_number} not found")

            part = upload.parts[part_number]
            if part.etag != completed_part.etag:
                raise ValueError(f"Invalid ETag for part {part_number}")

            previous_part_number = part_number
            total_size += len(part.data)
            ordered_parts.append(part)

        final_object_data = bytearray(total_size)
        combined_etag_bytes = bytearray()

        offset = 0
        for p in ordered_parts:
            final_object_data[offset:offset + len(p.data)] = p.data
            offset += len(p.data)
            combined_etag_bytes.extend(bytes.fromhex(p.etag))

        composite_etag_raw = hashlib.md5(combined_etag_bytes).hexdigest()
        composite_etag = f"{composite_etag_raw}-{len(ordered_parts)}"

        self.storage_service.put_object_internal(upload.bucket_name, upload.key,
                                                 bytes(final_object_data), composite_etag)

        del self.uploads[upload_id]

        return composite_etag

    def abort_multipart_upload(self, upload_id: str) -> None:
        if upload_id not in self.uploads:
            raise ValueError("Upload ID not found")
        del self.uploads[upload_id]

    def sweep_expired_uploads(self) -> Tuple[List[str], int]:
        """GC daemon pass (v2 item 3): remove uploads older than the TTL and
        reclaim their part data. Returns (expired upload ids, bytes freed).
        With no TTL configured, nothing expires (v1 parity)."""
        if self.upload_ttl_seconds is None:
            return ([], 0)
        now = self._clock()
        expired = [
            upload_id for upload_id, upload in self.uploads.items()
            if now - upload.created_at > self.upload_ttl_seconds
        ]
        freed = 0
        for upload_id in expired:
            freed += self.uploads[upload_id].stored_bytes()
            del self.uploads[upload_id]
        return (expired, freed)

    def _live_upload(self, upload_id: str) -> MultipartUpload:
        upload = self.uploads.get(upload_id)
        if upload is None:
            raise ValueError("Upload ID not found")
        if (self.upload_ttl_seconds is not None
                and self._clock() - upload.created_at > self.upload_ttl_seconds):
            raise ValueError("Upload ID expired")
        return upload

    def _calculate_md5_etag(self, data: bytes) -> str:
        return hashlib.md5(data).hexdigest()
