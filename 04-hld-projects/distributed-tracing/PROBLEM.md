# Distributed Tracing

## Problem Statement

Modern microservice architectures are highly distributed. A single user request might touch dozens or hundreds of downstream services before returning a response. When errors occur or latency spikes, it is incredibly difficult to determine *which* service in the chain caused the problem. 

We need to design a **Distributed Tracing System** (similar to Dapper, Zipkin, Jaeger, or Honeycomb) that can record the path of a request across all service boundaries, assemble these paths into a coherent DAG (Directed Acyclic Graph) of operations, and allow developers to query and visualize the resulting traces.

## Core Requirements

1. **Context Propagation:** Provide a standard mechanism to pass trace identifiers across service boundaries (HTTP headers, gRPC metadata, message queues).
2. **Ingestion & Buffering:** Receive telemetry data (Spans) from thousands of concurrent nodes without blocking the critical path of the application.
3. **Sampling:** Support strategies to reduce the volume of stored data, including head-based (random % at the edge) and tail-based (buffering entire traces and retaining them based on error/latency rules).
4. **DAG Assembly:** Reconstruct traces by linking parent and child spans and calculating critical paths and cumulative latency.
5. **Storage & Querying:** Store vast amounts of structured event data and support queries on trace ID, service name, duration, and arbitrary key-value tags.

## Capacity & Traffic Scenario

- **Traffic:** 1,000,000 spans/sec.
- **Span Size:** 600 bytes on average.
- **Retention:** 14 days hot storage.
- **Overhead:** < 2ms tail-latency overhead for instrumented apps.

## Non-Functional Requirements

- **Low Overhead:** Instrumentation must have near-zero performance impact on the host application (e.g., < 2ms tail-latency).
- **High Throughput:** The collector pipeline must handle 1,000,000 spans per second.
- **High Availability:** Ingestion cannot fail, even if the storage layer is degraded.
- **Durability (Post-Ingestion):** Once acknowledged by the buffer, spans should not be lost.
