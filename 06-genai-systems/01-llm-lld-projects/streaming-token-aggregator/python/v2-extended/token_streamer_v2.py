"""
Streaming Token Aggregator - v2-extended.

A deliberate step up from ``v1-basic/token_streamer.py``. It keeps the v1
public API names (``StreamChunk``, ``StreamingTokenAggregator``,
``write_chunk``, ``read_stream``, ``format_sse_event``), the bounded ring
buffer, the RLock + condition-variable contract, the drop-oldest backpressure
policy, the deadline-based (non-resetting) timeout, and the ephemeral-by-default
privacy boundary, while implementing three improvements the project's own
documents name:

1. **Client cancellation propagation** (FOLLOW-UPS 2). ``cancel()`` moves the
   aggregator to a cancelled terminal state: blocked consumers unblock and
   end their streams promptly, later writes are ignored (and counted), and the
   producer can poll ``is_cancelled`` each loop iteration to abort generation
   and free compute instead of discovering a dead socket much later.

2. **Reconnect resume via Last-Event-ID** (FOLLOW-UPS 3). Chunks already
   carry an ``index``; v2 adds an optional bounded replay window
   (``replay_capacity``) retaining the most recent written chunks, and
   ``read_stream(last_event_id=...)`` first replays retained chunks with
   ``index > last_event_id`` (counted as ``replayed``), then attaches to the
   live ring buffer, skipping any live chunk already replayed. The window is
   bounded and opt-in: with the default ``replay_capacity=0`` nothing is
   retained beyond v1's ring buffer, preserving v1's ephemeral privacy
   boundary. ``format_sse_event`` accepts an optional ``event_id`` and emits
   the ``id:`` field the SSE ``Last-Event-ID`` handshake needs.

3. **Stream metrics and input hardening.** ``metrics()`` snapshots written,
   read, dropped, and replayed counters plus the closed/cancelled flags, so
   backpressure engagement is observable instead of silent. The constructor
   validates ``max_size`` (v1 crashed with ZeroDivisionError on the first
   write when ``max_size=0``) and ``replay_capacity``.

Standard library only. Python 3.8 compatible. The v1 boundaries still apply:
no persistence across restarts, replay is best-effort within the configured
window, and a client that falls further behind than the window simply resumes
from the oldest retained chunk (documented, not silent).
"""

import threading
import time
import typing
from collections import deque
from dataclasses import dataclass


@dataclass
class StreamChunk:
    """One generated token or text chunk; ``index`` doubles as the SSE event id."""
    index: int
    text: str
    is_final: bool
    finish_reason: typing.Optional[str] = None


