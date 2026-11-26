# Scoring Rubric: Distributed Partitioned Commit Log Broker

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) |
|---|---|---|---|
| Requirements handling | Vague understanding of pub/sub. | Mentions throughput and partitions. | Quantifies ingress and fan-out limits explicitly. |
| Architecture clarity | Draws a single queue box. | Draws brokers, topics, and consumers. | Details partitions, leaders, followers, and metadata controller. |
| Technical depth | Mentions "save to disk". | Explains append-only logs. | Details Page Cache, Zero-Copy, ISR, and sparse indexing. |
| Trade-off quality | Ignores network bottlenecks. | Acknowledges replication overhead. | Compares pull vs push and ISR vs Quorum consensus. |
| Communication | Jumps around randomly. | Covers all components. | Structured, concise, and focused on core log mechanics. |
