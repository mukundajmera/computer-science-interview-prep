"""
Token Streaming Server - v2-extended.

A deliberate step up from ``v1-basic/streaming_server.py``. It keeps the v1
public API names (``LLMProvider``, ``Tokenizer``, ``Clock``, ``stream_response``,
``HEARTBEAT_TIMEOUT`` and the SSE event formats) while addressing weaknesses
the project docs already name:

1. **Explicit backpressure flow control** (PROBLEM.md requirement 5,
   FOLLOW-UPS.md extension 2). v1 relies on ``async for`` blocking alone.
   v2 adds an optional bounded producer/consumer queue
   (``max_buffered_tokens``) with explicit ``pause()``/``resume()`` signaling
   to providers that implement those methods, so a slow client throttles the
   upstream generator instead of growing memory without bound.

2. **Configurable chunking policy and metrics hooks.** v1 flushes only on
   boundary characters and exposes no observability. v2 adds a
   ``ChunkingPolicy`` (boundary flushing on/off, optional max chunk size in
   characters) and a ``StreamMetrics`` counter set (tokens received, chunks
   flushed, heartbeats, aborts, errors, pauses, resumes) with an optional
   per-event ``metrics_hook`` callback.

3. **Configurable heartbeat interval and input validation.** v1 hardcodes the
   module-level 15-second heartbeat; v2 accepts ``heartbeat_timeout`` per call
   and fails fast on empty prompt/tenant IDs, non-positive budgets, or
   non-positive heartbeat/buffer limits.

Standard library only. Python 3.8 compatible. The LLM provider and transport
remain injected fakes for deterministic offline testing; all guarantees
unsupported in v1 remain unsupported.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple

HEARTBEAT_TIMEOUT = 15

_PING_EVENT = "event: ping\ndata: {}\n\n"
_DONE_EVENT = "data: [DONE]\n\n"


class Clock(ABC):
    """Abstract interface to provide deterministic time."""

    @abstractmethod
    def time(self) -> float:
        """Returns the current time."""


class LLMProvider(ABC):
    """Abstract interface for an LLM provider."""

    @abstractmethod
    async def async_generate(self, prompt: str, tenant_id: str) -> AsyncGenerator[str, None]:
        """Generates tokens asynchronously."""
        yield ""

    @abstractmethod
    def abort(self) -> None:
        """Cancels generation."""


class Tokenizer:
    """An approximation of a tokenizer."""

    @staticmethod
    def is_boundary(char: str) -> bool:
        # Simple string boundary checks: spaces or punctuation
        return char in {" ", ".", ",", "!", "?", ";", ":", "\n", "\t"}


@dataclass
class ChunkingPolicy:
    """
    Controls when the buffered text is flushed as an SSE payload.

    flush_on_boundary: flush when the buffer ends in a boundary character
        (the v1 behavior). max_chunk_chars: also flush once the buffer reaches
        this many characters, emitting fixed-size pieces and keeping the
        remainder. Both may be combined; size flushing runs first.
    """
    flush_on_boundary: bool = True
    max_chunk_chars: Optional[int] = None


class StreamMetrics:
    """
    In-memory event counters for one stream's lifecycle.

    Pass an instance to ``stream_response(metrics=...)`` and inspect it after
    the stream completes, or attach ``metrics_hook`` for live events.
    """

    EVENTS = (
        "tokens_received",
        "chunks_flushed",
        "heartbeats_sent",
        "aborts",
        "errors",
        "pauses",
        "resumes",
    )

    def __init__(self) -> None:
        """Initializes all counters to zero. Complexity: O(1)."""
        self._counts: Dict[str, int] = {event: 0 for event in self.EVENTS}

    def record(self, event: str) -> None:
        """
        Increments the counter for one event. Complexity: O(1).

        Raises:
            ValueError: If the event name is unknown.
        """
        if event not in self._counts:
            raise ValueError("Unknown metrics event: %r" % event)
        self._counts[event] += 1

    def snapshot(self) -> Dict[str, int]:
        """Returns a copy of the current counters. Complexity: O(E)."""
        return dict(self._counts)


class _Pipeline:
    """Shared per-stream state and token processing for both pipeline paths."""

    def __init__(self, provider: LLMProvider, max_tokens: Optional[int],
                 policy: ChunkingPolicy, metrics: StreamMetrics,
                 metrics_hook: Optional[Callable[[str, str], None]],
                 tenant_id: str) -> None:
        self.provider = provider
        self.max_tokens = max_tokens
        self.policy = policy
        self.metrics = metrics
        self.metrics_hook = metrics_hook
        self.tenant_id = tenant_id
        self.buffer: Optional[str] = ""
        self.processed_token_count = 0

    def record(self, event: str) -> None:
        """Records a metrics event and invokes the optional hook."""
        self.metrics.record(event)
        if self.metrics_hook is not None:
            self.metrics_hook(event, self.tenant_id)

    def process_token(self, token: str) -> Tuple[List[str], bool]:
        """
        Processes one token, returning (SSE events to emit, stop_streaming).

        Complexity: O(len(token)) amortized for buffering; O(M) per flush
        where M is the flushed chunk size.
        """
        events: List[str] = []
        if not token:
            return events, False

        self.processed_token_count += 1
        self.record("tokens_received")

        if self.max_tokens is not None and self.processed_token_count > self.max_tokens:
            self.provider.abort()
            self.record("aborts")
            events.append('event: error\ndata: {"message": "Budget exceeded"}\n\n')
            return events, True

        self.buffer += token

        # Size-based flushing first: emit fixed-size pieces, keep the remainder.
        if self.policy.max_chunk_chars is not None:
            while len(self.buffer) >= self.policy.max_chunk_chars:
                piece = self.buffer[:self.policy.max_chunk_chars]
                self.buffer = self.buffer[self.policy.max_chunk_chars:]
                events.append("data: %s\n\n" % piece)
                self.record("chunks_flushed")

        # Boundary flushing (v1 behavior) on whatever remains buffered.
        if (self.buffer and self.policy.flush_on_boundary
                and Tokenizer.is_boundary(self.buffer[-1])):
            events.append("data: %s\n\n" % self.buffer)
            self.record("chunks_flushed")
            self.buffer = ""

        return events, False

    def flush_remainder(self) -> List[str]:
        """Flushes any leftover buffer at end of generation (PITFALLS 5)."""
        if self.buffer:
            chunk, self.buffer = self.buffer, ""
            self.record("chunks_flushed")
            return ["data: %s\n\n" % chunk]
        return []

    def error_event(self, exc: BaseException) -> str:
        """Formats a provider error as an SSE error payload."""
        self.record("errors")
        return 'event: error\ndata: {"message": "%s"}\n\n' % str(exc)

    def clear(self) -> None:
        """Aggressively clears local state for the privacy boundary (PITFALLS 3)."""
        self.buffer = None


def _validate_inputs(prompt: str, tenant_id: str, max_tokens: Optional[int],
                     heartbeat_timeout: float, max_buffered_tokens: Optional[int]) -> None:
    """Fail-fast validation for stream_response. Complexity: O(1)."""
    if not prompt:
        raise ValueError("prompt cannot be empty")
    if not tenant_id:
        raise ValueError("tenant_id cannot be empty")
    if max_tokens is not None and max_tokens < 1:
        raise ValueError("max_tokens must be at least 1 when set")
    if heartbeat_timeout <= 0:
        raise ValueError("heartbeat_timeout must be positive")
    if max_buffered_tokens is not None and max_buffered_tokens < 1:
        raise ValueError("max_buffered_tokens must be at least 1 when set")


async def _stream_direct(pipe: _Pipeline, provider: LLMProvider, prompt: str,
                         tenant_id: str, heartbeat_timeout: float) -> AsyncGenerator[str, None]:
    """v1-style pull pipeline: the consumer's await IS the backpressure."""
    generator = provider.async_generate(prompt, tenant_id)
    try:
        while True:
            try:
                token = await asyncio.wait_for(generator.__anext__(), timeout=heartbeat_timeout)
                events, stop = pipe.process_token(token)
                for event in events:
                    yield event
                if stop:
                    break
            except asyncio.TimeoutError:
                pipe.record("heartbeats_sent")
                yield _PING_EVENT
            except StopAsyncIteration:
                break

        for event in pipe.flush_remainder():
            yield event

    except asyncio.CancelledError:
        # Client disconnect: propagate abort upstream (PITFALLS 2).
        provider.abort()
        pipe.record("aborts")
        raise
    except Exception as exc:
        yield pipe.error_event(exc)
    finally:
        pipe.clear()
        generator = None

    yield _DONE_EVENT


