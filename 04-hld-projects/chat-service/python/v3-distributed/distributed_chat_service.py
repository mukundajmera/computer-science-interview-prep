"""
Chat Service - v3-distributed (Python)

Enhancements over v2:
- Multi-region deployment with geo-routing
- Consistent message ordering with vector clocks
- Multi-device synchronization
- Cross-region replication
- Advanced conflict resolution
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import time
import threading


# ============================================================================
# Multi-Region Interfaces
# ============================================================================

class GeoRouter(ABC):
    """Interface for geo-routing decisions."""
    
    @abstractmethod
    def determine_region(self, client_ip: str) -> str:
        pass
    
    @abstractmethod
    def get_user_home_region(self, user_id: str) -> str:
        pass
    
    @abstractmethod
    def get_replication_targets(self, primary_region: str) -> List[str]:
        pass


class CrossRegionMessaging(ABC):
    """Interface for cross-region message replication."""
    
    @abstractmethod
    def replicate_message(
        self, message_id: int, source_region: str, target_region: str
    ) -> None:
        pass
    
    @abstractmethod
    def sync_conversation(
        self, conversation_id: str, source_region: str, target_region: str
    ) -> None:
        pass


class DistributedIdGenerator(ABC):
    """Interface for distributed ID generation."""
    
    @abstractmethod
    def generate_id(self) -> int:
        pass
    
    @abstractmethod
    def generate_id_for_region(self, region: str) -> int:
        pass


@dataclass(frozen=True)
class SessionBinding:
    user_id: str
    device_id: str
    region: str
    connection_id: str


class PresenceSessionRegistry(ABC):
    """Tracks active sessions across devices and regions."""

    @abstractmethod
    def register_device(
        self, user_id: str, device_id: str, region: str, connection_id: str
    ) -> None:
        pass

    @abstractmethod
    def heartbeat(self, user_id: str, device_id: str, timestamp_ms: int) -> None:
        pass

    @abstractmethod
    def active_sessions(self, user_id: str) -> List[SessionBinding]:
        pass


# ============================================================================
# Vector Clock for Ordering
# ============================================================================

class VectorClock:
    """
    Vector clock for tracking causality in distributed systems.
    """
    
    def __init__(self, clock: Optional[Dict[str, int]] = None):
        self.clock: Dict[str, int] = dict(clock) if clock else {}
    
    def increment(self, node_id: str) -> None:
        """Increment the clock for a node."""
        self.clock[node_id] = self.clock.get(node_id, 0) + 1
    
    def merge(self, other: 'VectorClock') -> None:
        """Merge with another vector clock (take max)."""
        for node_id, value in other.clock.items():
            self.clock[node_id] = max(self.clock.get(node_id, 0), value)
    
    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this clock happens before another."""
        at_least_one_less = False
        
        for key in self.clock:
            this_value = self.clock.get(key, 0)
            other_value = other.clock.get(key, 0)
            
            if this_value > other_value:
                return False
            if this_value < other_value:
                at_least_one_less = True
        
        return at_least_one_less
    
    def is_concurrent(self, other: 'VectorClock') -> bool:
        """Check if two events are concurrent."""
        return not self.happens_before(other) and not other.happens_before(self)
    
    def get_clock(self) -> Dict[str, int]:
        """Get a copy of the clock."""
        return dict(self.clock)


# ============================================================================
# Distributed Message
# ============================================================================

@dataclass
class DistributedMessage:
    """A message with distributed ordering information."""
    message_id: int  # Snowflake ID
    conversation_id: str
    sender_id: str
    content: str
    vector_clock: VectorClock
    origin_region: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivery_status: Dict[str, int] = field(default_factory=dict)
    
    def mark_delivered_in_region(self, region: str) -> None:
        """Mark message as delivered in a region."""
        self.delivery_status[region] = int(time.time() * 1000)


# ============================================================================
# Device Sync
# ============================================================================

@dataclass
class DeviceSync:
    """Sync state for a device."""
    user_id: str
    device_id: str
    last_sync_timestamp: int = 0
    conversation_cursors: Dict[str, int] = field(default_factory=dict)
    
    def update_cursor(self, conversation_id: str, message_id: int) -> None:
        """Update the sync cursor for a conversation."""
        self.conversation_cursors[conversation_id] = message_id
        self.last_sync_timestamp = int(time.time() * 1000)


@dataclass
class SyncResponse:
    """Response to a sync request."""
    new_messages: List[DistributedMessage]
    updated_cursors: Dict[str, int]
    sync_timestamp: int


# ============================================================================
# Snowflake ID Generator
# ============================================================================

