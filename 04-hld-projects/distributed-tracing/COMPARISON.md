# Architecture Comparisons

| Feature | Elasticsearch (Document) | ClickHouse (Columnar) |
|---|---|---|
| **Write Throughput** | Medium/High | Extremely High |
| **Compression** | Moderate | Excellent (Run-length encoding on columns) |
| **Query Speed (Aggregations)** | Fast (Inverted Index) | Extremely Fast (Vectorized execution) |
| **Schema Flexibility** | High (Dynamic mapping) | Moderate (Requires Map types or schema migrations) |
| **Best For** | Full-text search on logs | Structured telemetry (Tracing, Metrics) |

| Strategy | Head-Based Sampling | Tail-Based Sampling |
|---|---|---|
| **Decision Point** | At the edge/gateway | Post-collection (Workers) |
| **Network Overhead** | Low (Drops data early) | High (Transmits 100% to workers) |
| **Value of Kept Data** | Random (Might miss errors) | High (Guaranteed to keep errors/slow traces) |
| **Complexity** | Low | High (Stateful buffering) |
