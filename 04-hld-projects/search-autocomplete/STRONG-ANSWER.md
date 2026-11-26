# Search Autocomplete - Strong Answer

A strong candidate drives the interview by clearly separating the high-frequency, latency-sensitive read path from the heavy, offline write path.

## Requirements & Estimation
They immediately identify the 100ms P99 latency constraint as the primary driver. They correctly estimate 48,000 peak QPS and recognize that while storage is manageable (~27GB for the Trie), keeping it in memory is crucial for speed.

**Say:** "With 10M DAU averaging 10 searches a day at 4 keystrokes each, we're looking at about 48,000 peak QPS. To maintain our <100ms latency SLA at this throughput, we must serve suggestions strictly from memory."

## Core Design (Data Structures)
They explain the Trie data structure and its time complexity O(p + m log k). They proactively optimize this by proposing **node-level caching**—storing the top 5 suggestions inside each Trie node. This reduces lookup time to O(p), effectively O(1) since prefix length is bounded.

**Say:** "A standard Trie traversal of O(p + m log k) is too slow. I'll optimize this to O(p) by pre-computing and caching the top-5 suggestions directly within each Trie node."

## Architecture
They propose an architecture where:
1. **Reads:** Hit a Load Balancer -> API Gateway -> Distributed Cache (Redis) -> Trie Service.
2. **Writes:** Keystrokes/searches are asynchronously logged via Kafka.
3. **Batch Job:** A nightly or weekly Spark job processes raw logs, aggregates frequencies, filters profanity, and builds a brand new Trie.
4. **Deployment:** The new Trie is swapped into memory using a Blue-Green deployment strategy to ensure zero downtime.

**Say:** "We need to completely decouple the read and write paths. I'll use a fast, synchronous read path querying the cached Trie, and a decoupled, asynchronous write path using Kafka and Spark to rebuild the Trie offline."

## Optimizations & Trade-offs
A strong answer doesn't stop at the backend. They discuss:
- **Client-side debouncing:** Don't send a request on every keystroke; wait 50ms.
- **Browser caching:** Save previous prefix results locally to avoid redundant API calls when the user hits backspace.
- **Sampling:** Not every single search needs to be logged for analytics; sampling 1 in 10 requests is sufficient for statistical popularity.
- **Sharding:** If the Trie exceeds memory, they propose prefix-based sharding (e.g., 'a-m' on server 1, 'n-z' on server 2) and handle hot spots by dynamically splitting shards.

**Say:** "Since the overall system throughput is so high, we should implement client-side debouncing of 50ms and sample our analytics at 10% to save bandwidth and compute costs."
