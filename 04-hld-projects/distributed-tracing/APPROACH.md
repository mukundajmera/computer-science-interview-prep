# Approach: Distributed Tracing

Designing a distributed tracing system requires solving for three distinct phases: **Collection & Propagation**, **Ingestion & Processing**, and **Storage & Querying**.

## Collection & Propagation

The edge gateway or first service generates a unique `Trace ID`. As the request moves through the system, each operation (database call, downstream HTTP request) is recorded as a `Span` with its own `Span ID`. To link them, we need to pass the `Trace ID` and the current `Span ID` (as the `Parent ID`) to the next service.

The proposed architecture adopts the **W3C Trace Context standard**. The HTTP header `traceparent: 00-{trace-id}-{parent-id}-{trace-flags}` is used for propagation.

## Ingestion & Processing

To minimize impact on applications and meet the < 2ms tail-latency overhead constraint, services send spans asynchronously via UDP or local gRPC to a **local sidecar daemon (OTel Collector)**.

The sidecar buffers and batches spans, then forwards them to a distributed queue like **Kafka**. Kafka decouples ingestion from storage, providing a highly durable buffer that absorbs traffic spikes.

Ingestion workers consume from Kafka. Here, we can apply **Tail-based sampling**. Workers buffer spans for a given trace in memory (or Redis) for a short window (e.g., 30s). When the window closes, if the trace contains an error or latency > 1s, the entire trace is written to storage; otherwise, it is dropped.

## Storage & Querying

Spans are highly structured immutable events, ideal for a **Columnar Database** (like ClickHouse or Apache Cassandra with custom indexing). We need to query by arbitrary tags (e.g., `http.status_code`, `user_id`). Columnar storage allows efficient compression and fast aggregation over massive datasets, which is essential for rendering trace visualizations and DAG assembly.
