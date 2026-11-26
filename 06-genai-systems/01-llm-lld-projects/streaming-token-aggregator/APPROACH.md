# Approach: Streaming Token Aggregator

## Backpressure Strategies

When the internal ring buffer becomes full (because the LLM produces tokens faster than the network can transmit them), the aggregator must employ a backpressure strategy. There are several trade-offs:

## Acceptance Case / Fixture
As verified in the test suite (`test_stream_aggregation_in_order`), under normal usage where chunks "Hello", " world", and "!" are written sequentially via `write_chunk` and the consumer is not backed up, a subsequent `read_stream` yields all chunks correctly in order ["Hello", " world", "!"].

As verified in the test suite (`test_backpressure_slow_consumer`), if a buffer of size 2 receives four chunks sequentially ("1", "2", "3", "4" where "4" is final), and the consumer hasn't read any, the aggregator correctly drops the two oldest chunks ("1" and "2"). A subsequent `read_stream` yields only "3" and "4", proving the "drop oldest" backpressure mechanism functions as a shock absorber.

As verified in the error test fixture (`test_read_stream_timeout`), attempting to read from an empty stream with a timeout of 0.1s correctly yields no chunks and unblocks the consumer, proving the timeout safety mechanism.


1. **Drop Oldest (Current Implementation)**
   - **How it works:** When a new token arrives via `write_chunk`, the buffer overwrites the oldest unread token by advancing the `head` pointer, before the consumer can consume it via `read_stream`.
   - **Pros:** Keeps the stream "live." The client receives the most recent output, which is often preferable for UI responsiveness (e.g., jumping to the end of a long generation). Never blocks the producer, ensuring LLM inference threads are not stalled by slow clients.
   - **Cons:** Loss of data. The client will miss intermediate tokens, resulting in text jumping or skipping.

2. **Drop Newest**
   - **How it works:** When the buffer is full, new incoming tokens are simply discarded until space frees up.
   - **Pros:** Easy to implement. Preserves the contiguous start of the generation.
   - **Cons:** The client receives a stalled, outdated stream and then suddenly misses a large chunk of text when it finally catches up. Generally worse UX than dropping the oldest.

3. **Block Producer**
   - **How it works:** The producer thread calls `wait()` on a condition variable when the buffer is full, blocking until the consumer reads a token.
   - **Pros:** Zero data loss. Guarantees perfect token delivery.
   - **Cons:** **Severe systemic risk.** If a single client connection hangs or is intentionally slow (e.g., a Slowloris attack), the LLM inference thread blocks. Since LLM resources are incredibly expensive and typically shared, stalling the producer can cause widespread cluster degradation.

4. **TCP Window Throttling**
   - **How it works:** Relies entirely on the OS network stack. If the client doesn't ACK packets, the TCP window fills, the web server's socket buffer fills, and eventually the application-level write blocks.
   - **Pros:** Standard network behavior.
   - **Cons:** Still leads to blocked application threads (same risk as blocking the producer).

**Decision:** "Drop Oldest" is implemented because protecting the shared LLM inference engine from stalling is strictly more important than guaranteeing perfect token delivery to a slow client.

## Unimplemented Advanced Extension: Aggregation Boundaries

While a basic aggregator streams every single token individually, this can cause issues on the frontend. LLM tokens are often sub-word fragments (e.g., " re", "act", "ion"). Rapidly firing hundreds of SSE events per second for partial words causes significant DOM render thrashing in the browser.

An advanced approach involves aggregating tokens in the buffer and flushing them on logical boundaries:
- **Word Boundaries:** Flush when a space character is encountered.
- **Sentence Boundaries:** Flush when punctuation (., !, ?) is encountered.
- **Time/Batch Limits:** Flush every *N* milliseconds or after *M* tokens accumulate.

While the current `v1-basic` implementation yields individual chunks as they are read, a real-world system would likely wrap this aggregator with a batching layer that concatenates `chunk.text` strings until a boundary condition is met, emitting fewer, larger SSE events to optimize client CPU usage.

## Public APIs

The actual implementation exposes the following core public interfaces:
- `StreamingTokenAggregator(max_size: int)`: Initializes the bounded ring buffer.
- `write_chunk(chunk: StreamChunk)`: Pushes a chunk into the buffer.
- `read_stream(timeout_sec: float)`: Yields tokens for the consumer, blocking if empty.
- `format_sse_event(event_type: str, data: str)`: Formats chunks to the SSE protocol text structure.

## Algorithm Complexity
- **Time Complexity**: The actual implementation of both `write_chunk` and `read_stream` yield single items in $O(1)$ time, as array indexing and lock acquisition (uncontended) are constant time operations.
- **Space Complexity**: The actual implemented system requires $O(M)$ space where $M$ is the `max_size` of the buffer pre-allocated as an array.

## Limitations and Privacy Boundaries
- **Limitations**: The actual implementation uses a bounded memory which means data is permanently lost if the backpressure mechanism engages. It does not persist or retry old tokens if the client reconnects.
- **Privacy Boundaries**: Tokens are stored purely in ephemeral process memory. The buffer clears references to streamed tokens by assigning `None` allowing immediate garbage collection, enforcing a strict boundary that streamed data is not unnecessarily retained in memory once delivered.
