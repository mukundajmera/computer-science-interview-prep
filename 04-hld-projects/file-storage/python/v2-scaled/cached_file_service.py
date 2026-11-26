"""
File Storage Service - v2-scaled (Python)

Enhancements over v1:
- Distributed caching for metadata and hot files
- CDN integration for static file delivery
- Chunked upload/download for large files
- Background workers for async processing
- Read replicas for metadata queries
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

import time
import asyncio


# ============================================================================
# Core Interfaces
# ============================================================================

class Cache(ABC):
    """Cache interface for metadata caching."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def put(self, key: str, value: Any, ttl_seconds: int) -> None:
        pass
    
    @abstractmethod
    def invalidate(self, key: str) -> None:
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass


class CDNService(ABC):
    """CDN interface for content delivery."""
    
    @abstractmethod
    def get_signed_url(self, file_id: str, expiry_seconds: int) -> str:
        pass
    
    @abstractmethod
    def invalidate_cache(self, file_id: str) -> None:
        pass
    
    @abstractmethod
    def warm_cache(self, file_id: str, object_storage_url: str) -> None:
        pass


class ChunkManager(ABC):
    """Chunk manager for large file uploads."""
    
    @abstractmethod
    def initiate_chunked_upload(
        self, file_id: str, total_size: int, chunk_size: int
    ) -> str:
        pass
    
    @abstractmethod
    def upload_chunk(
        self, upload_id: str, chunk_number: int, data: bytes
    ) -> None:
        pass
    
    @abstractmethod
    def complete_chunked_upload(self, upload_id: str) -> None:
        pass
    
    @abstractmethod
    def abort_chunked_upload(self, upload_id: str) -> None:
        pass
    
    @abstractmethod
    def get_upload_status(self, upload_id: str) -> 'ChunkStatus':
        pass


# ============================================================================
# DTOs
# ============================================================================

@dataclass
class ChunkStatus:
    """Status of a chunked upload."""
    upload_id: str
    uploaded_chunks: List[int]
    pending_chunks: List[int]
    total_size: int
    uploaded_size: int
    
    @property
    def progress_percent(self) -> float:
        if self.total_size == 0:
            return 0.0
        return (self.uploaded_size * 100.0) / self.total_size


@dataclass
class FileMetadataCache:
    """Cached file metadata."""
    file_id: str
    file_name: str
    size: int
    content_type: str
    cdn_url: Optional[str] = None
    cached_at: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class ChunkedUploadRequest:
    """Request to initiate chunked upload."""
    file_name: str
    total_size: int
    content_type: str
    user_id: str
    folder_id: str
    chunk_size_bytes: int = 5 * 1024 * 1024  # 5MB default


@dataclass
class DownloadResponse:
    """Response containing download information."""
    download_url: str
    expires_at: int
    is_cdn_url: bool
    headers: Dict[str, str]


# ============================================================================
# Repository Interface
# ============================================================================

class FileMetadataRepository(ABC):
    """Repository for file metadata with read replica support."""
    
    @abstractmethod
    def save(self, metadata: FileMetadataCache) -> FileMetadataCache:
        pass
    
    @abstractmethod
    def find_by_id(self, file_id: str) -> Optional[FileMetadataCache]:
        pass
    
    @abstractmethod
    def find_by_folder_id(self, folder_id: str) -> List[FileMetadataCache]:
        pass
    
    @abstractmethod
    def delete(self, file_id: str) -> None:
        pass
    
    # Read replica methods for read-heavy operations
    @abstractmethod
    def find_by_id_from_replica(self, file_id: str) -> Optional[FileMetadataCache]:
        pass
    
    @abstractmethod
    def find_by_folder_id_from_replica(
        self, folder_id: str
    ) -> List[FileMetadataCache]:
        pass


# ============================================================================
# Cached File Storage Service
# ============================================================================