async def _stream_bounded(pipe: _Pipeline, provider: LLMProvider, prompt: str,
                          tenant_id: str, heartbeat_timeout: float,
                          max_buffered_tokens: int) -> AsyncGenerator[str, None]:
    """
    Bounded producer/consumer pipeline with explicit pause/resume signaling.

    The producer task pulls tokens into an ``asyncio.Queue`` capped at
    ``max_buffered_tokens``; when the queue is full and the provider exposes
    ``pause()``/``resume()`` (FOLLOW-UPS.md extension 2), the producer signals
    the provider instead of only blocking.
    """
    queue: "asyncio.Queue[Any]" = asyncio.Queue(maxsize=max_buffered_tokens)
    sentinel = object()
    producer_error: List[BaseException] = []

    async def produce() -> None:
        paused = False
        try:
            async for token in provider.async_generate(prompt, tenant_id):
                if queue.full() and hasattr(provider, "pause") and not paused:
                    provider.pause()
                    pipe.record("pauses")
                    paused = True
                await queue.put(token)
                if paused and not queue.full():
                    provider.resume()
                    pipe.record("resumes")
                    paused = False
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # surfaced to the consumer below
            producer_error.append(exc)
        finally:
            if paused:
                try:
                    provider.resume()
                    pipe.record("resumes")
                except Exception:
                    pass
            await queue.put(sentinel)

    producer_task = asyncio.ensure_future(produce())
    try:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=heartbeat_timeout)
            except asyncio.TimeoutError:
                pipe.record("heartbeats_sent")
                yield _PING_EVENT
                continue

            if item is sentinel:
                break

            events, stop = pipe.process_token(item)
            for event in events:
                yield event
            if stop:
                break

        if producer_error:
            yield pipe.error_event(producer_error[0])
        else:
            for event in pipe.flush_remainder():
                yield event

    except asyncio.CancelledError:
        provider.abort()
        pipe.record("aborts")
        producer_task.cancel()
        try:
            await producer_task
        except asyncio.CancelledError:
            pass
        raise
    finally:
        if not producer_task.done():
            producer_task.cancel()
            try:
                await producer_task
            except (asyncio.CancelledError, Exception):
                pass
        pipe.clear()

    yield _DONE_EVENT


