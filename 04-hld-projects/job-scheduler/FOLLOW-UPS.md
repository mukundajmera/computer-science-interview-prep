# Job Scheduler — Follow-Up Questions

1. How do you support DAG-style workflow dependencies without blocking the main scheduler loop?
2. What changes when 30% of jobs are long-running and can overlap the next schedule window?
3. How do you guarantee fair scheduling across tenants with different SLA tiers?
4. How would you migrate from single-region to active-active while preserving run uniqueness?
5. Which metrics and alerts would detect stuck queues, retry storms, and lease churn first?

## Variant bridge
- Baseline interview answer: local region scheduler + durable queue.
- Advanced extension: workflow engine + cross-region lease coordination.
