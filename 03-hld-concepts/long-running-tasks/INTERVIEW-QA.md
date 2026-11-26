# Interview Questions: Long-Running Tasks

## Basic

### 1. Why move heavy work out of request/response?
**A:** To keep user-facing latency low and avoid request timeout failures.

### 2. What is the minimal async job architecture?
**A:** API enqueue + durable queue + worker pool + job status store.

### 3. Why return a job ID?
**A:** It gives clients a stable handle to poll or subscribe for completion state.

### 4. What does at-least-once processing imply?
**A:** Duplicate execution can happen, so handlers must be idempotent.

## Intermediate

### 5. How do you handle repeated failures?
**A:** Exponential backoff retries with cap, then route to DLQ for investigation.

### 6. How do you prevent duplicate submissions?
**A:** Idempotency keys on submit + lookup of existing job before enqueue.

### 7. What is backpressure in this context?
**A:** Controlled admission when queue depth/lag exceeds thresholds; reject/defer low-priority work.

### 8. Why split workloads into separate queues?
**A:** To avoid long jobs blocking short jobs and to tune resources by job class.

## Advanced

### 9. How do you avoid DB-write/queue-publish inconsistency?
**A:** Use transactional outbox + CDC or equivalent durable publication pattern.

### 10. What metrics define system health?
**A:** Queue depth, oldest message age, success/failure rate, retries, DLQ inflow, processing latency.

### 11. When should you adopt orchestration?
**A:** When workflows have branching, compensations, or strict step-level observability/retry control.

### 12. Strong trade-off statement?
**A:** "I accept eventual completion for heavy tasks to protect API latency, and compensate with durable job state, retries, and explicit failure paths."
