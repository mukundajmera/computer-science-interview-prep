# Distributed Tracing System - Approach & Architecture

## System Architecture

The solution utilizes a highly scalable, decoupled pipeline architecture to handle the massive volume of telemetry data without impacting the performance of monitored microservices.

### 1. Instrumentation and Context Propagation
- **SDKs:** Applications are instrumented using standard SDKs (e.g., OpenTelemetry). 
- **Context:** Trace context (Trace ID, Parent Span ID) is injected into and extracted from HTTP/gRPC headers (W3C TraceContext standard) to maintain the distributed execution graph.
- **Batching:** SDKs buffer spans in memory and send them in batches via UDP or gRPC to reduce network overhead.

### 2. Ingestion (Collectors)
- **Stateless Collectors:** A fleet of collectors deployed behind a load balancer receives spans from application SDKs.
- **Validation & Transformation:** They perform basic validation, normalize data formats, and attach necessary metadata.
- **Routing:** If utilizing Tail-Based Sampling, collectors use consistent hashing on the `Trace ID` to ensure all spans belonging to the same trace are routed to the same partition in the Message Queue.

### 3. Message Queue (Kafka)
- **Decoupling:** Apache Kafka sits between ingestion and processing. It acts as a shock absorber during traffic spikes.
- **Partitioning:** Data is partitioned by `Trace ID`. This guarantees that the downstream stream processor handling partition `N` will receive *all* spans for a given trace.

### 4. Stream Processing (Tail-Based Sampling)
- **Buffering:** Stream processors (e.g., Flink, or custom microservices) consume from Kafka. They buffer incoming spans in memory based on the `Trace ID`.
- **Windowing:** The buffer is held open for a specific window (e.g., 30 seconds after the first span arrives) to allow out-of-order or delayed spans to arrive.
- **Sampling Decision:** Once the window closes, the processor evaluates the entire assembled trace.
    - If any span contains an error tag (`error=true`).
    - If the total trace duration exceeds a latency threshold (e.g., > 2000ms).
    - If it passes a baseline probabilistic rate (e.g., 0.1% of all normal traffic).
- **Dispatch:** Retained traces are forwarded to the storage layer. Discarded traces are dropped.
- **Metrics Extraction:** The stream processor also extracts RED (Rate, Errors, Duration) metrics from *all* ingested spans (before sampling) and pushes them to a Time Series Database (TSDB) like Prometheus. This ensures metrics are 100% accurate even if traces are sampled.

### 5. Storage Layer (CQRS Pattern)
Tracing data requires different access patterns for writes and reads, making a CQRS (Command Query Responsibility Segregation) approach ideal.

- **Trace Storage (Cassandra / ScyllaDB):**
    - Optimized for extremely fast, high-volume writes.
    - Data is keyed by `Trace ID`.
    - Used to fetch the raw span data when a user wants to view a specific trace.
- **Search Index (Elasticsearch / OpenSearch):**
    - Optimized for complex queries (search by service, operation, tags).
    - Only indexes metadata (Trace ID, tags, timestamps) rather than the heavy raw payload to save space and improve performance.
    - Used to find a list of `Trace IDs` that match user criteria.

### 6. Query API and Visualization
- **Query Service:** When a user searches for "Checkout Service errors in the last 15 minutes", the API queries Elasticsearch to get a list of Trace IDs. 
- **Assembly:** It then fetches the full span payloads for those IDs from Cassandra. It assembles the spans into a Directed Acyclic Graph (DAG) based on `span_id` and `parent_span_id`.
- **UI:** The frontend renders this DAG as a Gantt chart or a network graph.

## Trade-offs & Alternatives

### Head-Based vs. Tail-Based Sampling
- **Head-Based (SDK-side):** The decision to sample is made at the root span. 
    - *Pros:* Easy to implement, drastically reduces ingestion bandwidth and processing costs. 
    - *Cons:* You might discard a trace early on, only to realize later down the call chain that an error occurred. You miss valuable data for debugging rare issues.
- **Tail-Based (Processor-side):** 100% of data is ingested. The decision is made after the trace is complete. 
    - *Pros:* Never miss an error or slow request. Highly accurate debugging.
    - *Cons:* Requires massive ingestion infrastructure, Kafka clusters, and memory buffering in stream processors. Much more expensive to run.
- *Chosen Approach:* We designed for Tail-Based Sampling to meet the requirement of not losing anomalous traces, leveraging Kafka and partitioned Stream Processors to handle the load.

### Storage Choice: Cassandra vs. RDBMS
- Relational databases (like PostgreSQL) use B-Trees, which struggle with the massive, constant write-heavy workload of tracing data. They require complex sharding.
- Cassandra uses LSM (Log-Structured Merge) trees, which excel at write-heavy append-only workloads. Data is distributed automatically via consistent hashing.

### Pull vs. Push Metrics
- Tracing systems push spans to collectors. However, extracted metrics (from the stream processors) can be pushed to a TSDB (like InfluxDB) or exposed via an endpoint for Prometheus to pull.