async def stream_response(provider: LLMProvider, prompt: str, tenant_id: str,
                          max_tokens: Optional[int] = None,
                          heartbeat_timeout: float = HEARTBEAT_TIMEOUT,
                          chunking_policy: Optional[ChunkingPolicy] = None,
                          metrics: Optional[StreamMetrics] = None,
                          metrics_hook: Optional[Callable[[str, str], None]] = None,
                          max_buffered_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
    """
    The Asynchronous Pipeline, v2.

    Consumes an async token stream from an injected LLMProvider, buffers tokens
    under a ChunkingPolicy, and yields formatted Server-Sent Events.

    - Without ``max_buffered_tokens``: v1-style pull semantics, where awaiting
      the next token is itself the backpressure signal.
    - With ``max_buffered_tokens``: a bounded internal queue decouples the
      producer and explicitly pauses/resumes providers that implement
      ``pause()``/``resume()``.

    Time Complexity: O(N) where N is the total number of yielded tokens.
    Space Complexity: O(M + B) where M is the chunk buffer and B is
    ``max_buffered_tokens`` (0 extra in pull mode).

    Raises (on first iteration):
        ValueError: On empty prompt/tenant, or non-positive limits.
    """
    _validate_inputs(prompt, tenant_id, max_tokens, heartbeat_timeout, max_buffered_tokens)
    pipe = _Pipeline(
        provider=provider,
        max_tokens=max_tokens,
        policy=chunking_policy if chunking_policy is not None else ChunkingPolicy(),
        metrics=metrics if metrics is not None else StreamMetrics(),
        metrics_hook=metrics_hook,
        tenant_id=tenant_id,
    )
    if max_buffered_tokens is None:
        async for event in _stream_direct(pipe, provider, prompt, tenant_id, heartbeat_timeout):
            yield event
    else:
        async for event in _stream_bounded(pipe, provider, prompt, tenant_id,
                                           heartbeat_timeout, max_buffered_tokens):
            yield event
