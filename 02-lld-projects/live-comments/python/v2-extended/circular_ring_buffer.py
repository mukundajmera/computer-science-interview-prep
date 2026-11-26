from typing import Dict, List, Optional
import threading

class RingBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer: List[Optional[str]] = [None] * capacity
        self.sequence = 0
        self.lock = threading.Lock()

    def add(self, message: str) -> None:
        with self.lock:
            self.sequence += 1
            index = self.sequence % self.capacity
            self.buffer[index] = message

    def replay(self, cursor_str: str, limit: int) -> List[str]:
        with self.lock:
            cursor = 0
            has_cursor = bool(cursor_str)
            if has_cursor:
                try:
                    cursor = int(cursor_str)
                except ValueError:
                    pass

            max_seq = self.sequence
            oldest_available = max(1, max_seq - self.capacity + 1)
            
            result = []
            
            # A bounded replay ring emits a documented sequence gap on overflow
            is_gap = has_cursor and cursor < oldest_available - 1
            if is_gap:
                result.append("[GAP] Sequence gap detected on overflow")
                cursor = oldest_available - 1
                
            if has_cursor:
                start_seq = max(cursor + 1, oldest_available)
            else:
                start_seq = max(oldest_available, max_seq - limit + 1)
                
            end_seq = max_seq
            
            for seq in range(start_seq, end_seq + 1):
                index = seq % self.capacity
                comment = self.buffer[index]
                if comment is not None:
                    result.append(comment)
                    
            if has_cursor and len(result) > limit:
                return result[:limit]
            return result

class CircularRingBufferReplayStore:
    def __init__(self, buffer_capacity: int):
        self.buffer_capacity = buffer_capacity
        self.stream_buffers: Dict[str, RingBuffer] = {}
        self.lock = threading.Lock()

    def add_comment(self, stream_id: str, comment_payload: str) -> None:
        with self.lock:
            if stream_id not in self.stream_buffers:
                self.stream_buffers[stream_id] = RingBuffer(self.buffer_capacity)
            buffer = self.stream_buffers[stream_id]
            
        buffer.add(comment_payload)

    def replay(self, stream_id: str, cursor: str, limit: int) -> List[str]:
        with self.lock:
            buffer = self.stream_buffers.get(stream_id)
        if not buffer:
            return []
        return buffer.replay(cursor, limit)