class SnowflakeIdGenerator(DistributedIdGenerator):
    """
    Snowflake ID generator for globally unique, time-ordered IDs.
    
    Structure:
    | Timestamp (41 bits) | Datacenter (5 bits) | Worker (5 bits) | Sequence (12 bits) |
    """
    
    EPOCH = 1609459200000  # Jan 1, 2021
    WORKER_ID_BITS = 5
    DATACENTER_ID_BITS = 5
    SEQUENCE_BITS = 12
    
    MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1
    MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1
    
    def __init__(self, worker_id: int, datacenter_id: int):
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"Worker ID must be between 0 and {self.MAX_WORKER_ID}")
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}")
        
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()
    
    def generate_id(self) -> int:
        """Generate a unique ID."""
        with self._lock:
            timestamp = self._current_time_millis()
            
            if timestamp < self.last_timestamp:
                raise RuntimeError("Clock moved backwards")
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp
            
            return (
                ((timestamp - self.EPOCH) << (self.WORKER_ID_BITS + self.DATACENTER_ID_BITS + self.SEQUENCE_BITS))
                | (self.datacenter_id << (self.WORKER_ID_BITS + self.SEQUENCE_BITS))
                | (self.worker_id << self.SEQUENCE_BITS)
                | self.sequence
            )
    
    def generate_id_for_region(self, region: str) -> int:
        """Generate ID using region-specific configuration."""
        return self.generate_id()
    
    def _current_time_millis(self) -> int:
        return int(time.time() * 1000)
    
    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._current_time_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_time_millis()
        return timestamp


# ============================================================================
# Distributed Chat Service
# ============================================================================

class DistributedChatService:
    """
    Chat service with multi-region support and consistent ordering.
    """
    
    def __init__(
        self,
        geo_router: GeoRouter,
        cross_region_messaging: CrossRegionMessaging,
        id_generator: DistributedIdGenerator,
        current_region: str
    ):
        self.geo_router = geo_router
        self.cross_region_messaging = cross_region_messaging
        self.id_generator = id_generator
        self.current_region = current_region
        
        # Per-conversation vector clocks
        self.conversation_clocks: Dict[str, VectorClock] = {}
        
        # Message storage (in production: distributed database)
        self._messages: Dict[int, DistributedMessage] = {}
    
    async def send_message(
        self,
        sender_id: str,
        conversation_id: str,
        content: str
    ) -> DistributedMessage:
        """Send message with global ordering."""
        
        # Get or create vector clock for conversation
        clock = self.conversation_clocks.setdefault(
            conversation_id, VectorClock()
        )
        
        # Increment clock for this region
        clock.increment(self.current_region)
        
        # Generate globally unique, time-ordered ID
        message_id = self.id_generator.generate_id_for_region(self.current_region)
        
        # Create distributed message
        message = DistributedMessage(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            vector_clock=VectorClock(clock.get_clock()),
            origin_region=self.current_region
        )
        
        # Persist locally
        self._persist_message(message)
        
        # Replicate to other regions asynchronously
        await self._replicate_async(message)
        
        return message
    
    def sync_device(
        self, user_id: str, device_id: str, device_sync: DeviceSync
    ) -> SyncResponse:
        """Sync device across all conversations."""
        new_messages: List[DistributedMessage] = []
        updated_cursors: Dict[str, int] = {}
        
        # Get all conversations for user
        conversation_ids = self._get_conversations_for_user(user_id)
        
        for conversation_id in conversation_ids:
            last_seen_id = device_sync.conversation_cursors.get(conversation_id, 0)
            
            # Get messages after last seen
            messages = self._get_messages_after(conversation_id, last_seen_id)
            new_messages.extend(messages)
            
            if messages:
                updated_cursors[conversation_id] = messages[-1].message_id
        
        # Sort by global ordering
        new_messages.sort(key=lambda m: m.message_id)
        
        return SyncResponse(
            new_messages=new_messages,
            updated_cursors=updated_cursors,
            sync_timestamp=int(time.time() * 1000)
        )
    
    def handle_replicated_message(self, message: DistributedMessage) -> None:
        """Handle message received from another region."""
        # Get local clock
        local_clock = self.conversation_clocks.setdefault(
            message.conversation_id, VectorClock()
        )
        
        # Check for conflicts
        if local_clock.is_concurrent(message.vector_clock):
            self._handle_conflict(message, local_clock)
        
        # Merge clocks
        local_clock.merge(message.vector_clock)
        
        # Persist and deliver locally
        self._persist_message(message)
        self._deliver_locally(message)
    
    def _handle_conflict(
        self, incoming: DistributedMessage, local_clock: VectorClock
    ) -> None:
        """Handle concurrent message conflict."""
        # Strategy: Use message ID as tiebreaker
        print(f"Concurrent message detected for {incoming.conversation_id}")
    
    def _persist_message(self, message: DistributedMessage) -> None:
        """Persist message to storage."""
        self._messages[message.message_id] = message
    
    async def _replicate_async(self, message: DistributedMessage) -> None:
        """Replicate message to other regions."""
        targets = self.geo_router.get_replication_targets(self.current_region)
        
        tasks = []
        for target_region in targets:
            tasks.append(
                self._replicate_to_region(message, target_region)
            )
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _replicate_to_region(
        self, message: DistributedMessage, target_region: str
    ) -> None:
        """Replicate single message to a region."""
        self.cross_region_messaging.replicate_message(
            message.message_id,
            self.current_region,
            target_region
        )
    
    def _deliver_locally(self, message: DistributedMessage) -> None:
        """Deliver message to local users."""
        pass
    
    def _get_conversations_for_user(self, user_id: str) -> List[str]:
        """Get all conversation IDs for a user."""
        return []
    
    def _get_messages_after(
        self, conversation_id: str, after_id: int
    ) -> List[DistributedMessage]:
        """Get messages after a given ID."""
        return [
            m for m in self._messages.values()
            if m.conversation_id == conversation_id and m.message_id > after_id
        ]


