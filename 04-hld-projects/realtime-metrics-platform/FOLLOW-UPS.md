# Real-Time Metrics Platform — Follow-Ups

1. How do you guarantee alert correctness during replay/backfill?
2. What does 10x ingest do to partitioning and query fan-out?
3. How do you isolate noisy tenants without global impact?
4. What are your late-data and out-of-order handling bounds?
5. How do you migrate from baseline metrics monitoring to this design safely?

## Top-K Variant Follow-Ups
1. How would you maintain exact Top-K under high skew without exploding memory?
2. When would you switch to approximate heavy-hitter algorithms, and what error bounds are acceptable?
3. How do watermark policies change ranking stability for a YouTube-like trending surface?
