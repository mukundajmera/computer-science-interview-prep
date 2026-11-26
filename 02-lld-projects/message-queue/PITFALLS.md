# In-Memory Message Queue - Common Pitfalls

## Pitfalls
- **Shared Unpartitioned Queue Bottleneck**: Using a single global lock for the whole queue severely limits throughput.
  - *Mitigation*: Use per-partition locks.
- **Blocking All Consumers on a Single Slow Consumer**: If consumers share a single thread or pool without isolation.
  - *Mitigation*: Consumers should poll independently.
- **Circular Dependency Deadlocks**: If the subscriber DAG has cycles.
  - *Mitigation*: Validate the DAG for cycles using topological sort on creation.
- **Missing DLQ for Poison Pills**: A bad message causes infinite retries, halting the partition.
  - *Mitigation*: Implement a max-retry limit and a DLQ.
