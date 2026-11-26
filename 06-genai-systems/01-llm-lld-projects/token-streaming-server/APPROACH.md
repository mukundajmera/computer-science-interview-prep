# Approach: Token Streaming Server

## Asynchronous Streaming Pipeline

The implementation is scoped as a single microcomponent that handles stream formatting and orchestration, completely independent of specific LLM models or heavy third-party AI frameworks.

The core mechanism for streaming involves leveraging Python's `asyncio` primitives. By treating the upstream generation as an asynchronous generator (`async for token in provider.generate(...)`), we can process tokens non-blockingly. 

**Trade-offs:**
- *Pros:* Maximizes I/O concurrency without native thread pools, ideal for HTTP serving.
- *Cons:* Requires the entire caller stack (web framework, handlers) to be async-compatible.

## Client Cancellation Detection & Abort Propagation

Client disconnection during a long-running generation must be detected to free up compute resources. 

1. **Passive Disconnect Detection (Implemented)**
   - The web server detects socket closure and raises an `asyncio.CancelledError` within the generator coroutine.
   - A `try/except asyncio.CancelledError:` block catches this signal and immediately calls `.abort()` on the LLM provider interface.
   - *Pros:* Built-in to async web frameworks (like FastAPI/Starlette).
   - *Cons:* May not detect hanging connections without TCP keep-alives or application-layer heartbeats.

2. **Active Polling**
   - The server occasionally polls the connection status.
   - *Pros:* Catches silent drops faster.
   - *Cons:* Adds overhead; generally deferred to the underlying web server implementation.

## Chunk Buffering Strategies

Streaming every micro-token (e.g., individual characters) creates massive DOM thrashing and high network overhead due to SSE envelopes.

1. **Semantic Boundary Buffering (Implemented)**
   - Tokens are accumulated in memory. The buffer flushes to the client when a whitespace or punctuation character is encountered, signifying a word boundary.
   - *Pros:* Dramatically reduces SSE event frequency; frontend updates feel like natural words typing out.
   - *Cons:* Slight latency increase for the very first token to appear (must wait for a full word).

2. **Fixed Time / Token Count Buffering**
   - Flush every $N$ milliseconds or $M$ tokens.
   - *Pros:* Predictable network throughput.
   - *Cons:* Can still break words midway, causing disjointed frontend rendering.

## Heartbeat Keep-Alive Events

If the LLM stalls (e.g., performing an internal tool call or search), intermediate network proxies (like NGINX or AWS ALBs) may time out the idle connection (often after 30-60 seconds).

1. **Asynchronous Timeout Injection (Implemented)**
   - We wrap the `async for` generation call with an `asyncio.wait_for(..., timeout=15)`.
   - If a `TimeoutError` occurs, we yield an SSE event (`event: ping\n\n`) and immediately loop back to waiting for the next token.
   - *Pros:* Keeps the HTTP stream alive transparently to the frontend application logic.
   - *Cons:* Requires precise timeout loop management to avoid accidentally canceling the underlying LLM generation.

## Backpressure Flow Control

If the downstream client reads data slower than the LLM produces it, memory buffers can explode.

1. **Async Write Throttling (Implemented)**
   - The transport layer (or our internal buffer wrapper) blocks the coroutine yielding tokens if the outbound network socket buffer is full.
   - Because `async for` inherently blocks the upstream generation while waiting to yield, backpressure propagates naturally up the stack. The LLM provider (if properly implemented) will slow down generation.
   - *Pros:* Zero data loss; prevents memory exhaustion.
   - *Cons:* A maliciously slow client (Slowloris) can intentionally tie up the LLM inference threads. In production, strict timeout limits and dedicated inference proxy load balancers handle this, decoupling the client socket from the GPU thread.
