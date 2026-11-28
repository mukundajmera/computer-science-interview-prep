# Distributed Tracing System — Comparison

This guide compares key architectural trade-offs inside a distributed tracing pipeline, explains how this pack differs from the sibling [Distributed Tracing](../distributed-tracing/DESIGN.md) pack, and contrasts tracing ID generation with [Distributed Unique ID Generator (Snowflake)](../distributed-unique-id-snowflake/DESIGN.md).

---

## 1. How `distributed-tracing-system` Differs from `distributed-tracing`

Both packs solve the distributed request-tracing problem using W3C TraceContext propagation, a Kafka ingestion buffer, and tail-based sampling, but they model different architectural variants and study depths:

| Dimension | [Distributed Tracing](../distributed-tracing/DESIGN.md) | Distributed Tracing System (This Pack) |
|---|---|---|
| **Target Scale & Retention** | 1M spans/sec, ~600 B/span (~600 MB/s), 14-day retention (~145 TB compressed) | 5M spans/sec (100K RPS × 50 spans), ~500 B/span (2.5 GB/s / 20 Gbps), 7-day retention (~15 TB at 1% sampled) |
| **Collector Topology** | Per-host local OpenTelemetry sidecar daemon on `localhost` | Horizontally scaled stateless collector fleet behind a load balancer using consistent hashing on `trace_id` |
| **Storage Architecture** | Single unified columnar store (ClickHouse with `ReplacingMergeTree` deduplication) | **CQRS split:** Cassandra / ScyllaDB (raw span payloads keyed by `trace_id`) + Elasticsearch / OpenSearch (inverted tag & service index) |
| **Pre-Sampling Metrics** | Focuses on trace collection and DAG assembly | Explicitly extracts pre-sampling **RED metrics** (Rate, Errors, Duration) from 100% of spans into a TSDB before tail sampling drops normal traces |
| **Pack Extras** | Runnable Java and Python simulators (`TailSampler`, `DAGAssembler`) plus `diagrams/architecture.mmd` | Dedicated [CAPACITY.md](./CAPACITY.md) (including 75 GB distributed tail-sampling RAM buffer math) and deeper operational trade-off prose |
| **When to Study** | Start here for the concise baseline architecture, columnar storage trade-offs, and runnable code | Study this pack for CQRS storage separation, pre-sampling RED-metrics pipelines, and high-throughput capacity sizing |

---

## 2. Sampling Strategies: Head-Based vs. Tail-Based vs. Hybrid

| Dimension | Head-Based Sampling | Tail-Based Sampling | Hybrid (Head + Tail) |
|---|---|---|---|
| **Decision Point** | At the edge / root SDK before downstream RPCs fire | In stateful stream processors after buffering the trace window (10–30 s) | Coarse filter at edge + rule-based evaluation at tail |
| **Ingestion Bandwidth** | Lowest (drops unsampled traces at the source) | Highest (ingests 100% of spans; 2.5 GB/s at 5M spans/sec) | Moderate (sheds high-volume healthy noise early) |
| **Error & Tail-Latency Capture** | Probabilistic (can miss rare 5xx errors or P99 spikes) | Near-complete (keeps all traces with `error=true` or latency > threshold) | High for errors/slow traces if edge flags or retains anomalous routes |
| **Infrastructure Complexity** | Low (stateless; propagates sampled flag in `traceparent`) | High (Kafka partitioning by `trace_id` + 75 GB distributed RAM buffer) | High (coordinated rule distribution to both SDKs and stream processors) |
| **Best Fit** | Cost-constrained clusters with uniform traffic | Production debugging where missing errors is unacceptable | Very large fleets balancing ingestion cost and anomaly recall |

---

## 3. Storage Engines: CQRS Split vs. Unified Columnar vs. Object Storage

