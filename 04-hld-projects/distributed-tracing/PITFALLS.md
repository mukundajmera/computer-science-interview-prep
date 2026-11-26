# Common Pitfalls

- **Ignoring Application Overhead:** Assuming apps can just send HTTP requests to a central collector for every span. This will block application threads and cause cascading failures. Local sidecars or UDP agents are necessary.
- **Misunderstanding Tail-Based Sampling:** Thinking tail-based sampling can be done immutably row-by-row. It requires buffering all spans for a given `trace_id` for a window of time before making a keep/drop decision.
- **Elasticsearch Defaulting:** While ES is popular (e.g., Jaeger initially), for massive scale tracing, columnar databases (ClickHouse) are far superior due to high cardinality tags and write-heavy workloads.
- **Forgetting Clock Skew:** Assuming timestamps from different servers are perfectly aligned when assembling the DAG.
