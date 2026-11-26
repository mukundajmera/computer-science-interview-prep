"""
Chat Service - v2-scaled (Python)

Enhancements over v1:
- Message queue for reliable async delivery
- Group chat with fan-out
- Read receipts and delivery status
- Presence service
- Connection scaling across multiple servers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Callable
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# Infrastructure Interfaces
# ============================================================================

class MessageQueue(ABC):
    """Interface for message queue operations."""
    
    @abstractmethod
    def publish(self, topic: str, message: bytes) -> None:
        pass
    
    @abstractmethod
    def subscribe(self, topic: str, consumer: Callable[[bytes], None]) -> None:
        pass


class Cache(ABC):
    """Interface for cache operations."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        pass
    
    @abstractmethod
    def publish(self, channel: str, message: str) -> None:
        pass
    
    @abstractmethod
    def subscribe(
        self, channel: str, callback: Callable[[str, str], None]
    ) -> None:
        pass


# ============================================================================
# DTOs
# ============================================================================

class MessageStatusEnum(Enum):
    """Message delivery status."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class PresenceStatus(Enum):
    """User presence status."""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"


@dataclass
class MessageStatus:
    """Status of message delivery per recipient."""
    message_id: str
    recipient_status: Dict[str, MessageStatusEnum] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def mark_delivered(self, user_id: str) -> None:
        self.recipient_status[user_id] = MessageStatusEnum.DELIVERED
        self.updated_at = datetime.utcnow()
    
    def mark_read(self, user_id: str) -> None:
        self.recipient_status[user_id] = MessageStatusEnum.READ
        self.updated_at = datetime.utcnow()


@dataclass
class DeliveryTask:
    """Task for async message delivery."""
    message_id: str
    conversation_id: str
    sender_id: str
    recipient_ids: List[str]
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    
    def increment_retry(self) -> None:
        self.retry_count += 1


@dataclass
class UserPresence:
    """User presence information."""
    user_id: str
    status: PresenceStatus = PresenceStatus.OFFLINE
    last_seen: datetime = field(default_factory=datetime.utcnow)
    connected_devices: Set[str] = field(default_factory=set)
    ws_server_id: Optional[str] = None


# ============================================================================
# Presence Service
# ============================================================================

class PresenceService(ABC):
    """Interface for presence operations."""
    
    @abstractmethod
    def set_online(
        self, user_id: str, device_id: str, ws_server_id: str
    ) -> None:
        pass
    
    @abstractmethod
    def set_offline(self, user_id: str, device_id: str) -> None:
        pass
    
    @abstractmethod
    def get_presence(self, user_id: str) -> UserPresence:
        pass
    
    @abstractmethod
    def get_presence_bulk(self, user_ids: List[str]) -> Dict[str, UserPresence]:
        pass
    
    @abstractmethod
    def heartbeat(self, user_id: str, device_id: str) -> None:
        pass


class RedisPresenceService(PresenceService):
    """Redis-based presence service."""
    
    PRESENCE_TTL = 300  # 5 minutes
    
    def __init__(self, cache: Cache):
        self.cache = cache
    
    def set_online(
        self, user_id: str, device_id: str, ws_server_id: str
    ) -> None:
        key = f"presence:{user_id}"
        value = f'{{"status": "online", "ws_server": "{ws_server_id}"}}'
        self.cache.set(key, value, self.PRESENCE_TTL)
        
        # Notify subscribers
        self.cache.publish("presence_updates", f"{user_id}:online")
    
    def set_offline(self, user_id: str, device_id: str) -> None:
        key = f"presence:{user_id}"
        timestamp = datetime.utcnow().isoformat()
        value = f'{{"status": "offline", "last_seen": "{timestamp}"}}'
        self.cache.set(key, value, self.PRESENCE_TTL * 12)
        
        self.cache.publish("presence_updates", f"{user_id}:offline")
    
    def get_presence(self, user_id: str) -> UserPresence:
        key = f"presence:{user_id}"
        value = self.cache.get(key)
        return self._parse_presence(user_id, value)
    
    def get_presence_bulk(self, user_ids: List[str]) -> Dict[str, UserPresence]:
        return {uid: self.get_presence(uid) for uid in user_ids}
    
    def heartbeat(self, user_id: str, device_id: str) -> None:
        key = f"presence:{user_id}"
        existing = self.cache.get(key)
        if existing:
            self.cache.set(key, existing, self.PRESENCE_TTL)
    
    def _parse_presence(
        self, user_id: str, value: Optional[str]
    ) -> UserPresence:
        presence = UserPresence(user_id=user_id)
        if value and "online" in value:
            presence.status = PresenceStatus.ONLINE
        return presence


# ============================================================================
# Connection Registry
# ============================================================================

class ConnectionRegistry(ABC):
    """Registry for tracking user connections."""
    
    @abstractmethod
    def register(
        self, user_id: str, device_id: str, ws_server_id: str
    ) -> None:
        pass
    
    @abstractmethod
    def unregister(self, user_id: str, device_id: str) -> None:
        pass
    
    @abstractmethod
    def get_ws_server(self, user_id: str) -> Optional[str]:
        pass
    
    @abstractmethod
    def push_to_user(
        self, ws_server_id: str, user_id: str, message: str
    ) -> bool:
        pass


class RedisConnectionRegistry(ConnectionRegistry):
    """Redis-based connection registry."""
    
    def __init__(self, cache: Cache):
        self.cache = cache
    
    def register(
        self, user_id: str, device_id: str, ws_server_id: str
    ) -> None:
        key = f"conn:{user_id}"
        self.cache.set(key, ws_server_id, 3600)
    
    def unregister(self, user_id: str, device_id: str) -> None:
        key = f"conn:{user_id}"
        self.cache.delete(key)
    
    def get_ws_server(self, user_id: str) -> Optional[str]:
        return self.cache.get(f"conn:{user_id}")
    
    def push_to_user(
        self, ws_server_id: str, user_id: str, message: str
    ) -> bool:
        # Route through Redis pub/sub to correct WS server
        self.cache.publish(f"ws:{ws_server_id}", f"{user_id}:{message}")
        return True


# ============================================================================
# Async Message Service
# ============================================================================

class AsyncMessageService:
    """Message service with async delivery."""
    
    DELIVERY_TOPIC = "message_delivery"
    FANOUT_TOPIC = "message_fanout"
    
    def __init__(
        self,
        message_queue: MessageQueue,
        presence_service: PresenceService,
        cache: Cache
    ):
        self.message_queue = message_queue
        self.presence_service = presence_service
        self.cache = cache
    
    async def send_message(
        self,
        sender_id: str,
        conversation_id: str,
        content: str,
        recipient_ids: List[str]
    ) -> str:
        """Send message with async delivery."""
        message_id = str(uuid.uuid4())
        
        task = DeliveryTask(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            recipient_ids=recipient_ids,
            content=content
        )
        
        # Enqueue for delivery
        self.message_queue.publish(
            self.DELIVERY_TOPIC, 
            self._serialize(task)
        )
        
        # Update status
        self._update_status(message_id, MessageStatusEnum.SENT)
        
        return message_id
    
    async def send_group_message(
        self,
        sender_id: str,
        group_id: str,
        content: str,
        member_ids: List[str]
    ) -> str:
        """Send group message with fan-out."""
        message_id = str(uuid.uuid4())
        
        # Large groups use fan-out pattern
        if len(member_ids) > 50:
            task = DeliveryTask(
                message_id=message_id,
                conversation_id=group_id,
                sender_id=sender_id,
                recipient_ids=member_ids,
                content=content
            )
            self.message_queue.publish(
                self.FANOUT_TOPIC,
                self._serialize(task)
            )
        else:
            # Direct delivery for small groups
            for member_id in member_ids:
                if member_id != sender_id:
                    task = DeliveryTask(
                        message_id=message_id,
                        conversation_id=group_id,
                        sender_id=sender_id,
                        recipient_ids=[member_id],
                        content=content
                    )
                    self.message_queue.publish(
                        self.DELIVERY_TOPIC,
                        self._serialize(task)
                    )
        
        return message_id
    
    def mark_delivered(self, message_id: str, user_id: str) -> None:
        """Mark message as delivered."""
        self._update_status_for_user(
            message_id, user_id, MessageStatusEnum.DELIVERED
        )
        self._notify_sender(message_id, "delivered", user_id)
    
    def mark_read(self, message_id: str, user_id: str) -> None:
        """Mark message as read."""
        self._update_status_for_user(
            message_id, user_id, MessageStatusEnum.READ
        )
        self._notify_sender(message_id, "read", user_id)
    
    def _update_status(
        self, message_id: str, status: MessageStatusEnum
    ) -> None:
        key = f"msg:{message_id}:status"
        self.cache.set(key, status.value, 86400 * 7)
    
    def _update_status_for_user(
        self, message_id: str, user_id: str, status: MessageStatusEnum
    ) -> None:
        key = f"msg:{message_id}:status:{user_id}"
        self.cache.set(key, status.value, 86400 * 7)
    
    def _notify_sender(
        self, message_id: str, status: str, by_user_id: str
    ) -> None:
        self.cache.publish(
            "status_updates",
            f"{message_id}:{status}:{by_user_id}"
        )
    
    def _serialize(self, task: DeliveryTask) -> bytes:
        # In production: use proper serialization
        return str(task).encode()


# ============================================================================
# Delivery Worker
# ============================================================================

class DeliveryWorker:
    """Worker for async message delivery."""
    
    MAX_RETRIES = 3
    
    def __init__(
        self,
        presence_service: PresenceService,
        connection_registry: ConnectionRegistry,
        message_queue: MessageQueue,
        cache: Cache
    ):
        self.presence_service = presence_service
        self.connection_registry = connection_registry
        self.message_queue = message_queue
        self.cache = cache
    
    def process_message(self, message: bytes) -> None:
        """Process a delivery task."""
        task = self._deserialize(message)
        
        for recipient_id in task.recipient_ids:
            self._deliver_to_user(task, recipient_id)
    
    def _deliver_to_user(self, task: DeliveryTask, recipient_id: str) -> None:
        """Attempt to deliver message to a user."""
        presence = self.presence_service.get_presence(recipient_id)
        
        if presence.status == PresenceStatus.ONLINE:
            ws_server_id = presence.ws_server_id
            if ws_server_id:
                delivered = self.connection_registry.push_to_user(
                    ws_server_id, recipient_id, task.content
                )
                
                if delivered:
                    self.cache.publish(
                        "status_updates",
                        f"{task.message_id}:delivered:{recipient_id}"
                    )
                else:
                    self._handle_delivery_failure(task, recipient_id)
        else:
            self._queue_for_offline_user(task, recipient_id)
    
    def _handle_delivery_failure(
        self, task: DeliveryTask, recipient_id: str
    ) -> None:
        """Handle failed delivery attempt."""
        task.increment_retry()
        
        if task.retry_count < self.MAX_RETRIES:
            # Retry with backoff
            self.message_queue.publish(
                "message_delivery_retry",
                self._serialize(task)
            )
        else:
            # Move to offline queue
            self._queue_for_offline_user(task, recipient_id)
    
    def _queue_for_offline_user(
        self, task: DeliveryTask, recipient_id: str
    ) -> None:
        """Queue message for offline user."""
        key = f"offline_queue:{recipient_id}"
        self.cache.set(key, task.message_id, 86400 * 30)
    
    def _deserialize(self, data: bytes) -> DeliveryTask:
        # In production: proper deserialization
        return DeliveryTask(
            message_id="",
            conversation_id="",
            sender_id="",
            recipient_ids=[],
            content=""
        )
    
    def _serialize(self, task: DeliveryTask) -> bytes:
        return str(task).encode()


# ============================================================================
# Group Chat Service
# ============================================================================

@dataclass
class Group:
    """A chat group."""
    group_id: str
    conversation_id: str
    name: str
    member_ids: List[str]
    admin_ids: List[str]
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class GroupService:
    """Service for group chat operations."""
    
    def __init__(self, cache: Cache):
        self.cache = cache
        self._groups: Dict[str, Group] = {}
    
    def create_group(
        self,
        creator_id: str,
        name: str,
        member_ids: List[str]
    ) -> Group:
        """Create a new group."""
        group = Group(
            group_id=str(uuid.uuid4()),
            conversation_id=str(uuid.uuid4()),
            name=name,
            member_ids=[creator_id] + member_ids,
            admin_ids=[creator_id],
            created_by=creator_id
        )
        
        self._groups[group.group_id] = group
        return group
    
    def add_member(
        self, group_id: str, admin_id: str, new_member_id: str
    ) -> None:
        """Add a member to the group."""
        group = self._groups.get(group_id)
        if not group:
            raise ValueError("Group not found")
        
        if admin_id not in group.admin_ids:
            raise ValueError("Only admins can add members")
        
        if new_member_id not in group.member_ids:
            group.member_ids.append(new_member_id)
    
    def remove_member(
        self, group_id: str, admin_id: str, member_id: str
    ) -> None:
        """Remove a member from the group."""
        group = self._groups.get(group_id)
        if not group:
            raise ValueError("Group not found")
        
        if admin_id not in group.admin_ids and member_id != admin_id:
            raise ValueError("Only admins can remove other members")
        
        if member_id in group.member_ids:
            group.member_ids.remove(member_id)
    
    def get_members(self, group_id: str) -> List[str]:
        """Get group members."""
        group = self._groups.get(group_id)
        return group.member_ids if group else []


# ============================================================================
# Typing Indicator Service
# ============================================================================

class TypingIndicatorService:
    """Service for managing typing indicators."""
    
    TYPING_TTL = 5  # seconds
    
    def __init__(self, cache: Cache):
        self.cache = cache
    
    def set_typing(
        self, user_id: str, conversation_id: str, is_typing: bool
    ) -> None:
        """Update typing status."""
        key = f"typing:{conversation_id}:{user_id}"
        
        if is_typing:
            self.cache.set(key, "1", self.TYPING_TTL)
        else:
            self.cache.delete(key)
        
        # Broadcast to conversation participants
        self.cache.publish(
            f"typing:{conversation_id}",
            f"{user_id}:{'1' if is_typing else '0'}"
        )
    
    def get_typing_users(self, conversation_id: str) -> List[str]:
        """Get users currently typing in a conversation."""
        # In production: scan Redis keys or maintain set
        return []