| Aspect | CQRS Split (Cassandra/ScyllaDB + Elasticsearch) | Unified Columnar (ClickHouse) | Object Storage + Lightweight Index (S3 + Parquet) |
|---|---|---|---|
| **Write Throughput** | Very high (LSM-tree sequential appends in Cassandra) | Extremely high (batched columnar inserts) | Very high (batched block flushes) |
| **Compression & Cost** | Moderate (LZ4/Snappy in Cassandra + inverted index overhead in ES) | Excellent (5×+ columnar compression on a single engine) | Lowest storage cost for longer retention |
| **Point Lookup by `trace_id`** | Fast (direct partition-key lookup) | Fast (when `trace_id` leads the primary/sorting key) | Moderate (Bloom filters + object-store block fetch) |
| **Tag & Attribute Search** | Rich ad-hoc queries via Elasticsearch inverted indexes | Fast vectorized filtering on structured columns and `Map` tags | Limited without a companion tag index |
| **Operational Complexity** | Higher (two datastores, dual-write sync, aligned TTLs) | Lower (single engine for lookups and tag queries) | Low storage ops, higher query-tier caching complexity |

---

## 4. Collector Topology Trade-offs

| Aspect | Local Sidecar / Node Agent | Stateless Collector Fleet (Behind LB) | Two-Tier (Node Agent + Gateway Fleet) |
|---|---|---|---|
| **App Overhead** | Lowest (loopback UDP/gRPC on `localhost`) | Low-to-moderate (SDK batches directly over network) | Lowest on app (agent batches locally; gateway routes) |
| **Trace-ID Routing for Tail Sampling** | Relies on Kafka partitioning downstream | Collector hashes `trace_id` directly to Kafka partitions / aggregators | Gateway tier routes by `trace_id` to stateful tail samplers |
| **Deployment Footprint** | DaemonSet/sidecar on every host; upgrades touch fleet | Centralized autoscaling pool | Two tiers to operate and monitor |

---

## 5. ID Generation: Tracing IDs vs. [Snowflake](../distributed-unique-id-snowflake/DESIGN.md)

Distributed tracing requires generating a globally unique `trace_id` at every ingress request (100K/sec) and a unique `span_id` for every service hop (5M/sec). It is worth contrasting why tracing systems do **not** use a centralized or Snowflake-style ID service (see [Distributed Unique ID Generator (Snowflake)](../distributed-unique-id-snowflake/DESIGN.md) and [Unique ID Generator](../unique-id-generator/DESIGN.md)):

| Dimension | W3C TraceContext IDs (Used Here) | Snowflake-Style 64-Bit IDs |
|---|---|---|
| **Bit Width & Format** | 128-bit random `trace_id` (32 hex chars); 64-bit random `span_id` (16 hex chars) | 64-bit integer (41-bit ms timestamp + 10-bit worker ID + 12-bit sequence) |
| **Coordination** | **Zero** — generated locally in-process via CSPRNG/PRNG inside the SDK | Requires worker-ID lease coordination (ZooKeeper/etcd) and NTP skew handling |
| **Time Ordering** | Not encoded in the ID; spans carry explicit `start_time_unix_nano` | Encoded in high bits for B-tree index locality |
| **Hot-Partition Risk** | Uniformly random `trace_id` hashes evenly across Kafka partitions and Cassandra nodes | Time-prefixed IDs can cluster recent writes on range-partitioned stores unless hashed |
| **Why Chosen Here** | Instrumentation must add < 1–2 ms overhead and never fail if a coordinator is unreachable; 128-bit randomness makes collisions negligible across 5M spans/sec | Best for relational primary keys (`BIGINT`) where compact 8-byte sortable integers matter |

---

## Related Packs
- [Distributed Tracing](../distributed-tracing/DESIGN.md) — Baseline tracing pack with ClickHouse and runnable simulators.
- [Distributed Unique ID Generator (Snowflake)](../distributed-unique-id-snowflake/DESIGN.md) — 64-bit coordinated time-ordered ID generation.
- [Unique ID Generator](../unique-id-generator/DESIGN.md) — Broader ID strategy comparison (Ticket Server, UUID/ULID, Snowflake).
