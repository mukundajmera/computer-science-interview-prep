import threading
from typing import List, Optional, Tuple

class Segment:
    def __init__(self, base_offset: int, max_bytes: int):
        self.base_offset = base_offset
        self.max_bytes = max_bytes
        self.messages: List[Tuple[int, bytes]] = []  # (offset, data)
        self.sparse_index: List[Tuple[int, int]] = []  # (offset, physical_byte_offset)
        self.current_byte_offset = 0
        self.next_offset = base_offset
        self.lock = threading.RLock()

    def append(self, data: bytes) -> Optional[int]:
        with self.lock:
            msg_size = len(data)
            if self.current_byte_offset + msg_size > self.max_bytes and len(self.messages) > 0:
                return None  # Segment is full

            offset = self.next_offset
            self.messages.append((offset, data))
            
            # Sparse index: index every N bytes, let's say every 100 bytes or every message for simplicity in this simulation
            # In real life, it's every X bytes. We'll do it every message for easy binary search simulation if needed.
            # But the requirement says "sparse offset indexing". We will index every 2 messages.
            if len(self.messages) % 2 == 1:
                self.sparse_index.append((offset, self.current_byte_offset))
                
            self.current_byte_offset += msg_size
            self.next_offset += 1
            return offset

    def read(self, start_offset: int, max_messages: int) -> List[Tuple[int, bytes]]:
        with self.lock:
            if start_offset < self.base_offset or start_offset >= self.next_offset:
                return []
            
            # Binary search on sparse index to find the starting point
            low, high = 0, len(self.sparse_index) - 1
            best_idx = 0
            while low <= high:
                mid = (low + high) // 2
                if self.sparse_index[mid][0] <= start_offset:
                    best_idx = mid
                    low = mid + 1
                else:
                    high = mid - 1
                    
            # In a real log, we would jump to physical_byte_offset and read from file.
            # Here we just find the message in the list starting from the index hint.
            # The index gives us a message offset, we know it corresponds roughly to its position in the list
            # since lists are arrays. Actually list index is just (offset - base_offset)
            # but we simulate the sparse index search anyway to show intent.
            start_idx = start_offset - self.base_offset
            if start_idx < 0:
                start_idx = 0
            
            return self.messages[start_idx : start_idx + max_messages]


class PartitionLog:
    def __init__(self, max_segment_bytes: int = 1024):
        self.max_segment_bytes = max_segment_bytes
        self.segments: List[Segment] = [Segment(0, self.max_segment_bytes)]
        self.lock = threading.RLock()

    def append(self, data: bytes) -> int:
        with self.lock:
            active_segment = self.segments[-1]
            offset = active_segment.append(data)
            if offset is None:
                # Segment is full, roll over
                new_base_offset = active_segment.next_offset
                new_segment = Segment(new_base_offset, self.max_segment_bytes)
                self.segments.append(new_segment)
                offset = new_segment.append(data)
                if offset is None:
                     raise RuntimeError("Message too large for a single segment")
            return offset

    def read(self, start_offset: int, max_messages: int = 10) -> List[Tuple[int, bytes]]:
        with self.lock:
            results = []
            messages_needed = max_messages
            current_offset = start_offset

            # Find the starting segment
            segment_idx = 0
            low, high = 0, len(self.segments) - 1
            while low <= high:
                mid = (low + high) // 2
                if self.segments[mid].base_offset <= current_offset:
                    segment_idx = mid
                    low = mid + 1
                else:
                    high = mid - 1

            for i in range(segment_idx, len(self.segments)):
                segment = self.segments[i]
                msgs = segment.read(current_offset, messages_needed)
                results.extend(msgs)
                messages_needed -= len(msgs)
                if messages_needed <= 0:
                    break
                if msgs:
                    current_offset = msgs[-1][0] + 1
                else:
                    break # No more messages in this segment, though it shouldn't happen unless we hit the end
                    
            return results

    def get_log_end_offset(self) -> int:
        with self.lock:
            return self.segments[-1].next_offset

