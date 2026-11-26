# Distributed Tracing System - Grading Rubric

This rubric helps interviewers evaluate a candidate's high-level design for a Distributed Tracing System.

## 1. Problem Understanding & Requirements (10%)
- **Excellent:** Clearly defines spans, traces, and the need for context propagation (Trace ID, Span ID, Parent ID). Identifies write-heavy nature (high throughput) vs. read-heavy (low frequency, but complex queries).
- **Good:** Understands the basics of tracing but misses some nuances (e.g., forgets to mention parent-child relationships or the difference between logs and traces).
- **Poor:** Confuses tracing with logging or metrics. Does not grasp the scale of data generation.

## 2. Architecture & Component Design (30%)
- **Excellent:** Designs a decoupled pipeline (SDK -> Collector -> Queue -> Processor -> Storage). Correctly utilizes a message queue (Kafka) to handle ingestion spikes. Understands the CQRS pattern for storage (Cassandra for raw spans, Elasticsearch for index).
- **Good:** Proposes a functional architecture but might couple ingestion directly to storage, or misses the need for an inverted index for complex queries.
- **Poor:** Monolithic design, or proposes inappropriate datastores (e.g., writing millions of spans per second into a single PostgreSQL instance).

## 3. Sampling Strategies (25%)
- **Excellent:** Clearly articulates the difference between Head-Based and Tail-Based sampling. Discusses the trade-offs (accuracy vs. cost). Explains how Tail-Based sampling requires consistent routing by Trace ID and memory buffering in stream processors.
- **Good:** Understands that sampling is necessary but struggles to explain how to implement Tail-Based sampling or why Head-Based sampling might miss errors.
- **Poor:** Does not mention sampling, or proposes unscalable sampling methods (e.g., storing everything and deleting it later).

## 4. Scalability & Fault Tolerance (20%)
- **Excellent:** Explains how to scale collectors horizontally. Discusses Kafka partitioning by Trace ID. Addresses what happens if an ingestion worker (Stream Processor) crashes (loss of in-memory buffer) and how to mitigate it (e.g., accepting minor data loss vs. using persistent state stores).
- **Good:** Identifies single points of failure but lacks concrete mitigation strategies.
- **Poor:** Ignores failover scenarios or assumes infinite vertical scaling.

## 5. Capacity Estimation (15%)
- **Excellent:** Provides realistic estimates for QPS, bandwidth, and storage. Correctly applies the sampling rate to storage calculations but not to ingestion bandwidth (if doing Tail-Based).
- **Good:** Rough estimates, but logic is sound. Might miss the distinction between ingestion volume and retained volume.
- **Poor:** Wildly inaccurate estimates, math errors, or skips estimations entirely.