# ============================================================================
# Multi-Region Connection Manager
# ============================================================================

class MultiRegionConnectionManager:
    """
    Manages connections across multiple regions.
    """
    
    def __init__(self, geo_router: GeoRouter, local_region: str):
        self.geo_router = geo_router
        self.local_region = local_region
        self.region_pools: Dict[str, Any] = {}
    
    def route_connection(self, user_id: str, client_ip: str) -> str:
        """Route user to appropriate region."""
        # Try user's home region first
        home_region = self.geo_router.get_user_home_region(user_id)
        
        # Fallback to nearest region if home is overloaded
        if self._is_region_overloaded(home_region):
            return self.geo_router.determine_region(client_ip)
        
        return home_region
    
    async def deliver_to_user(self, user_id: str, message: str) -> bool:
        """Deliver message to user across regions."""
        user_region = self.geo_router.get_user_home_region(user_id)
        
        if user_region == self.local_region:
            return await self._deliver_locally(user_id, message)
        else:
            return await self._forward_to_region(user_region, user_id, message)
    
    def _is_region_overloaded(self, region: str) -> bool:
        """Check if a region is overloaded."""
        return False
    
    async def _deliver_locally(self, user_id: str, message: str) -> bool:
        """Deliver to local user."""
        return True
    
    async def _forward_to_region(
        self, region: str, user_id: str, message: str
    ) -> bool:
        """Forward message to another region."""
        return True


# ============================================================================
# Conflict Resolution
# ============================================================================

class ConflictResolutionStrategy(Enum):
    """Strategies for resolving message conflicts."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"


class ConflictResolver:
    """
    Resolves conflicts in distributed message ordering.
    """
    
    def __init__(self, strategy: ConflictResolutionStrategy):
        self.strategy = strategy
    
    def resolve(
        self, messages: List[DistributedMessage]
    ) -> List[DistributedMessage]:
        """Resolve ordering of concurrent messages."""
        
        if self.strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            # Order by message ID (includes timestamp)
            return sorted(messages, key=lambda m: m.message_id)
        
        elif self.strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
            return sorted(messages, key=lambda m: m.message_id, reverse=True)
        
        else:
            # Merge: keep all, order by ID
            return sorted(messages, key=lambda m: m.message_id)


# ============================================================================
# Cross-Region Health Monitor
# ============================================================================

class RegionHealthMonitor:
    """
    Monitors health of regions for routing decisions.
    """
    
    def __init__(self, regions: List[str]):
        self.regions = regions
        self._health_scores: Dict[str, float] = {r: 1.0 for r in regions}
    
    def update_health(self, region: str, latency_ms: float, error_rate: float) -> None:
        """Update health score for a region."""
        # Simple health calculation
        health = 1.0 - (latency_ms / 1000.0) - error_rate
        self._health_scores[region] = max(0.0, min(1.0, health))
    
    def get_health(self, region: str) -> float:
        """Get health score for a region."""
        return self._health_scores.get(region, 0.0)
    
    def get_healthiest_region(self) -> str:
        """Get the healthiest region."""
        return max(self._health_scores, key=self._health_scores.get)
    
    def is_healthy(self, region: str, threshold: float = 0.5) -> bool:
        """Check if a region is healthy."""
        return self._health_scores.get(region, 0.0) >= threshold


# ============================================================================
# Pattern Integration Hooks (Real-time transport, contention, workflow durability)
# ============================================================================

class DeliveryMode(Enum):
    POLLING = "POLLING"
    LONG_POLLING = "LONG_POLLING"
    SSE = "SSE"
    WEBSOCKET = "WEBSOCKET"
    # WebRTC can be layered for media handoff when P2P is acceptable.


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
