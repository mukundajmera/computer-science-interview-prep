"""
File Storage Service - V1 Basic

Core file storage service implementation in Python.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from abc import ABC, abstractmethod
import uuid
import hashlib


@dataclass
class FileMetadata:
    """File metadata entity."""
    file_id: str
    user_id: str
    filename: str
    content_type: str
    size_bytes: int
    content_hash: str
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    parent_folder_id: Optional[str] = None
    is_folder: bool = False
    is_deleted: bool = False
    
    @staticmethod
    def create(user_id: str, filename: str, content_type: str,
               size_bytes: int, content_hash: str) -> 'FileMetadata':
        return FileMetadata(
            file_id=str(uuid.uuid4()),
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            content_hash=content_hash
        )
    
    def increment_version(self):
        self.version += 1
        self.updated_at = datetime.utcnow()
    
    def mark_deleted(self):
        self.is_deleted = True
        self.updated_at = datetime.utcnow()


class BlockStorage(ABC):
    """Block storage interface."""
    
    @abstractmethod
    def store(self, data: bytes) -> str:
        pass
    
    @abstractmethod
    def retrieve(self, block_id: str) -> Optional[bytes]:
        pass
    
    @abstractmethod
    def delete(self, block_id: str) -> None:
        pass


class FileMetadataRepository(ABC):
    """Metadata repository interface."""
    
    @abstractmethod
    def save(self, metadata: FileMetadata) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, file_id: str) -> Optional[FileMetadata]:
        pass
    
    @abstractmethod
    def find_by_user_and_parent(self, user_id: str, 
                               parent_folder_id: Optional[str]) -> List[FileMetadata]:
        pass


class FileStorageService(ABC):
    """File storage service interface."""
    
    @abstractmethod
    def upload(self, user_id: str, filename: str, content_type: str,
               content: bytes) -> FileMetadata:
        pass
    
    @abstractmethod
    def download(self, file_id: str, user_id: str) -> bytes:
        pass
    
    @abstractmethod
    def delete(self, file_id: str, user_id: str) -> bool:
        pass
    
    @abstractmethod
    def list_files(self, user_id: str, folder_id: Optional[str]) -> List[FileMetadata]:
        pass


class BasicFileStorageService(FileStorageService):
    """Basic file storage service implementation."""
    
    def __init__(self, metadata_repository: FileMetadataRepository,
                 block_storage: BlockStorage):
        self._metadata_repository = metadata_repository
        self._block_storage = block_storage
    
    def upload(self, user_id: str, filename: str, content_type: str,
               content: bytes) -> FileMetadata:
        # Calculate content hash
        content_hash = self._calculate_hash(content)
        
        # Store content
        self._block_storage.store(content)
        
        # Create metadata
        metadata = FileMetadata.create(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            content_hash=content_hash
        )
        
        self._metadata_repository.save(metadata)
        return metadata
    
    def download(self, file_id: str, user_id: str) -> bytes:
        metadata = self._metadata_repository.find_by_id(file_id)
        
        if not metadata:
            raise FileNotFoundError(f"File not found: {file_id}")
        
        if metadata.user_id != user_id:
            raise PermissionError("Access denied")
        
        if metadata.is_deleted:
            raise FileNotFoundError("File has been deleted")
        
        content = self._block_storage.retrieve(metadata.content_hash)
        if content is None:
            raise FileNotFoundError("File content not found")
        
        return content
    
    def delete(self, file_id: str, user_id: str) -> bool:
        metadata = self._metadata_repository.find_by_id(file_id)
        
        if not metadata:
            return False
        
        if metadata.user_id != user_id:
            raise PermissionError("Access denied")
        
        metadata.mark_deleted()
        self._metadata_repository.save(metadata)
        return True
    
    def list_files(self, user_id: str, folder_id: Optional[str]) -> List[FileMetadata]:
        return self._metadata_repository.find_by_user_and_parent(user_id, folder_id)
    
    def _calculate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()


class InMemoryBlockStorage(BlockStorage):
    """In-memory block storage."""
    
    def __init__(self):
        self._storage: Dict[str, bytes] = {}
    
    def store(self, data: bytes) -> str:
        block_id = str(uuid.uuid4())
        self._storage[block_id] = data
        return block_id
    
    def retrieve(self, block_id: str) -> Optional[bytes]:
        return self._storage.get(block_id)
    
    def delete(self, block_id: str) -> None:
        self._storage.pop(block_id, None)


class InMemoryFileMetadataRepository(FileMetadataRepository):
    """In-memory metadata repository."""
    
    def __init__(self):
        self._files: Dict[str, FileMetadata] = {}
    
    def save(self, metadata: FileMetadata) -> None:
        self._files[metadata.file_id] = metadata
    
    def find_by_id(self, file_id: str) -> Optional[FileMetadata]:
        return self._files.get(file_id)
    
    def find_by_user_and_parent(self, user_id: str,
                               parent_folder_id: Optional[str]) -> List[FileMetadata]:
        return [
            f for f in self._files.values()
            if f.user_id == user_id
            and not f.is_deleted
            and f.parent_folder_id == parent_folder_id
        ]