class CachedFileStorageService:
    """
    File storage service with caching, CDN, and chunked uploads.
    """
    
    # Configuration
    METADATA_CACHE_TTL = 3600  # 1 hour
    DOWNLOAD_URL_EXPIRY = 3600  # 1 hour
    DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(
        self,
        metadata_repository: FileMetadataRepository,
        metadata_cache: Cache,
        cdn_service: CDNService,
        chunk_manager: ChunkManager
    ):
        self.metadata_repository = metadata_repository
        self.metadata_cache = metadata_cache
        self.cdn_service = cdn_service
        self.chunk_manager = chunk_manager
    
    def get_file_metadata(self, file_id: str) -> Optional[FileMetadataCache]:
        """
        Get file metadata with caching.
        Cache-aside pattern: check cache first, then DB.
        """
        # Check cache first
        cached = self.metadata_cache.get(file_id)
        if cached is not None:
            return cached
        
        # Cache miss - read from replica
        metadata = self.metadata_repository.find_by_id_from_replica(file_id)
        if metadata is not None:
            self.metadata_cache.put(file_id, metadata, self.METADATA_CACHE_TTL)
        
        return metadata
    
    def initiate_chunked_upload(self, request: ChunkedUploadRequest) -> str:
        """
        Initiate chunked upload for large files.
        Returns upload session ID for resumable uploads.
        """
        chunk_size = (
            request.chunk_size_bytes 
            if request.chunk_size_bytes > 0 
            else self.DEFAULT_CHUNK_SIZE
        )
        
        upload_id = self.chunk_manager.initiate_chunked_upload(
            file_id=self._generate_file_id(),
            total_size=request.total_size,
            chunk_size=chunk_size
        )
        
        return upload_id
    
    def upload_chunk(
        self, upload_id: str, chunk_number: int, data: bytes
    ) -> None:
        """
        Upload a single chunk.
        Chunks can be uploaded in parallel and out of order.
        """
        self.chunk_manager.upload_chunk(upload_id, chunk_number, data)
    
    def get_upload_progress(self, upload_id: str) -> ChunkStatus:
        """Get upload progress for resumable uploads."""
        return self.chunk_manager.get_upload_status(upload_id)
    
    def complete_chunked_upload(
        self,
        upload_id: str,
        file_name: str,
        user_id: str,
        folder_id: str
    ) -> FileMetadataCache:
        """
        Complete chunked upload.
        Assembles chunks and creates final file.
        """
        # Complete the upload
        self.chunk_manager.complete_chunked_upload(upload_id)
        
        # Get final status
        status = self.chunk_manager.get_upload_status(upload_id)
        
        # Create metadata
        metadata = FileMetadataCache(
            file_id=upload_id,
            file_name=file_name,
            size=status.total_size,
            content_type=self._detect_content_type(file_name),
            cdn_url=None
        )
        
        # Save to database
        self.metadata_repository.save(metadata)
        
        # Cache the metadata
        self.metadata_cache.put(
            metadata.file_id, metadata, self.METADATA_CACHE_TTL
        )
        
        return metadata
    
    def get_download_url(self, file_id: str) -> DownloadResponse:
        """Get download URL - uses CDN for hot files."""
        metadata = self.get_file_metadata(file_id)
        if metadata is None:
            raise ValueError(f"File not found: {file_id}")
        
        # Generate signed CDN URL
        cdn_url = self.cdn_service.get_signed_url(
            file_id, self.DOWNLOAD_URL_EXPIRY
        )
        
        return DownloadResponse(
            download_url=cdn_url,
            expires_at=int(time.time() * 1000) + (self.DOWNLOAD_URL_EXPIRY * 1000),
            is_cdn_url=True,
            headers={
                "Content-Type": metadata.content_type,
                "Content-Disposition": f'attachment; filename="{metadata.file_name}"'
            }
        )
    
    def delete_file(self, file_id: str, user_id: str) -> None:
        """Delete file with cache invalidation."""
        # Invalidate caches first
        self.metadata_cache.invalidate(file_id)
        self.cdn_service.invalidate_cache(file_id)
        
        # Delete from database (soft delete)
        self.metadata_repository.delete(file_id)
    
    def list_files(self, folder_id: str) -> List[FileMetadataCache]:
        """List files in folder - uses read replica."""
        return self.metadata_repository.find_by_folder_id_from_replica(folder_id)
    
    # ========================================================================
    # Private Helpers
    # ========================================================================
    
    def _generate_file_id(self) -> str:
        """Generate unique file ID."""
        import random
        return f"file_{int(time.time() * 1000)}_{random.randint(0, 9999)}"
    
    def _detect_content_type(self, file_name: str) -> str:
        """Detect content type from file extension."""
        extension_map = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".mp4": "video/mp4",
            ".txt": "text/plain",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        
        for ext, content_type in extension_map.items():
            if file_name.lower().endswith(ext):
                return content_type
        
        return "application/octet-stream"


