# Distributed Tracing System - Common Pitfalls

When designing a distributed tracing system, candidates often fall into several predictable traps. This document outlines those common pitfalls.

## 1. Storage Choice Mismatch
- **The Pitfall:** Choosing a standard Relational Database (e.g., MySQL, PostgreSQL) to store raw tracing data.
- **Why it's wrong:** Tracing data is generated at millions of spans per second. RDBMS systems using B-Trees suffer from massive write amplification and index locking under this kind of load. 
- **The Fix:** Use an LSM-Tree based NoSQL store (like Cassandra, HBase, or ScyllaDB) optimized for massive, rapid, append-only writes, keyed by Trace ID.

## 2. Ignoring the Search Requirement (Missing CQRS)
- **The Pitfall:** Assuming Cassandra can handle both writing the raw spans *and* answering queries like "Find all traces where service=Checkout and error=true".
- **Why it's wrong:** Cassandra is terrible at multi-column ad-hoc search. If you don't query by the partition key (Trace ID), it requires a full table scan, which will timeout.
- **The Fix:** Implement a CQRS pattern. Write raw payloads to Cassandra (Trace ID -> Payload). Asynchronously write searchable metadata (tags, service name, Trace ID) to an Inverted Index (like Elasticsearch). Query Elasticsearch to get IDs, then fetch payloads from Cassandra.

## 3. Misunderstanding Tail-Based Sampling
- **The Pitfall:** Assuming tail-based sampling can be done instantly at the collector without state.
- **Why it's wrong:** A trace is composed of many spans arriving over time (e.g., a request takes 2 seconds, spans arrive over 5 seconds due to network jitter). You cannot make a decision about the *whole* trace until you wait for all parts of it.
- **The Fix:** Explicitly state the need for stream processors (e.g., Flink) that hold spans in an in-memory buffer/window. Note that this requires routing all spans for a specific `Trace ID` to the *same* processor instance via Kafka partitioning.

## 4. Coupling Ingestion to Processing
- **The Pitfall:** Having the collectors directly call the database or Elasticsearch.
- **Why it's wrong:** Traffic spikes (e.g., a Black Friday event or a cascading failure causing massive error logging) will overwhelm the database, causing backpressure that crashes the tracing agents, potentially taking down the monitored services.
- **The Fix:** Introduce a Message Queue (Kafka) as a shock absorber between ingestion and processing/storage.

## 5. Over-engineering for 100% Reliability
- **The Pitfall:** Designing complex two-phase commits or synchronous replication for tracing data to ensure zero data loss.
- **Why it's wrong:** Tracing is observability data. If a node crashes and you lose 0.01% of traces during a 5-second window, the business does not lose money (unlike a payments database). The overhead of strict consistency destroys throughput.
- **The Fix:** Accept minor data loss. Use asynchronous replication, fire-and-forget UDP/gRPC from agents, and in-memory buffers in stream processors without writing to disk first. Favor availability and throughput over strict consistency.
