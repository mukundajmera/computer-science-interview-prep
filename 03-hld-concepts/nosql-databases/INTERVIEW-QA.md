# NoSQL Databases — Interview Q&A

## 1) When would you choose NoSQL over SQL?

Choose NoSQL for high-scale distributed workloads where horizontal scalability, flexible schema, and partition-tolerant designs are more important than rich relational querying.

## 2) How does data modeling differ from relational systems?

NoSQL models are query/access-pattern first. You often denormalize data and design around partition keys to avoid expensive cross-partition operations.

## 3) What is tunable consistency?

Some NoSQL systems allow per-request consistency choices (for example, stronger reads for critical paths and eventual reads for lower-latency/cost paths).

## 4) What causes hot partitions and how do you avoid them?

Skewed partition keys funnel disproportionate traffic to a subset of nodes. Mitigations include better key design, bucketing, and adaptive routing.

## 5) What are common interview trade-offs?

- Consistency vs availability/latency
- Denormalization speed vs update complexity
- Managed service simplicity vs vendor coupling

## Deep Dives

- [Cassandra Interview Q&A](../cassandra/INTERVIEW-QA.md)
- [DynamoDB Interview Q&A](../dynamodb/INTERVIEW-QA.md)
