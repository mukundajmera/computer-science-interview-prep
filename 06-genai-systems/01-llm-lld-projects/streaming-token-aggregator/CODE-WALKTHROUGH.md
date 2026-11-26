# Code Walkthrough: Streaming Token Aggregator

This walkthrough explains the `v1-basic` Python implementation of the `StreamingTokenAggregator`.

## The Data Model

```python
@dataclass
class StreamChunk:
    index: int
    text: str
    is_final: bool
    finish_reason: typing.Optional[str] = None
```
A simple dataclass encapsulates the data being streamed. It tracks its position (`index`), the actual string `text`, and lifecycle flags (`is_final`, `finish_reason`) so the consumer knows when the stream is complete.

## Initialization & Buffer Setup

```python
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
```
- The `_buffer` is pre-allocated with `None` to the size of `max_size` (100). This prevents dynamic memory allocation during high-speed token generation.
- The `_lock` (Reentrant Lock) ensures that simultaneous writes from the model and reads from the web server don't corrupt the `_head`, `_tail`, or `_size` counters.
- The `_not_empty` condition variable is bound to the lock and allows the reader to sleep efficiently when there are no tokens.

## The Producer: `write_chunk`

```python
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
```
The producer method:
1. Acquires the lock.
2. Checks for overflow (`self._size == self._max_size`). If full, it moves the `_head` pointer forward, intentionally "forgetting" the oldest unread chunk (Drop Oldest backpressure).
3. Writes the new chunk to `_buffer[_tail]` and advances the `_tail` modulo the max size.
4. Updates the `_closed` state if this is the final token.
5. Calls `notify_all()` to wake up any consumer threads currently sleeping in `read_stream`.

## The Consumer: `read_stream`

```python
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
```
The consumer method is a generator (using `yield`):
1. **Timeout Calculation:** Note how `deadline = time.monotonic() + timeout_sec` is calculated *outside* the inner loop. Inside the loop, `time_left` is continuously re-calculated. This ensures the total time spent blocking strictly adheres to the budget, a critical pattern for robust system design.
2. **Sleeping:** If the buffer is empty (`_size == 0`) and not closed, it calls `_not_empty.wait()`. The thread goes to sleep, releasing the lock.
3. **Reading:** Once awakened (and if chunks exist), it reads from `_buffer[_head]`, clears the reference (allowing Python garbage collection of the chunk), advances `_head`, and decrements `_size`.
4. **Yielding:** It steps out of the lock block and `yields` the text, streaming it back to the HTTP response framework.

## Formatting SSE

```python
    def format_sse_event(self, event_type: str, data: str) -> str:
        lines = []
        if event_type:
            lines.append(f"event: {event_type}")
        
        for line in data.split("\n"):
            lines.append(f"data: {line}")
            
        lines.append("") 
        lines.append("")
        return "\n".join(lines)
```
This utility method formats the output strictly to the Server-Sent Events specification, ensuring that multi-line text blocks have `data: ` prepended to every line, and the whole payload is terminated by `\n\n`.
