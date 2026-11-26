import hashlib
import uuid
from typing import Dict, List, Optional
try:
    from .s3_storage_service import S3StorageService
except ImportError:
    from s3_storage_service import S3StorageService

class Part:
    def __init__(self, part_number: int, data: bytes, etag: str):
        self.part_number = part_number
        self.data = data
        self.etag = etag

class MultipartUpload:
    def __init__(self, upload_id: str, bucket_name: str, key: str):
        self.upload_id = upload_id
        self.bucket_name = bucket_name
        self.key = key
        self.parts: Dict[int, Part] = {}

class CompletedPart:
    def __init__(self, part_number: int, etag: str):
        self.part_number = part_number
        self.etag = etag

class MultipartUploadManager:
    def __init__(self, storage_service: S3StorageService):
        self.storage_service = storage_service
        self.uploads: Dict[str, MultipartUpload] = {}

    def initiate_multipart_upload(self, bucket_name: str, key: str) -> str:
        upload_id = str(uuid.uuid4())
        self.uploads[upload_id] = MultipartUpload(upload_id, bucket_name, key)
        return upload_id

    def upload_part(self, upload_id: str, part_number: int, data: bytes) -> str:
        if upload_id not in self.uploads:
            raise ValueError("Upload ID not found")
        if part_number < 1 or part_number > 10000:
            raise ValueError("Invalid part number")

        upload = self.uploads[upload_id]
        etag = self._calculate_md5_etag(data)
        upload.parts[part_number] = Part(part_number, data, etag)
        
        return etag

    def complete_multipart_upload(self, upload_id: str, parts_to_complete: List[CompletedPart]) -> str:
        if upload_id not in self.uploads:
            raise ValueError("Upload ID not found")
            
        upload = self.uploads[upload_id]
        
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
            final_object_data[offset:offset+len(p.data)] = p.data
            offset += len(p.data)
            combined_etag_bytes.extend(bytes.fromhex(p.etag))

        composite_etag_raw = hashlib.md5(combined_etag_bytes).hexdigest()
        composite_etag = f"{composite_etag_raw}-{len(ordered_parts)}"
        
        self.storage_service.put_object_internal(upload.bucket_name, upload.key, bytes(final_object_data), composite_etag)
        
        del self.uploads[upload_id]
        
        return composite_etag

    def abort_multipart_upload(self, upload_id: str) -> None:
        if upload_id not in self.uploads:
            raise ValueError("Upload ID not found")
        del self.uploads[upload_id]

    def _calculate_md5_etag(self, data: bytes) -> str:
        return hashlib.md5(data).hexdigest()
