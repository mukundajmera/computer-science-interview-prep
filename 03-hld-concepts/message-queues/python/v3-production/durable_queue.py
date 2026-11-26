import os
import time
import json
import threading
from typing import TypeVar, Generic, Dict, List, Optional, Any, Tuple

class DurableMessage:
    """Represents a message stored durably on disk."""
    def __init__(self, key: str, payload: Any, offset: int = -1):
        self.key = key
        self.payload = payload
        self.offset = offset
        self.timestamp = time.time()
        
    def to_dict(self):
        return {
            "key": self.key,
            "payload": self.payload,
            "offset": self.offset,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: dict):
        msg = cls(data["key"], data["payload"], data["offset"])
        msg.timestamp = data["timestamp"]
        return msg

class Partition:
    """
    A single partition of a durable queue.
    Messages appended here are written sequentially to a log file.
    """
    def __init__(self, partition_id: int, log_dir: str):
        self.partition_id = partition_id
        self.log_file = os.path.join(log_dir, f"part_{partition_id}.log")
        self._lock = threading.Lock()
        self._messages: List[DurableMessage] = []
        self._next_offset = 0
        
        # Recover state from disk if it exists
        self._load()

    def _load(self):
        if not os.path.exists(self.log_file):
            return
        with open(self.log_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                msg = DurableMessage.from_dict(data)
                self._messages.append(msg)
                self._next_offset = max(self._next_offset, msg.offset + 1)

    def append(self, message: DurableMessage) -> int:
        """
        Append a message to the partition and flush to disk.
        Returns the assigned offset.
        """
        with self._lock:
            message.offset = self._next_offset
            self._next_offset += 1
            self._messages.append(message)
            
            with open(self.log_file, "a") as f:
                f.write(json.dumps(message.to_dict()) + "\n")
                f.flush()
                os.fsync(f.fileno())
                
            return message.offset

    def read(self, offset: int) -> Optional[DurableMessage]:
        """Read a message at a specific offset."""
        with self._lock:
            # simple array indexing since we assume contiguous offsets from 0
            if 0 <= offset < len(self._messages):
                return self._messages[offset]
            return None

class DurableQueue:
    """
    A durable file-backed log queue with offsets, partitioning (per-key ordering).
    """
    def __init__(self, log_dir: str, num_partitions: int = 4):
        self.log_dir = log_dir
        self.num_partitions = num_partitions
        os.makedirs(log_dir, exist_ok=True)
        
        self.partitions = [Partition(i, log_dir) for i in range(num_partitions)]
        
        # Consumer group offsets: group_id -> (partition_id -> offset)
        self.consumer_offsets: Dict[str, Dict[int, int]] = {}
        self.offsets_file = os.path.join(log_dir, "offsets.json")
        self._offset_lock = threading.Lock()
        self._load_offsets()

    def _load_offsets(self):
        """Load committed offsets from disk."""
        if os.path.exists(self.offsets_file):
            with open(self.offsets_file, "r") as f:
                content = f.read()
                if content:
                    raw_offsets = json.loads(content)
                    self.consumer_offsets = {
                        k: {int(p): off for p, off in v.items()}
                        for k, v in raw_offsets.items()
                    }

    def _save_offsets(self):
        """Save committed offsets to disk."""
        with open(self.offsets_file, "w") as f:
            json.dump(self.consumer_offsets, f)
            f.flush()
            os.fsync(f.fileno())

    def _get_partition(self, key: str) -> Partition:
        """Route message to a partition based on the key's hash."""
        # Using hash to ensure per-key ordering (all messages with same key go to same partition)
        part_id = hash(key) % self.num_partitions
        return self.partitions[part_id]

    def produce(self, key: str, payload: Any) -> Tuple[int, int]:
        """Produce a message, ensuring it's durably written. Returns (partition_id, offset)"""
        part = self._get_partition(key)
        msg = DurableMessage(key, payload)
        offset = part.append(msg)
        return part.partition_id, offset

    def consume(self, group_id: str, partition_id: int) -> Optional[DurableMessage]:
        """Read the next uncommitted message for a consumer group in a specific partition."""
        with self._offset_lock:
            if group_id not in self.consumer_offsets:
                self.consumer_offsets[group_id] = {}
            if partition_id not in self.consumer_offsets[group_id]:
                self.consumer_offsets[group_id][partition_id] = 0
                
            offset = self.consumer_offsets[group_id][partition_id]
            
        part = self.partitions[partition_id]
        return part.read(offset)

    def commit_offset(self, group_id: str, partition_id: int, offset: int) -> None:
        """Commit an offset for a consumer group, durably saving it."""
        with self._offset_lock:
            if group_id not in self.consumer_offsets:
                self.consumer_offsets[group_id] = {}
            
            # Only move forward
            current = self.consumer_offsets[group_id].get(partition_id, 0)
            if offset > current:
                self.consumer_offsets[group_id][partition_id] = offset
                self._save_offsets()


class IdempotentConsumerWrapper:
    """Wrapper that prevents processing the same message twice (idempotency) and handles retries/DLQ."""
    def __init__(self, queue: DurableQueue, group_id: str, max_retries: int = 3):
        self.queue = queue
        self.group_id = group_id
        self.max_retries = max_retries
        self.processed_messages = set() # Ideally bounded or in persistent store
        self.retry_counts: Dict[str, int] = {}
        self.dlq: List[DurableMessage] = []
        self._lock = threading.Lock()
        
    def consume_and_process(self, partition_id: int, processor: callable) -> bool:
        """
        Consumes, deduplicates, and processes a message.
        Handles retry backoff (conceptually, by letting processor fail) and DLQ logic.
        """
        msg = self.queue.consume(self.group_id, partition_id)
        if not msg:
            return False
            
        msg_id = f"{partition_id}:{msg.offset}"
        
        with self._lock:
            if msg_id in self.processed_messages:
                # Already processed, just commit and move on
                self.queue.commit_offset(self.group_id, partition_id, msg.offset + 1)
                return True
                
        # Process
        success = False
        try:
            processor(msg.payload)
            success = True
        except Exception:
            with self._lock:
                # Retry logic
                count = self.retry_counts.get(msg_id, 0) + 1
                self.retry_counts[msg_id] = count
                
                if count >= self.max_retries:
                    # Move to DLQ
                    self.dlq.append(msg)
                    # Commit to move past this poisonous message
                    self.queue.commit_offset(self.group_id, partition_id, msg.offset + 1)
                else:
                    # In a real system we'd wait before retrying, or put it in a separate retry queue.
                    # Here we just leave the offset uncommitted so it will be consumed again.
                    pass
            
        if success:
            with self._lock:
                self.processed_messages.add(msg_id)
            self.queue.commit_offset(self.group_id, partition_id, msg.offset + 1)
            
        return success
