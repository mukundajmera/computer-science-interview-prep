# Comparison: ID Generation Strategies

## 1. Generation Methodologies

| Strategy | Pros | Cons | Use Case |
| :--- | :--- | :--- | :--- |
| **Multi-Master Database Auto-Increment** | Simple, relies on existing infrastructure. | Write bottleneck on central DB, single point of failure, complex to scale horizontally. | Small to medium scale apps with low write rates. |
| **UUIDv4 (Random)** | Zero coordination, scales infinitely, decentralized. | 128-bit size is large. Not time-ordered, leading to massive index fragmentation in relational databases. | Non-indexed unique tokens, session IDs. |
| **UUIDv7 (Time-ordered)** | Decentralized, time-ordered, solves index fragmentation. | 128-bit size violates strict 64-bit `BIGINT` constraints. | Systems where 128-bit IDs are acceptable. |
| **Snowflake (Custom 64-bit)** | Decentralized, strict 64-bit size, time-ordered. | Requires clock drift handling and external worker coordination (e.g., ZooKeeper). | High-scale distributed databases, social networks. |