# ============================================================================
# Background Workers
# ============================================================================

class ThumbnailGenerationWorker:
    """
    Async worker that generates thumbnails for images/videos.
    Triggered after file upload completion.
    """
    
    async def generate_thumbnail(self, file_id: str) -> str:
        """Generate thumbnail asynchronously."""
        # Simulate async work
        await asyncio.sleep(0.1)
        
        # Steps:
        # 1. Download original file
        # 2. Generate thumbnail using image processing library
        # 3. Upload thumbnail to object storage
        # 4. Update metadata with thumbnail URL
        
        return f"thumbnail_{file_id}"


class VirusScanWorker:
    """
    Async worker that scans uploaded files for viruses.
    Runs before file is made publicly accessible.
    """
    
    async def scan_file(self, file_id: str) -> bool:
        """Scan file for viruses asynchronously."""
        # Simulate async work
        await asyncio.sleep(0.1)
        
        # Steps:
        # 1. Download file
        # 2. Run virus scan using external service
        # 3. Update file status (clean/quarantined)
        
        return True  # File is clean


class DeduplicationWorker:
    """
    Worker that detects duplicate files based on content hash.
    Saves storage by reusing existing blobs.
    """
    
    async def check_duplicate(self, content_hash: str) -> Optional[str]:
        """Check if file with same content already exists."""
        # Query blob storage for existing file with same hash
        # If found, return existing blob ID for reuse
        return None


# ============================================================================
# Rate Limiting for Uploads
# ============================================================================

class UploadRateLimiter:
    """Rate limiter for upload operations."""
    
    def __init__(
        self,
        max_uploads_per_minute: int = 10,
        max_bytes_per_hour: int = 10 * 1024 * 1024 * 1024  # 10GB
    ):
        self.max_uploads_per_minute = max_uploads_per_minute
        self.max_bytes_per_hour = max_bytes_per_hour
        self._upload_counts: Dict[str, List[float]] = {}
        self._byte_counts: Dict[str, List[tuple]] = {}
    
    def is_allowed(self, user_id: str, file_size: int) -> bool:
        """Check if upload is allowed under rate limits."""
        current_time = time.time()
        
        # Check upload count limit
        self._cleanup_old_entries(user_id, current_time)
        
        if len(self._upload_counts.get(user_id, [])) >= self.max_uploads_per_minute:
            return False
        
        # Check byte limit
        hour_bytes = sum(
            size for ts, size in self._byte_counts.get(user_id, [])
            if current_time - ts < 3600
        )
        
        if hour_bytes + file_size > self.max_bytes_per_hour:
            return False
        
        return True
    
    def record_upload(self, user_id: str, file_size: int) -> None:
        """Record an upload for rate limiting."""
        current_time = time.time()
        
        if user_id not in self._upload_counts:
            self._upload_counts[user_id] = []
        self._upload_counts[user_id].append(current_time)
        
        if user_id not in self._byte_counts:
            self._byte_counts[user_id] = []
        self._byte_counts[user_id].append((current_time, file_size))
    
    def _cleanup_old_entries(self, user_id: str, current_time: float) -> None:
        """Remove expired entries."""
        if user_id in self._upload_counts:
            self._upload_counts[user_id] = [
                ts for ts in self._upload_counts[user_id]
                if current_time - ts < 60
            ]
        
        if user_id in self._byte_counts:
            self._byte_counts[user_id] = [
                (ts, size) for ts, size in self._byte_counts[user_id]
                if current_time - ts < 3600
            ]
