"""
File Storage Service - v3-distributed (Python)

Enhancements over v2:
- Multi-region deployment with geo-routing
- Cross-region replication for disaster recovery
- Distributed locking for concurrent operations
- Event-driven architecture with message queues
- Advanced conflict resolution for shared files
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import time
import asyncio
import hashlib
import uuid


# ============================================================================
# Multi-Region Interfaces
# ============================================================================

class GeoRouter(ABC):
    """Interface for geo-routing decisions."""
    
    @abstractmethod
    def determine_region(self, user_id: str) -> str:
        pass
    
    @abstractmethod
    def get_nearest_region(self, client_ip: str) -> str:
        pass
    
    @abstractmethod
    def get_replication_targets(self, primary_region: str) -> List[str]:
        pass


class CrossRegionReplicator(ABC):
    """Interface for cross-region data replication."""
    
    @abstractmethod
    def replicate_metadata(
        self, file_id: str, source_region: str, target_region: str
    ) -> None:
        pass
    
    @abstractmethod
    def replicate_blob(
        self, file_id: str, source_region: str, target_region: str
    ) -> None:
        pass
    
    @abstractmethod
    def get_replication_status(self, file_id: str) -> 'ReplicationStatus':
        pass


class DistributedLock(ABC):
    """Interface for distributed locking."""
    
    @abstractmethod
    def acquire(self, lock_key: str, timeout_ms: int) -> bool:
        pass
    
    @abstractmethod
    def release(self, lock_key: str) -> None:
        pass
    
    @abstractmethod
    def extend(self, lock_key: str, additional_time_ms: int) -> bool:
        pass


class EventBus(ABC):
    """Interface for event-driven communication."""
    
    @abstractmethod
    def publish(self, topic: str, event: 'FileEvent') -> None:
        pass
    
    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[['FileEvent'], None]) -> None:
        pass


# ============================================================================
# Event-Driven DTOs
# ============================================================================

class EventType(Enum):
    """Types of file events."""
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FILE_SHARED = "file_shared"
    FILE_MOVED = "file_moved"
    FILE_VERSIONED = "file_versioned"
    SYNC_REQUESTED = "sync_requested"


@dataclass
class FileEvent:
    """Event representing a file operation."""
    type: EventType
    file_id: str
    user_id: str
    region: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


class ReplicationStatusEnum(Enum):
    """Status of replication to a region."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReplicationStatus:
    """Status of file replication across regions."""
    file_id: str
    region_status: Dict[str, ReplicationStatusEnum]
    last_updated: int = field(default_factory=lambda: int(time.time() * 1000))
    
    def is_fully_replicated(self) -> bool:
        return all(
            status == ReplicationStatusEnum.COMPLETED 
            for status in self.region_status.values()
        )


# ============================================================================
# Conflict Resolution
# ============================================================================

