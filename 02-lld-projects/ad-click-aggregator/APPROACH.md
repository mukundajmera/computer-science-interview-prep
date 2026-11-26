# Approach for Ad Click Aggregator

## Overview and Core Strategy
The Ad Click Aggregator is engineered to process an enormous volume of advertising click events, summarize them over defined time intervals, and provide low-latency querying capabilities for downstream billing and analytics systems. The primary architectural challenge lies in balancing high throughput with data accuracy, particularly when dealing with delayed, duplicate, or out-of-order events from global edge nodes. Our approach centers on a stream processing architecture, eschewing traditional batch processing to ensure near real-time visibility into campaign performance.

To achieve this, we adopt an event-driven model that incrementally layers on complexity. In **v1-basic**, we focus on in-memory counters by key, and ensure empty input and invalid event payloads fail predictably. In **v2-extended**, we introduce pluggable deduplication and windowing policies. Finally, in **v3-optimized**, we deploy a concurrent ingestion pipeline and replay-friendly state snapshots within standard library boundaries.

## Windowing and Watermarking
A critical aspect of our approach is how we handle time. Window-boundary, late-event and out-of-order timestamp examples state processing-time/event-time policy. We strictly use "event time" (the time the click actually occurred on the user's device) rather than "processing time" (the time our server received it). This distinction is vital for maintaining accurate historical records, especially when mobile clients reconnect after losing signal and upload batches of older clicks.

We implement sliding and tumbling time windows. Because events can arrive out of order, we use a watermarking strategy. A watermark is a heuristic timestamp indicating that the system does not expect any more events older than that time. When the watermark passes the end of a window, that window is considered "closed," and its aggregated state is committed. Any events arriving after the window has closed are considered "late" and are routed to a separate dead-letter queue for daily batch reconciliation.

## Deduplication Strategy
Click fraud and network retries often lead to duplicate events. To ensure billing accuracy, deduplication is paramount. Duplicate event IDs affect billing aggregates exactly once; probabilistic filters only accelerate an exact deduplication check. We achieve this within our standard library constraints by utilizing an in-memory bitset (bloom filter approximation) followed by a definitive check against an exact event set, avoiding external dependencies like Redis.

## State Management
Maintaining the state of active windows requires careful consideration. Storing it entirely in memory is fast but volatile. We use a hybrid approach: active windows are kept in memory for high-speed increments, but in **v3-optimized**, we periodically snapshot this state to local persistent storage (e.g. standard file I/O). If a processing node crashes, a new node can resume from the last offset and reload the state from the persistent snapshot, ensuring exactly-once processing semantics without data loss.
