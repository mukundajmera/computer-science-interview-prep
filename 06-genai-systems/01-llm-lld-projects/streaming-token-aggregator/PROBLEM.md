# Problem Statement: Streaming Token Aggregator

## Overview

Modern Generative AI systems rely on autoregressive language models that generate responses one token at a time. Because users expect low latency, it is essential to begin streaming tokens to the client immediately rather than waiting for the entire response to be generated. The `Streaming Token Aggregator` sits at the edge of the backend serving layer, buffering tokens emitted by the LLM inference engine and streaming them to HTTP clients using Server-Sent Events (SSE).

## Core Requirements

1. **Token Delivery over HTTP SSE**
   - The aggregator must stream tokens to frontend clients continuously using the standard Server-Sent Events (SSE) format.
   - Each token or chunk must be encapsulated in a valid SSE envelope (e.g., `data: <content>\n\n`).

2. **Concurrency Contract**
   - Multiple threads will interact with the aggregator:
     - **Producer (Model Backend):** Pushes newly generated tokens into the aggregator as they are ready.
     - **Consumer (Web Server / Client Connection):** Drains the aggregator and sends chunks over the network.
   - The buffer must ensure thread-safe operations, maintaining strict ordering of tokens while preventing race conditions or corrupted reads/writes.

3. **Buffer Management & Backpressure**
   - In ideal scenarios, network transmission matches or exceeds the LLM inference speed. However, networks can be slow or clients may stall.
   - The aggregator must implement a bound (e.g., maximum queue size) to prevent unbounded memory growth if the client connection is slow (server-side overflow).
   - If the buffer becomes full, the aggregator must employ a defined backpressure strategy (e.g., dropping the oldest tokens) to keep the stream moving for active components.
   - Conversely, if the client drains the buffer faster than the LLM produces tokens (client-side buffer starvation), the consumer must efficiently block and wait for new tokens without busy looping.

4. **Timeout & Lifecycle Control**
   - Consumers must adhere to timeout limits when waiting for new tokens. If the LLM engine hangs, the connection must unblock and terminate gracefully.
   - The stream must safely transition into a `closed` state when the LLM signals the final token (e.g., `finish_reason` provided), unblocking any waiting consumers.

## Out of Scope
- Complete implementation of the actual LLM engine or model weights.
- Advanced protocol downgrades (e.g., long-polling if SSE fails).
- Direct socket-level TCP window management (assumed to be handled by the web framework/WSGI server).


## Public APIs

The actual implementation exposes the following core public interfaces:
- `StreamingTokenAggregator(max_size: int)`: Initializes the bounded ring buffer.
- `write_chunk(chunk: StreamChunk)`: Pushes a chunk into the buffer.
- `read_stream(timeout_sec: float)`: Yields tokens for the consumer, blocking if empty.
- `format_sse_event(event_type: str, data: str)`: Formats chunks to the SSE protocol text structure.

## Acceptance Case / Fixture
As verified in the test suite (`test_stream_aggregation_in_order`), under normal usage where chunks "Hello", " world", and "!" are written sequentially and the consumer is not backed up, a subsequent read yields all chunks correctly in order ["Hello", " world", "!"].

As verified in the test suite (`test_backpressure_slow_consumer`), if a buffer of size 2 receives four chunks sequentially ("1", "2", "3", "4" where "4" is final), and the consumer hasn't read any, the aggregator correctly drops the two oldest chunks ("1" and "2"). A subsequent read yields only "3" and "4", proving the "drop oldest" backpressure mechanism functions as a shock absorber.

As verified in the error test fixture (`test_read_stream_timeout`), attempting to read from an empty stream with a timeout of 0.1s correctly yields no chunks and unblocks the consumer, proving the timeout safety mechanism.


## Algorithm Complexity
- **Time Complexity**: The actual implementation of both `write_chunk` and `read_stream` yield single items in $O(1)$ time, as array indexing and lock acquisition (uncontended) are constant time operations.
- **Space Complexity**: The actual implemented system requires $O(M)$ space where $M$ is the `max_size` of the buffer pre-allocated as an array.

## Limitations and Privacy Boundaries
- **Limitations**: The actual implementation uses a bounded memory which means data is permanently lost if the backpressure mechanism engages. It does not persist or retry old tokens if the client reconnects.
- **Privacy Boundaries**: Tokens are stored purely in ephemeral process memory. The buffer clears references to streamed tokens by assigning `None` allowing immediate garbage collection, enforcing a strict boundary that streamed data is not unnecessarily retained in memory once delivered.