class StreamingTokenAggregator:
    """
    Thread-safe bounded ring buffer between an LLM producer and an HTTP/SSE
    consumer, with cancellation, bounded replay, and metrics.

    ``write_chunk`` and the per-chunk read in ``read_stream`` are O(1);
    replay costs O(R) where R is the retained window size. Space is
    O(max_size + replay_capacity).
    """

    def __init__(self, max_size: int = 100, replay_capacity: int = 0):
        """
        Initializes the ring buffer and optional replay window.

        Raises ValueError for non-positive max_size (v1 accepted 0 and then
        crashed with ZeroDivisionError on the first write) or a negative
        replay_capacity. Complexity: O(max_size) for the pre-allocation.
        """
        if not isinstance(max_size, int) or isinstance(max_size, bool) or max_size <= 0:
            raise ValueError("max_size must be a positive integer.")
        if not isinstance(replay_capacity, int) or isinstance(replay_capacity, bool) \
                or replay_capacity < 0:
            raise ValueError("replay_capacity must be a non-negative integer.")
        self._max_size = max_size
        self._buffer: typing.List[typing.Optional[StreamChunk]] = [None] * self._max_size
        self._head = 0
        self._tail = 0
        self._size = 0
        self._lock = threading.RLock()
        self._not_empty = threading.Condition(self._lock)
        self._closed = False
        self._cancelled = False
        self._cancel_reason: typing.Optional[str] = None
        self._dropped = 0
        self._history: typing.Deque[StreamChunk] = deque(maxlen=replay_capacity or None)
        self._retain_history = replay_capacity > 0
        self._written = 0
        self._read = 0
        self._replayed = 0

    @property
    def is_cancelled(self) -> bool:
        """True once cancel() has been called; the producer polls this. O(1)."""
        with self._lock:
            return self._cancelled

    @property
    def cancel_reason(self) -> typing.Optional[str]:
        """The reason passed to cancel(), if any. O(1)."""
        with self._lock:
            return self._cancel_reason

    def cancel(self, reason: typing.Optional[str] = None) -> None:
        """
        Signals client-side cancellation (FOLLOW-UPS 2): unblocks waiting
        consumers, ends the stream, and causes later writes to be ignored.
        Idempotent. O(1).
        """
        with self._lock:
            if not self._cancelled:
                self._cancelled = True
                self._cancel_reason = reason
            self._closed = True
            self._not_empty.notify_all()

    def write_chunk(self, chunk: StreamChunk) -> None:
        """
        Appends a chunk, dropping the oldest on overflow (backpressure).
        Writes after close or cancel are ignored. O(1).
        """
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
            self._written += 1

            if self._retain_history:
                self._history.append(chunk)

            if chunk.is_final:
                self._closed = True

            self._not_empty.notify_all()

    def read_stream(self, timeout_sec: float = 1.0,
                    last_event_id: typing.Optional[int] = None) -> typing.Generator[str, None, None]:
        """
        Yields chunk texts in order, blocking up to ``timeout_sec`` per chunk
        when the buffer is empty (deadline-based; never resets on spurious
        wakeups). Ends when the stream closes, is cancelled, or times out.

        With ``last_event_id``, first replays retained chunks with
        ``index > last_event_id`` (bounded replay window; if the client fell
        further behind than the window, only the retained suffix is replayed),
        then continues with the live stream, skipping live chunks already
        replayed.
        """
        replayed_max: typing.Optional[int] = None

        if last_event_id is not None:
            with self._lock:
                history_snapshot = [c for c in self._history if c.index > last_event_id]
                self._replayed += len(history_snapshot)
            for chunk in history_snapshot:
                yield chunk.text
                replayed_max = chunk.index

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
                if replayed_max is not None and chunk.index <= replayed_max:
                    # Already delivered by the replay phase; skip the duplicate.
                    continue
                with self._lock:
                    self._read += 1
                yield chunk.text
            else:
                # Timeout waiting for a single chunk
                break

    def format_sse_event(self, event_type: str, data: str,
                         event_id: typing.Optional[typing.Union[int, str]] = None) -> str:
        """
        Formats one SSE event: optional ``id:`` field (for the Last-Event-ID
        reconnect handshake), optional ``event:`` field, then one ``data:``
        line per line of payload, terminated by a blank line. O(len(data)).
        """
        lines = []
        if event_id is not None:
            lines.append(f"id: {event_id}")
        if event_type:
            lines.append(f"event: {event_type}")

        # SSE standard requires each line of data to be prefixed with "data: "
        for line in data.split("\n"):
            lines.append(f"data: {line}")

        lines.append("")  # Empty line to terminate the event
        lines.append("")
        return "\n".join(lines)

    def metrics(self) -> typing.Dict[str, typing.Any]:
        """
        Snapshot of stream counters and lifecycle flags: written, read,
        dropped (backpressure), replayed, closed, cancelled. O(1).
        """
        with self._lock:
            return {
                "written": self._written,
                "read": self._read,
                "dropped": self._dropped,
                "replayed": self._replayed,
                "buffered": self._size,
                "closed": self._closed,
                "cancelled": self._cancelled,
            }