class ResolutionStrategy(Enum):
    """Strategies for resolving version conflicts."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    MERGE_VERSIONS = "merge_versions"


@dataclass
class FileVersion:
    """A specific version of a file."""
    version_id: str
    file_id: str
    version_number: int
    size: int
    checksum: str
    modified_by: str
    modified_at: int
    region: str


class ConflictResolver:
    """Resolver for file version conflicts."""
    
    def resolve_conflict(
        self,
        conflicting_versions: List[FileVersion],
        strategy: ResolutionStrategy
    ) -> FileVersion:
        """Resolve conflicts when same file is modified in multiple regions."""
        
        if strategy == ResolutionStrategy.LAST_WRITE_WINS:
            return max(conflicting_versions, key=lambda v: v.modified_at)
        
        elif strategy == ResolutionStrategy.FIRST_WRITE_WINS:
            return min(conflicting_versions, key=lambda v: v.modified_at)
        
        elif strategy == ResolutionStrategy.MERGE_VERSIONS:
            return self._create_conflict_copies(conflicting_versions)
        
        else:
            return self._mark_for_manual_resolution(conflicting_versions)
    
    def _create_conflict_copies(
        self, versions: List[FileVersion]
    ) -> FileVersion:
        """Create copies with conflict suffix."""
        # Return the latest as primary
        return max(versions, key=lambda v: v.modified_at)
    
    def _mark_for_manual_resolution(
        self, versions: List[FileVersion]
    ) -> FileVersion:
        """Flag all versions for user review."""
        return versions[0]


# ============================================================================
# Supporting Classes
# ============================================================================

class SharePermission(Enum):
    """Permission levels for shared files."""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    FULL_ACCESS = "full_access"


@dataclass
class ShareResult:
    """Result of sharing a file."""
    file_id: str
    shared_with: str
    permission: SharePermission
    share_link: str = field(
        default_factory=lambda: f"https://files.example.com/share/{uuid.uuid4()}"
    )


@dataclass
class DownloadResult:
    """Result of a download request."""
    file_id: str
    region: str
    download_url: str


class SyncOperationType(Enum):
    """Types of sync operations."""
    DOWNLOAD = "download"
    UPLOAD = "upload"
    DELETE = "delete"
    RENAME = "rename"


@dataclass
class SyncOperation:
    """A single sync operation."""
    type: SyncOperationType
    file_id: str
    path: str


@dataclass
class SyncResponse:
    """Response to a sync request."""
    operations: List[SyncOperation]
    sync_timestamp: int
    total_changes: int


class ConflictException(Exception):
    """Exception raised when a file conflict is detected."""
    
    def __init__(self, message: str, conflicting_version: FileVersion):
        super().__init__(message)
        self.conflicting_version = conflicting_version


# ============================================================================
# Distributed File Storage Service
# ============================================================================

class DistributedFileStorageService:
    """
    File storage service with multi-region support.
    """
    
    # Topics for event-driven communication
    TOPIC_FILE_EVENTS = "file-events"
    TOPIC_SYNC_EVENTS = "sync-events"
    
    def __init__(
        self,
        geo_router: GeoRouter,
        replicator: CrossRegionReplicator,
        distributed_lock: DistributedLock,
        event_bus: EventBus,
        conflict_resolver: ConflictResolver,
        current_region: str
    ):
        self.geo_router = geo_router
        self.replicator = replicator
        self.distributed_lock = distributed_lock
        self.event_bus = event_bus
        self.conflict_resolver = conflict_resolver
        self.current_region = current_region
        
        # Subscribe to sync events
        self._setup_event_handlers()
    
    def upload_file(
        self,
        user_id: str,
        file_name: str,
        content: bytes,
        folder_id: str
    ) -> FileVersion:
        """Upload file with multi-region replication."""
        lock_key = f"upload:{user_id}:{file_name}"
        
        # Acquire distributed lock
        if not self.distributed_lock.acquire(lock_key, 30000):
            raise RuntimeError("Could not acquire lock for upload")
        
        try:
            # Create version in primary region
            version = self._create_file_version(user_id, file_name, content)
            
            # Publish event for async replication
            self.event_bus.publish(
                self.TOPIC_FILE_EVENTS,
                FileEvent(
                    type=EventType.FILE_UPLOADED,
                    file_id=version.file_id,
                    user_id=user_id,
                    region=self.current_region,
                    metadata={"fileName": file_name, "size": len(content)}
                )
            )
            
            # Trigger async replication to other regions
            self._trigger_async_replication(version)
            
            return version
        finally:
            self.distributed_lock.release(lock_key)
    
    def download_file(self, file_id: str, client_ip: str) -> DownloadResult:
        """
        Download file with geo-routing.
        Routes to nearest region with the file.
        """
        # Determine nearest region
        nearest_region = self.geo_router.get_nearest_region(client_ip)
        
        # Check if file is available in nearest region
        status = self.replicator.get_replication_status(file_id)
        
        if self._is_available_in_region(status, nearest_region):
            return self._download_from_region(file_id, nearest_region)
        else:
            return self._download_from_region(file_id, self.current_region)
    
    def update_file(
        self,
        file_id: str,
        user_id: str,
        new_content: bytes,
        expected_checksum: str
    ) -> FileVersion:
        """Update file with conflict detection."""
        lock_key = f"update:{file_id}"
        
        if not self.distributed_lock.acquire(lock_key, 30000):
            raise RuntimeError("File is being modified by another user")
        
        try:
            # Check for conflicts
            current_version = self._get_current_version(file_id)
            
            if current_version.checksum != expected_checksum:
                raise ConflictException(
                    "File was modified since last read",
                    current_version
                )
            
            # Create new version
            new_version = self._create_new_version(
                file_id,
                user_id,
                new_content,
                current_version.version_number + 1
            )
            
            # Publish update event
            self.event_bus.publish(
                self.TOPIC_FILE_EVENTS,
                FileEvent(
                    type=EventType.FILE_VERSIONED,
                    file_id=file_id,
                    user_id=user_id,
                    region=self.current_region,
                    metadata={"version": new_version.version_number}
                )
            )
            
            return new_version
        finally:
            self.distributed_lock.release(lock_key)
    
    def sync_device(
        self,
        user_id: str,
        device_id: str,
        last_sync_timestamp: int
    ) -> SyncResponse:
        """Sync device - returns changes since last sync."""
        # Get all changes for user since last sync
        changes = self._get_changes_since(user_id, last_sync_timestamp)
        
        # Calculate delta
        operations = self._calculate_sync_operations(changes)
        
        return SyncResponse(
            operations=operations,
            sync_timestamp=int(time.time() * 1000),
            total_changes=len(operations)
        )
    
    def share_file(
        self,
        file_id: str,
        owner_id: str,
        target_user_id: str,
        permission: SharePermission
    ) -> ShareResult:
        """Share file with another user across regions."""
        # Determine target user's primary region
        target_region = self.geo_router.determine_region(target_user_id)
        
        # Create share record
        result = self._create_share(file_id, owner_id, target_user_id, permission)
        
        # Ensure file is replicated to target's region
        if target_region != self.current_region:
            self.replicator.replicate_metadata(
                file_id, self.current_region, target_region
            )
            self.replicator.replicate_blob(
                file_id, self.current_region, target_region
            )
        
        # Publish share event
        self.event_bus.publish(
            self.TOPIC_FILE_EVENTS,
            FileEvent(
                type=EventType.FILE_SHARED,
                file_id=file_id,
                user_id=owner_id,
                region=self.current_region,
                metadata={
                    "targetUser": target_user_id,
                    "permission": permission.value
                }
            )
        )
        
        return result
    
    # ========================================================================
    # Event Handlers
    # ========================================================================
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers for incoming events."""
        
        def file_event_handler(event: FileEvent) -> None:
            if event.region != self.current_region:
                self._handle_remote_event(event)
        
        self.event_bus.subscribe(self.TOPIC_FILE_EVENTS, file_event_handler)
        self.event_bus.subscribe(self.TOPIC_SYNC_EVENTS, self._handle_sync_request)
    
    def _handle_remote_event(self, event: FileEvent) -> None:
        """Handle events from other regions."""
        if event.type in (EventType.FILE_UPLOADED, EventType.FILE_VERSIONED):
            # Pull file from source region
            self.replicator.replicate_blob(
                event.file_id,
                event.region,
                self.current_region
            )
        elif event.type == EventType.FILE_DELETED:
            self._soft_delete_local(event.file_id)
    
    def _handle_sync_request(self, event: FileEvent) -> None:
        """Process sync request from another device."""
        pass
    
    # ========================================================================
    # Private Helpers
    # ========================================================================
    
    def _create_file_version(
        self,
        user_id: str,
        file_name: str,
        content: bytes
    ) -> FileVersion:
        """Create a new file version."""
        file_id = self._generate_file_id()
        checksum = self._calculate_checksum(content)
        
        return FileVersion(
            version_id=self._generate_version_id(),
            file_id=file_id,
            version_number=1,
            size=len(content),
            checksum=checksum,
            modified_by=user_id,
            modified_at=int(time.time() * 1000),
            region=self.current_region
        )
    
    def _create_new_version(
        self,
        file_id: str,
        user_id: str,
        content: bytes,
        version_number: int
    ) -> FileVersion:
        """Create a new version of an existing file."""
        return FileVersion(
            version_id=self._generate_version_id(),
            file_id=file_id,
            version_number=version_number,
            size=len(content),
            checksum=self._calculate_checksum(content),
            modified_by=user_id,
            modified_at=int(time.time() * 1000),
            region=self.current_region
        )
    
    def _trigger_async_replication(self, version: FileVersion) -> None:
        """Trigger async replication to other regions."""
        targets = self.geo_router.get_replication_targets(self.current_region)
        
        for target_region in targets:
            # In production, this would be truly async
            asyncio.create_task(
                self._replicate_to_region(version.file_id, target_region)
            )
    
    async def _replicate_to_region(
        self, file_id: str, target_region: str
    ) -> None:
        """Async helper for replication."""
        self.replicator.replicate_blob(
            file_id,
            self.current_region,
            target_region
        )
    
    def _is_available_in_region(
        self,
        status: Optional[ReplicationStatus],
        region: str
    ) -> bool:
        """Check if file is available in a region."""
        return (
            status is not None and
            status.region_status.get(region) == ReplicationStatusEnum.COMPLETED
        )
    
    def _download_from_region(
        self, file_id: str, region: str
    ) -> DownloadResult:
        """Get download URL for a specific region."""
        return DownloadResult(
            file_id=file_id,
            region=region,
            download_url=self._generate_signed_url(file_id, region)
        )
    
    def _get_current_version(self, file_id: str) -> FileVersion:
        """Fetch current version from database."""
        # Placeholder - would fetch from database
        return FileVersion(
            version_id="",
            file_id=file_id,
            version_number=1,
            size=0,
            checksum="",
            modified_by="",
            modified_at=0,
            region=self.current_region
        )
    
    def _get_changes_since(
        self, user_id: str, timestamp: int
    ) -> List[FileEvent]:
        """Query event store for changes."""
        return []  # Placeholder
    
    def _calculate_sync_operations(
        self, changes: List[FileEvent]
    ) -> List[SyncOperation]:
        """Convert events to sync operations."""
        return []  # Placeholder
    
    def _create_share(
        self,
        file_id: str,
        owner_id: str,
        target_user_id: str,
        permission: SharePermission
    ) -> ShareResult:
        """Create a share record."""
        return ShareResult(
            file_id=file_id,
            shared_with=target_user_id,
            permission=permission
        )
    
    def _soft_delete_local(self, file_id: str) -> None:
        """Mark file as deleted locally."""
        pass
    
    def _generate_file_id(self) -> str:
        """Generate unique file ID."""
        return f"file_{self.current_region}_{int(time.time() * 1000)}"
    
    def _generate_version_id(self) -> str:
        """Generate unique version ID."""
        return f"ver_{int(time.time() * 1000)}"
    
    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate SHA-256 checksum."""
        return hashlib.sha256(content).hexdigest()
    
    def _generate_signed_url(self, file_id: str, region: str) -> str:
        """Generate signed download URL."""
        return f"https://{region}.storage.example.com/{file_id}?signed=..."


# ============================================================================
# Additional Distributed Components
# ============================================================================

class ConsistencyChecker:
    """
    Periodically checks consistency across regions.
    Detects and repairs inconsistencies.
    """
    
    def __init__(self, replicator: CrossRegionReplicator, regions: List[str]):
        self.replicator = replicator
        self.regions = regions
    
    async def check_file_consistency(self, file_id: str) -> Dict[str, Any]:
        """Check if file is consistent across all regions."""
        status = self.replicator.get_replication_status(file_id)
        
        inconsistent_regions = [
            region for region, s in status.region_status.items()
            if s != ReplicationStatusEnum.COMPLETED
        ]
        
        return {
            "file_id": file_id,
            "is_consistent": len(inconsistent_regions) == 0,
            "inconsistent_regions": inconsistent_regions
        }
    
    async def repair_inconsistency(
        self, file_id: str, source_region: str, target_region: str
    ) -> bool:
        """Repair inconsistency by re-replicating from source."""
        try:
            self.replicator.replicate_blob(file_id, source_region, target_region)
            return True
        except Exception:
            return False


class QuotaManager:
    """
    Manages storage quotas per user across regions.
    """
    
    def __init__(self, default_quota_bytes: int = 15 * 1024 * 1024 * 1024):
        self.default_quota_bytes = default_quota_bytes  # 15GB default
        self._user_usage: Dict[str, int] = {}
        self._user_quotas: Dict[str, int] = {}
    
    def check_quota(self, user_id: str, file_size: int) -> bool:
        """Check if user has enough quota for file."""
        quota = self._user_quotas.get(user_id, self.default_quota_bytes)
        usage = self._user_usage.get(user_id, 0)
        return usage + file_size <= quota
    
    def consume_quota(self, user_id: str, file_size: int) -> None:
        """Record quota consumption."""
        current = self._user_usage.get(user_id, 0)
        self._user_usage[user_id] = current + file_size
    
    def release_quota(self, user_id: str, file_size: int) -> None:
        """Release quota when file is deleted."""
        current = self._user_usage.get(user_id, 0)
        self._user_usage[user_id] = max(0, current - file_size)
    
    def get_usage(self, user_id: str) -> Dict[str, Any]:
        """Get quota usage for user."""
        quota = self._user_quotas.get(user_id, self.default_quota_bytes)
        usage = self._user_usage.get(user_id, 0)
        
        return {
            "user_id": user_id,
            "quota_bytes": quota,
            "used_bytes": usage,
            "available_bytes": quota - usage,
            "usage_percent": (usage * 100.0) / quota if quota > 0 else 0
        }


# ============================================================================
# Pattern Integration Hooks (Real-time transport, contention, workflow durability)
# ============================================================================

class DeliveryMode(Enum):
    POLLING = "POLLING"
    LONG_POLLING = "LONG_POLLING"
    SSE = "SSE"
    WEBSOCKET = "WEBSOCKET"
    # WebRTC can be layered for peer-to-peer upload/download negotiation if needed.


class ContentionPolicy(Enum):
    OPTIMISTIC = "OPTIMISTIC"
    PESSIMISTIC = "PESSIMISTIC"
    SERIAL_QUEUE = "SERIAL_QUEUE"
    DISTRIBUTED_LOCK = "DISTRIBUTED_LOCK"


@dataclass
class ExecutionResult:
    success: bool
    checkpoint_id: Optional[str] = None
    error_message: Optional[str] = None
    retryable: bool = False


class WorkflowStep(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def execute(self) -> ExecutionResult:
        ...


class CompensationStep(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def compensate(self, checkpoint_id: Optional[str]) -> None:
        ...


class WorkflowOrchestrator(ABC):
    @abstractmethod
    def run_step(self, step: WorkflowStep, idempotency_key: str, store: "IdempotencyStore") -> ExecutionResult:
        ...

    @abstractmethod
    def register_compensation(self, checkpoint_id: str, compensation_step: CompensationStep) -> None:
        ...


class IdempotencyStore(ABC):
    @abstractmethod
    def has_processed(self, key: str) -> bool:
        ...

    @abstractmethod
    def mark_processed(self, key: str, result: ExecutionResult) -> None:
        ...

    @abstractmethod
    def get_result(self, key: str) -> Optional[ExecutionResult]:
        ...
