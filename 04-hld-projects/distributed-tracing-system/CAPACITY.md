# Distributed Tracing System - Capacity Estimation

This document provides capacity estimations for the distributed tracing system based on the typical interview constraints provided in the problem statement.

## Assumptions

- **Incoming Request Rate (System-wide):** 100,000 requests per second (RPS).
- **Spans per Request:** On average, 1 request generates 50 spans (as it fans out across microservices).
- **Average Span Size:** 500 bytes.
- **Data Retention Period:** 7 days.
- **Sampling Rate:** We will assume a tail-based sampling strategy that ultimately retains 1% of all traces for long-term storage, but requires 100% ingestion and buffering.

## 1. Traffic (Throughput & Bandwidth)

### Spans Generated per Second
* `Total Spans/sec = Requests/sec * Spans/Request`
* `Total Spans/sec = 100,000 * 50 = 5,000,000 spans/sec (5 Million)`

### Ingestion Bandwidth (Network I/O)
* `Ingestion Bandwidth = Total Spans/sec * Average Span Size`
* `Ingestion Bandwidth = 5,000,000 * 500 bytes = 2.5 GB/sec`
* `2.5 GB/sec * 8 bits/byte = 20 Gbps (Gigabits per second)`

*Note: This is the traffic hitting the Collectors and the Message Queue. This requires a highly scalable ingestion layer and a robust messaging system (like Kafka) provisioned for extremely high throughput.*

## 2. Storage Estimation

Because 100% of data is ingested but only 1% is stored (after tail-based sampling), we must calculate the storage for the retained data.

### Retained Spans per Second
* `Retained Spans/sec = Total Spans/sec * Sampling Rate`
* `Retained Spans/sec = 5,000,000 * 0.01 = 50,000 spans/sec`

### Storage Needed per Day
* `Storage/sec = Retained Spans/sec * Average Span Size`
* `Storage/sec = 50,000 * 500 bytes = 25 MB/sec`
* `Storage/hour = 25 MB/sec * 3600 = 90,000 MB/hour (90 GB/hour)`
* `Storage/day = 90 GB/hour * 24 = 2,160 GB/day (~2.16 TB/day)`

### Total Storage Needed (7 Days Retention)
* `Total Storage = Storage/day * Retention Period`
* `Total Storage = 2.16 TB/day * 7 days = 15.12 TB`

*Note: This is raw data. Databases (like Cassandra) often compress data (e.g., LZ4 or Snappy) which might reduce this by 30-50%. However, indexing (in Elasticsearch) will add overhead. It is safe to estimate ~15-20 TB of total cluster storage needed.*

## 3. Memory Estimation (Tail-Based Sampling Buffer)

If using tail-based sampling, the system must buffer traces in memory (or fast SSDs) for a short window (e.g., 30 seconds) until the trace completes, before making a sampling decision.

* `Buffered Data/sec = Ingestion Bandwidth = 2.5 GB/sec`
* `Total Memory Buffer = Buffered Data/sec * Buffer Window`
* `Total Memory Buffer = 2.5 GB/sec * 30 seconds = 75 GB`

*Note: 75 GB of RAM distributed across a cluster of Stream Processors (e.g., 10 nodes with 8-16GB RAM each dedicated to buffering) is very manageable.*

## Summary

| Metric | Estimation |
| :--- | :--- |
| **Ingestion RPS (Spans)** | 5 Million / sec |
| **Ingestion Bandwidth** | 2.5 GB/sec (20 Gbps) |
| **Write RPS to Storage (1% Sampled)** | 50,000 / sec |
| **Total Storage (7 Days, 1% Sampled)** | ~15 TB |
| **Tail-Sampler Memory Buffer (30s)** | 75 GB (Distributed) |
