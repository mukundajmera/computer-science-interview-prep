# Strong Answer

*(Time-boxed 90 second summary)*

**Say:** "To design this Distributed Tracing System, I've chosen a write-heavy telemetry pipeline architecture.

The core flow starts with Context Propagation using the W3C Trace Context standard. Applications generate Spans and send them asynchronously via UDP or local gRPC to a local Collector Sidecar to ensure zero blocking on the critical path.

The sidecars batch and send the data to a central Kafka cluster. Kafka is critical here as a durable buffer; it absorbs traffic spikes and prevents data loss if our storage tier experiences downtime. 

From Kafka, we use Ingestion Workers to consume the streams, partitioned by Trace ID. This allows us to implement Tail-based sampling—we buffer the spans in memory for 30 seconds and only write the full trace to storage if it contains an error or exceeds a p99 latency threshold.

Finally, the surviving spans are written to ClickHouse. A columnar database is ideal here for high-throughput writes, massive compression, and fast analytical queries required to assemble and visualize the Trace DAGs."
