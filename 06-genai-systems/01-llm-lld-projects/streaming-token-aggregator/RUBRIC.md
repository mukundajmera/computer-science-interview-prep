# Grading Rubric: Streaming Token Aggregator

*Note: This rubric applies to the core implementation. Optional extensions are handled in follow-ups.*
Assess candidates based on their handling of concurrency, memory management, and edge cases inherent in streaming data to unpredictable clients.

## 1. Concurrency & Synchronization (40%)
- **Excellent:** Correctly uses `threading.RLock()` and condition variables (`wait`/`notify_all`). Handles spurious wakeups by wrapping the `wait()` call in a `while self._size == 0 and not self._closed:` loop checking the `size` condition. Safely releases locks before yielding chunks (`yield chunk.text` outside `with self._lock:`) to prevent deadlocks with the HTTP framework.
- **Adequate:** Uses locks for thread safety but might use sleep/polling (`time.sleep()`) instead of condition variables, resulting in higher latency or CPU burn.
- **Poor:** Fails to use locks, leading to race conditions on the `_head`/`_tail` pointers, or holds the lock while blocked on network I/O (`yield` inside the lock).

## 2. Memory & Buffer Management (30%)
- **Excellent:** Implements a fixed-size ring buffer (`self._buffer = [None] * self._max_size`) to achieve a zero-allocation profile during the hot path. Correctly uses modulo arithmetic (`(self._tail + 1) % self._max_size`) for index wrapping. Invariants like `self._size <= self._max_size` are strictly maintained.
- **Adequate:** Uses dynamic collections (like a standard List or unbounded Queue) but implements explicit caps and truncations.
- **Poor:** Allows unbounded buffer growth, risking Out-Of-Memory (OOM) errors if the client connection stalls.

## 3. Backpressure Policy (15%)
- **Excellent:** Explicitly defines and implements a backpressure strategy (e.g., dropping the oldest token). Defends the choice as protecting the expensive LLM producer from slow consumer clients. When `self._size == self._max_size`, correctly overwrites the oldest data, increments `_dropped`, and advances `_head`.
- **Adequate:** Fails on buffer full (e.g., raises an Exception), terminating the stream but protecting the server.
- **Poor:** Blocks the producer thread indefinitely waiting for the client to read, creating severe vulnerability to stalling/Slowloris attacks.

## 4. Timeout Budgeting (15%)
- **Excellent:** Calculates an absolute deadline (`time.monotonic() + timeout_sec`) *before* the wait loop, recalculating the `time_left = deadline - time.monotonic()` for each iteration to handle spurious wakeups without exceeding the total budget.
- **Adequate:** Applies a static timeout to individual `wait()` calls, meaning multiple wakeups could cause the total wait time to exceed the intended limit.
- **Poor:** Blocks indefinitely (`wait()` with no timeout) causing permanent thread leaks if the producer hangs.
