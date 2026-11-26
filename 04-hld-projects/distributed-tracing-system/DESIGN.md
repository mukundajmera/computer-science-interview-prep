# Distributed Tracing System - High Level Design

## Architecture Overview

A distributed tracing system typically follows a pipeline architecture designed to ingest, process, store, and serve telemetry data with high throughput and low latency. 

### Core Components

#### 1. Tracing Agents / SDKs
- Embedded within application code (e.g., OpenTelemetry SDK).
- Generates spans, injects/extracts context across process boundaries (W3C TraceContext).
- Performs local buffering, batching, and often **Head-Based Sampling** before sending data over the network via gRPC or UDP.

#### 2. Collector / Ingestion Layer
- Horizontally scalable stateless services.
- Receives batches of spans from various agents.
- Performs basic validation, formatting, and enriches data if necessary.
- Acts as a buffer to handle traffic spikes. 
- For **Tail-Based Sampling**, collectors route spans with the same Trace ID to specific downstream aggregators using consistent hashing.

#### 3. Message Queue (Buffer)
- e.g., Apache Kafka.
- Decouples ingestion from processing and storage.
- Absorbs massive traffic spikes and prevents downstream systems (like databases) from being overwhelmed.

#### 4. Stream Processors / Aggregators
- Reads from the message queue.
- If using Tail-Based Sampling, buffers all spans for a trace in memory for a short window (e.g., 10-30 seconds).
- Evaluates the complete trace against sampling rules (e.g., keep if `error=true` or `duration > 2s`).
- Forwards selected traces to storage and discards the rest.
- Aggregates metrics (e.g., RED metrics - Rate, Errors, Duration) and writes them to a Time Series Database (TSDB).

#### 5. Storage Layer
Tracing requires specific storage patterns:
- **Trace Storage (Blob/Object Storage or NoSQL):** e.g., Cassandra, ScyllaDB, or S3-compatible storage for older traces. Optimized for high-throughput writes and point lookups by Trace ID.
- **Search Index (Inverted Index):** e.g., Elasticsearch, OpenSearch, or ClickHouse. Used to index tags, service names, and operations to quickly find Trace IDs that match user queries.

#### 6. Query Service & UI
- Provides an API for the frontend UI.
- Queries the Search Index to find Trace IDs.
- Retrieves the full span payloads from Trace Storage using the Trace IDs.
- Reconstructs the trace tree (DAG) and visualizes the timeline, relationships, and bottlenecks.

## System Diagram (Conceptual)

```
[Service A (SDK)] --> [Collector] 
[Service B (SDK)] --> [Collector] --> [Kafka] --> [Stream Processor (Tail Sampler)] --> [Cassandra (Trace Store)]
[Service C (SDK)] --> [Collector]                                                 --> [Elasticsearch (Index)]
                                                                                  --> [TSDB (Metrics)]
                                                                                  
[UI] --> [Query Service] --> [Elasticsearch (Find Trace IDs)]
                         --> [Cassandra (Fetch Spans by Trace ID)]
```

## Data Model

### Span Record
```json
{
  "trace_id": "1234abcd",
  "span_id": "5678efgh",
  "parent_span_id": "9012ijkl", // null for root span
  "service_name": "checkout-service",
  "operation_name": "ProcessPayment",
  "start_time_unix_nano": 1678886400000000000,
  "duration_nano": 150000000,
  "tags": {
    "http.status_code": "500",
    "error": "true"
  },
  "events": [ // Logs attached to the span
    { "time": 1678886400050000000, "name": "Payment Gateway Timeout" }
  ]
}
```