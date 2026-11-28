"""v2 PartitionLog: retention policies and disk monitoring (improvement #1).

Implements FOLLOW-UPS.md #2: size-based and time-based segment deletion
plus a disk usage reading. Retention only ever deletes whole inactive
segments from the head, exactly like real Kafka; the active segment is
never deleted, and reading a deleted offset still raises the v1
OffsetOutOfRange error. See broker_cluster.py for the full v2 list.
"""
import threading
import time
from typing import Callable, List, Optional, Tuple


class Segment:
    def __init__(self, base_offset: int, max_bytes: int, created_at_ms: float = 0.0):
        self.base_offset = base_offset
        self.max_bytes = max_bytes
        self.created_at_ms = created_at_ms
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

            if len(self.messages) % 2 == 1:
                self.sparse_index.append((offset, self.current_byte_offset))

            self.current_byte_offset += msg_size
            self.next_offset += 1
            return offset

    def read(self, start_offset: int, max_messages: int) -> List[Tuple[int, bytes]]:
        with self.lock:
            if start_offset < self.base_offset or start_offset > self.next_offset:
                return []

            low, high = 0, len(self.sparse_index) - 1
            best_idx = -1
            while low <= high:
                mid = (low + high) // 2
                if self.sparse_index[mid][0] <= start_offset:
                    best_idx = mid
                    low = mid + 1
                else:
                    high = mid - 1

            start_idx = 0
            while start_idx < len(self.messages) and self.messages[start_idx][0] < start_offset:
                start_idx += 1

            return self.messages[start_idx : start_idx + max_messages]


class PartitionLogV2:
    def __init__(self, max_segment_bytes: int = 1024, clock: Optional[Callable[[], float]] = None):
        self.max_segment_bytes = max_segment_bytes
        # Wall-clock milliseconds, injectable for deterministic retention tests.
        self.clock = clock or (lambda: time.time() * 1000.0)
        self.segments: List[Segment] = [Segment(0, self.max_segment_bytes, self.clock())]
        self.lock = threading.RLock()

    def append(self, data: bytes) -> int:
        with self.lock:
            active_segment = self.segments[-1]
            offset = active_segment.append(data)
            if offset is None:
                new_base_offset = active_segment.next_offset
                new_segment = Segment(new_base_offset, self.max_segment_bytes, self.clock())
                self.segments.append(new_segment)
                offset = new_segment.append(data)
                if offset is None:
                    raise RuntimeError("Message too large for a single segment")
            return offset

    def truncate_to(self, offset: int):
        with self.lock:
            self.segments = [seg for seg in self.segments if seg.base_offset <= offset]
            if not self.segments:
                self.segments.append(Segment(0, self.max_segment_bytes, self.clock()))
                self.segments[0].next_offset = offset
                self.segments[0].base_offset = offset
                return

            last_seg = self.segments[-1]
            last_seg.messages = [m for m in last_seg.messages if m[0] < offset]
            last_seg.sparse_index = [idx for idx in last_seg.sparse_index if idx[0] < offset]
            last_seg.next_offset = offset
            last_seg.current_byte_offset = sum(len(m[1]) for m in last_seg.messages)

    def read(self, start_offset: int, max_messages: int = 10) -> List[Tuple[int, bytes]]:
        with self.lock:
            if not self.segments:
                return []

            earliest_offset = self.segments[0].messages[0][0] if self.segments[0].messages else self.segments[0].base_offset
            if start_offset < earliest_offset:
                raise ValueError("OffsetOutOfRange: Retention gap")
            if start_offset > self.get_log_end_offset():
                raise ValueError("OffsetOutOfRange: Invalid future offset")

            results = []
            messages_needed = max_messages
            current_offset = start_offset

            segment_idx = -1
            low, high = 0, len(self.segments) - 1
            while low <= high:
                mid = (low + high) // 2
                if self.segments[mid].base_offset <= current_offset:
                    segment_idx = mid
                    low = mid + 1
                else:
                    high = mid - 1

            if segment_idx == -1:
                return []

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
                    break

            return results

    def get_log_end_offset(self) -> int:
        with self.lock:
            return self.segments[-1].next_offset

    # --- Improvement #1: retention + disk monitoring (FOLLOW-UPS.md #2) ---

    def disk_usage_bytes(self) -> int:
        """Total bytes held across all segments, the number a disk monitor
        would watch."""
        with self.lock:
            return sum(seg.current_byte_offset for seg in self.segments)

    def enforce_retention(self, max_total_bytes: Optional[int] = None,
                          max_age_ms: Optional[float] = None) -> int:
        """Deletes whole inactive segments from the head while the total
        size exceeds max_total_bytes or the segment is older than
        max_age_ms. The active (last) segment is never deleted. Returns the
        number of segments deleted."""
        with self.lock:
            now_ms = self.clock()
            deleted = 0
            while len(self.segments) > 1:
                head = self.segments[0]
                over_size = (max_total_bytes is not None
                             and sum(s.current_byte_offset for s in self.segments) > max_total_bytes)
                over_age = (max_age_ms is not None
                            and now_ms - head.created_at_ms > max_age_ms)
                if not over_size and not over_age:
                    break
                self.segments.pop(0)
                deleted += 1
            return deleted
