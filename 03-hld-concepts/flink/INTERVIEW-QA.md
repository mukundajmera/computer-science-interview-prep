# Interview Questions: Flink

## Basic Questions

### 1. Why choose Flink over Spark batch jobs?
**A**: Choose Flink when low-latency continuous processing and stateful event-time correctness are core requirements.

### 2. What is Flink state?
**A**: Operator-managed data (keyed/window/session) used to produce results across events rather than per-event stateless logic.

### 3. What is a watermark?
**A**: A progress signal for event time that helps the system decide when windows are ready to emit.

## Intermediate Questions

### 4. Event time vs processing time?
**A**: Event time is resilient to out-of-order arrivals and gives more accurate results; processing time is simpler but can skew correctness under delay.

### 5. How do you handle late events?
**A**: Set allowed lateness, define update/retraction strategy, and route very-late events to a side output for audit/backfill.

### 6. How does checkpointing improve reliability?
**A**: It captures consistent state snapshots so failures can resume from the latest checkpoint with replay.

## Advanced Questions

### 7. What does exactly-once mean in stream design?
**A**: State updates and sink outputs are committed consistently once, typically using checkpoint-coordinated sink transactions.

### 8. How do you control backpressure?
**A**: Scale bottleneck operators, tune parallelism/buffers, optimize serialization, and isolate expensive sinks.

### 9. When should you avoid Flink entirely?
**A**: If business SLAs accept batch latency or team operational maturity is low, use simpler batch/event-driven pipelines.

## Common Follow-ups

- How do you select checkpoint interval?
- What do you monitor to detect state growth risk?
- How do you backfill historical events safely?

## Red Flags to Avoid

- Choosing Flink without a real-time requirement.
- Ignoring watermark/late-data policy.
- Claiming exactly-once without sink semantics discussion.

## 30-second Explanation

"Flink is a stateful stream engine for low-latency event-time processing. In interviews, I focus on windowing, watermarks, checkpointing, and operational trade-offs against simpler batch alternatives."
