# Interview Questions: Cassandra

## Basic Questions

### 1. Why Cassandra?
**Q**: When is Cassandra a strong choice?
**A**: For large write-heavy, highly available systems with key-based access patterns and horizontal scale requirements.

### 2. Partition key vs clustering key
**Q**: Explain the difference.
**A**: Partition key decides distribution across nodes; clustering key orders rows inside each partition.

## Intermediate Questions

### 3. Consistency levels
**Q**: How do you use ONE, QUORUM, ALL?
**A**: Pick per operation based on correctness risk and latency budget rather than one global setting.

### 4. Data modeling approach
**Q**: How do you model Cassandra tables?
**A**: Start from query patterns and design primary keys around those reads/writes to avoid expensive scans.

## Advanced Questions

### 5. Hot partition handling
**Q**: One partition is overloaded. What now?
**A**: Revisit partition key strategy, introduce bucketing where valid, and rebalance traffic using controlled migration.

### 6. Failure behavior under node loss
**Q**: How does Cassandra stay available?
**A**: Replica-based design with coordinator routing keeps service alive if consistency requirements can still be met.

## Common follow-ups
- How do you tune replication factor per region?
- What workload indicates compaction pressure?
- How do you test consistency behavior in failure drills?

## Red flags to avoid
- Relational thinking first, query model second.
- No partition-size guardrails.
- Hand-waving consistency choices.

## 30-second explanation
"Cassandra is a distributed wide-column database built for high write throughput and availability. I model data around query patterns using partition and clustering keys, then choose consistency levels per operation based on business risk and latency targets."
