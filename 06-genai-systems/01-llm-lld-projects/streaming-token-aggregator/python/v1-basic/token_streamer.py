import typing
import threading
import time
from dataclasses import dataclass

@dataclass
class StreamChunk:
    index: int
    text: str
    is_final: bool
    finish_reason: typing.Optional[str] = None

class StreamingTokenAggregator:
    def __init__(self, max_size: int = 100):
        self._max_size = max_size
        self._buffer: typing.List[typing.Optional[StreamChunk]] = [None] * self._max_size
        self._head = 0
        self._tail = 0
        self._size = 0
        self._lock = threading.RLock()
        self._not_empty = threading.Condition(self._lock)
        self._closed = False
        self._dropped = 0

    def write_chunk(self, chunk: StreamChunk) -> None:
        with self._lock:
            if self._closed:
                return

            if self._size == self._max_size:
                # Backpressure: drop the oldest chunk (slow consumer)
                self._head = (self._head + 1) % self._max_size
                self._size -= 1
                self._dropped += 1

            self._buffer[self._tail] = chunk
            self._tail = (self._tail + 1) % self._max_size
            self._size += 1

            if chunk.is_final:
                self._closed = True

            self._not_empty.notify_all()

    def read_stream(self, timeout_sec: float = 1.0) -> typing.Generator[str, None, None]:
        while True:
            deadline = time.monotonic() + timeout_sec
            chunk = None
            
            with self._lock:
                while self._size == 0 and not self._closed:
                    time_left = deadline - time.monotonic()
                    if time_left <= 0:
                        break
                    self._not_empty.wait(timeout=time_left)
                
                if self._size > 0:
                    chunk = self._buffer[self._head]
                    self._buffer[self._head] = None
                    self._head = (self._head + 1) % self._max_size
                    self._size -= 1
                elif self._closed:
                    break

            if chunk is not None:
                yield chunk.text
            else:
                # Timeout waiting for a single chunk
                break

    def format_sse_event(self, event_type: str, data: str) -> str:
        lines = []
        if event_type:
            lines.append(f"event: {event_type}")
        
        # SSE standard requires each line of data to be prefixed with "data: "
        for line in data.split("\n"):
            lines.append(f"data: {line}")
            
        lines.append("") # Empty line to terminate the event (will be double newline because of join)
        lines.append("")
        return "\n".join(lines)
