import threading
import time
import uuid
from typing import TypeVar, Generic, Dict, List, Optional, Any, Callable

T = TypeVar('T')

class Message(Generic[T]):
    """Represents a message flowing through the pub/sub system."""
    def __init__(self, payload: T):
        self.id = str(uuid.uuid4())
        self.payload = payload
        self.created_at = time.time()
        self.delivery_count = 0

class ConsumerGroup(Generic[T]):
    """
    A consumer group handles the delivery of messages to a logical group of consumers.
    It supports visibility timeouts (if a message isn't acked in time, it's redelivered)
    and a Dead Letter Queue (DLQ) for messages that repeatedly fail processing.
    """
    def __init__(self, name: str, visibility_timeout_sec: float = 5.0, max_deliveries: int = 3):
        self.name = name
        self.visibility_timeout_sec = visibility_timeout_sec
        self._max_deliveries = max_deliveries
        self._lock = threading.Lock()
        
        self._messages: List[Message[T]] = []
        self._inflight: Dict[str, tuple[Message[T], float]] = {}  # msg_id -> (message, invisible_until)
        self._dead_letter_queue: List[Message[T]] = []

    def push(self, message: Message[T]) -> None:
        """Add a message to this consumer group's backlog."""
        with self._lock:
            self._messages.append(message)

    def pull(self) -> Optional[Message[T]]:
        """
        Retrieve a message for processing. 
        First checks if any in-flight messages have expired their visibility timeout.
        If a message exceeds max deliveries, it's moved to the DLQ.
        """
        with self._lock:
            now = time.time()
            
            # 1. Check for expired inflight messages (redelivery logic)
            expired_ids = []
            for msg_id, (msg, invisible_until) in self._inflight.items():
                if now > invisible_until:
                    expired_ids.append(msg_id)
            
            for msg_id in expired_ids:
                msg, _ = self._inflight.pop(msg_id)
                # Put back in queue, BUT don't increment delivery_count yet.
                # It will be incremented when it is actually pulled again.
                self._messages.append(msg)

            # 2. Get a new message if available
            if not self._messages:
                return None
            
            msg = self._messages.pop(0)
            msg.delivery_count += 1
            if msg.delivery_count >= self._max_deliveries:
                self._dead_letter_queue.append(msg)
                return None
                
            self._inflight[msg.id] = (msg, now + self.visibility_timeout_sec)
            return msg

    def ack(self, msg_id: str) -> bool:
        """
        Acknowledge successful processing of a message.
        Removes it from the in-flight list.
        """
        with self._lock:
            if msg_id in self._inflight:
                del self._inflight[msg_id]
                return True
            return False

    def get_dlq(self) -> List[Message[T]]:
        """Return a copy of the dead letter queue."""
        with self._lock:
            return list(self._dead_letter_queue)


class PubSubQueue(Generic[T]):
    """
    A robust Publish/Subscribe system supporting consumer groups, acknowledgements,
    visibility timeouts, and redelivery.
    """
    def __init__(self):
        # topics -> group_name -> ConsumerGroup
        self._topics: Dict[str, Dict[str, ConsumerGroup[T]]] = {}
        self._lock = threading.Lock()

    def create_topic(self, topic: str) -> None:
        """Explicitly create a topic."""
        with self._lock:
            if topic not in self._topics:
                self._topics[topic] = {}

    def subscribe(self, topic: str, group_name: str, visibility_timeout_sec: float = 5.0) -> None:
        """Subscribe a consumer group to a topic."""
        with self._lock:
            if topic not in self._topics:
                self._topics[topic] = {}
            if group_name not in self._topics[topic]:
                self._topics[topic][group_name] = ConsumerGroup(group_name, visibility_timeout_sec)

    def publish(self, topic: str, payload: T) -> int:
        """
        Publish a message to a topic.
        The message is copied to all subscribed consumer groups.
        """
        with self._lock:
            if topic not in self._topics:
                return 0
            
            groups = self._topics[topic].values()
            for group in groups:
                # Create a distinct Message object per group so each has its own id, state, delivery count
                group.push(Message(payload))
            
            return len(groups)

    def pull(self, topic: str, group_name: str) -> Optional[Message[T]]:
        """Pull a message from a specific topic and consumer group."""
        with self._lock:
            if topic not in self._topics or group_name not in self._topics[topic]:
                return None
            group = self._topics[topic][group_name]
            
        return group.pull()

    def ack(self, topic: str, group_name: str, msg_id: str) -> bool:
        """Acknowledge a message in a specific consumer group."""
        with self._lock:
            if topic not in self._topics or group_name not in self._topics[topic]:
                return False
            group = self._topics[topic][group_name]
            
        return group.ack(msg_id)
        
    def get_dlq(self, topic: str, group_name: str) -> List[Message[T]]:
        """Get the Dead Letter Queue for a specific consumer group."""
        with self._lock:
            if topic not in self._topics or group_name not in self._topics[topic]:
                return []
            group = self._topics[topic][group_name]
        return group.get_dlq()
