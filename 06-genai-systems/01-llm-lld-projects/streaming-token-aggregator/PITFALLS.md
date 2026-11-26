# Pitfalls: Streaming Token Aggregator

*Note: These pitfalls assume the core behavior is correctly implemented without optional extensions.*
Common mistakes and architectural traps encountered when building token streaming infrastructure.

## 1. Deadlocks in Condition Variables
A classic concurrency mistake is failing to acquire the lock before calling `wait()`, or worse, holding the lock during a long-running, blocking I/O operation (like writing to the TCP socket). If the consumer yields the token to the network stack *while still holding the aggregator's RLock*, the producer (LLM) will be permanently blocked trying to write the next token.

**Counterexample (Bad Practice):**
```python
    def read_stream(self, timeout_sec: float = 1.0):
        while True:
            with self._lock:
                while self._size == 0 and not self._closed:
                    self._not_empty.wait(timeout=1.0)
                if self._size > 0:
                    chunk = self._buffer[self._head]
                    # BAD: Yielding while holding the lock blocks the producer!
                    yield chunk.text 
```

## 2. Unbounded Memory Leaks (Hanging Clients)
If a client establishes an HTTP connection but stops reading TCP packets, the OS network buffers will fill up. If the aggregator does not enforce a strict `max_size` limit on its internal buffer, it will continue appending tokens until the server runs out of memory (OOM). Bounding the buffer is critical.

## 3. The "Static Timeout" Trap
When using `Condition.wait(timeout)` inside a `while` loop (which is necessary to guard against spurious wakeups), a common mistake is passing the original timeout value to every iteration. 

**Counterexample (Bad Practice):**
```python
# BAD: Resets the 5-second timer on every wakeup
while self._size == 0 and not self._closed:
    # If a spurious wakeup occurs after 4s, the next wait resets to 5s,
    # leading to a total wait time up to 9s!
    self._not_empty.wait(timeout=5.0) 
```

**Correct Approach:**
The correct approach calculates a static deadline once, and calculates the delta on every loop (see `time_left = deadline - time.monotonic()` usage in the Code Walkthrough).

## 4. Reverse Proxy Buffer Bloat
Even if the Python application streams tokens perfectly, infrastructure like Nginx, Envoy, or AWS API Gateway might buffer the responses. 
- Proxies often wait to accumulate chunks of data (e.g., 4KB) before flushing to the client to optimize packet sizes.
- This defeats the purpose of streaming; the user will see nothing for several seconds, and then a large chunk of text will appear instantly.
- **Fix:** You must explicitly disable proxy buffering for streaming endpoints (e.g., `proxy_buffering off;` in Nginx) or send appropriate headers (like `X-Accel-Buffering: no`).

## 5. SSE Formatting Errors
The Server-Sent Events protocol is simple but strict. Failing to prefix every line of a multi-line string with `data: ` will cause the client's `EventSource` parser to silently drop or corrupt the event. Failing to terminate the event with a double newline (`\n\n`) will cause the client to hang, waiting for the end of the message.
