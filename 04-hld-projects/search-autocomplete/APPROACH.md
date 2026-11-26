# Search Autocomplete - Approach

## 1. System Overview
The system involves a read-heavy path for serving autocomplete suggestions and a write-heavy path for logging query analytics. A batch pipeline periodically aggregates data to build a new Trie snapshot for fast lookups.

## 2. Core Trade-offs
### 2.1. Real-time Trie Updates vs. Offline Batch Aggregation
**Approach:** Offline Batch Aggregation
- **Why:** Updating Trie nodes synchronously on every keystroke introduces lock contention and cache thrashing. The design employs an append-only analytics log + weekly/hourly aggregation job (MapReduce/Spark) to build immutable Trie snapshots loaded into memory.

### 2.2. On-the-fly Traversal vs. Node-level Top-k Caching
**Approach:** Node-level Top-k Caching
- **Why:** Standard Trie traversal takes O(p + m log k) (p=prefix length, m=nodes in subtree). Storing pre-sorted top-5 queries at each Trie node reduces lookup to O(p) = O(1) (since prefix length is capped at 50 chars).

## 3. Storage Strategy
- **Analytics Log:** Append-only distributed log (e.g., Kafka or raw logs to object storage).
- **Aggregated Data:** SQL or NoSQL database to store query frequencies.
- **Trie Store/Cache:** In-memory key-value store (e.g., Redis) or specialized Trie server to hold the compiled Trie with node-level top-k cache.
