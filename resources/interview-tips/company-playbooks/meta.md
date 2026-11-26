# Meta Playbook: Public Context and Sources

## Purpose and caveats

This playbook is an unofficial preparation guide for Meta candidate interviews. It is based entirely on public engineering blogs, conference talks, and published system architectures.

**Caveat:** Any company level, title (e.g., E5/E6), or rubric mentioned here is purely non-official preparation context and does not represent an official Meta hiring scorecard or policy. Do not use this section as a definitive guide for hiring guarantees.

## Public architecture/interview context

### Bottom-up engineering
*Caveat: This cultural aspect is based on historical external observation and anecdotal candidate reports, rather than a specific documented engineering blog post in our sources.*
Meta's engineering culture has historically emphasized a "bottom-up" approach, where engineers are encouraged to identify problems, propose solutions, and drive execution. For senior engineering levels (like E5/E6—note these are non-official preparation context titles), demonstrating a proactive mindset is often considered critical.

### TAO cache architecture
TAO (The Associations and Objects) is Meta's distributed data store designed for the social graph. It is optimized for read-heavy workloads, modeling data as objects and associations. In system design discussions, referencing TAO demonstrates an understanding of how to manage massive, read-optimized social graphs, handle cache invalidation, and ensure eventual consistency across geographical regions. Supported by the public source: *TAO: The power of the graph*.

### Thrift RPC
Meta heavily relies on Thrift, a cross-language remote procedure call (RPC) framework. Thrift provides efficient serialization and strongly typed APIs. Understanding Thrift in microservices design shows awareness of low-latency communication, efficient request batching, and cross-language interoperability at scale. *Status: Thrift is historically fundamental, but specific internal usage patterns may evolve over time and its ubiquitous standalone status could be uncertain/historical compared to modern gRPC usage outside Meta.*

### RocksDB and Memcached
- **RocksDB:** Meta uses RocksDB extensively as an embeddable, persistent key-value store optimized for fast storage (like SSDs). Systems like ZippyDB use RocksDB as their underlying storage engine. It is highly relevant for write-heavy workloads. *Current Status: Verified as active based on public ZippyDB sources.*
- **Memcached:** Meta operates massive Memcached deployments to reduce database load. Understanding Memcached scaling techniques, such as handling thundering herds with leases and managing regional pools, is frequently applicable in design discussions. *Status: Memcached is a historical foundational piece of Meta's scaling story. While still widely used historically, its exact current widespread architectural dominance may be uncertain/historical.*

### Rapid delivery vs. reliability trade-offs
*Caveat: This trade-off philosophy is based on general industry understanding of Meta's historical "move fast" motto, not explicitly sourced from the architecture documents below.*
Meta’s culture historically valued rapid delivery. However, at senior engineering levels (unofficially E5/E6 as non-official preparation context), this translates to making deliberate, calculated trade-offs between speed and reliability. System designs should reflect an understanding of when to incur technical debt for rapid iteration and how to architect systems so that this debt can be paid down before impacting scalability.

## Sources consulted

1. **TAO: The power of the graph**
   - URL: https://engineering.fb.com/2013/06/25/core-infra/tao-the-power-of-the-graph/
   - Publication Date: June 25, 2013
   - Access Date: October 2023
   - Notes: Details the TAO cache architecture, graph modeling, and eventual consistency choices.

2. **How we built a general purpose key value store for Facebook with ZippyDB**
   - URL: https://engineering.fb.com/2021/08/06/core-infra/zippydb/
   - Publication Date: August 6, 2021
   - Access Date: October 2023
   - Notes: Confirms the current, widespread use of RocksDB as the underlying storage engine for ZippyDB and details consistency features.

3. **ZGateway: Learnings from Putting a Proxy in Front of ZippyDB**
   - URL: https://engineering.fb.com/2023/09/03/core-infra/zgateway-proxy-zippydb-meta/
   - Publication Date: September 3, 2023
   - Access Date: October 2023
   - Notes: Discusses Thrift RPC overhead, batching optimizations, and architectural evolution at Meta.

4. **Scaling Memcache at Facebook**
   - URL: https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf
   - Publication Date: 2013
   - Access Date: October 2023
   - Notes: Details the historical scaling of Memcached across Facebook's infrastructure.


## Candidate preparation
*Caveat: The following preparation advice is based on general industry observation of Meta's engineering culture and unofficial candidate experiences. It does not guarantee success or reflect official Meta hiring policies.*

Preparing for Meta systems design and behavioral interviews generally requires focusing on massive scale, bottom-up problem solving, and moving fast while making deliberate reliability trade-offs. Candidates should be comfortable modeling graph data (similar to TAO), using embedding key-value stores (like RocksDB via ZippyDB context), and optimizing for high read-heavy workloads using caching strategies (e.g., Memcached).

## Practice scenario
**Scenario:** Design a distributed rate limiter for Meta's Graph API.

*Stated requirements/constraints:*
- The rate limiter must enforce limits at a per-user, per-endpoint granularity across global data centers.
- The system handles 100M+ requests per second globally.
- Low latency is critical; rate limit checks must complete in under 5ms on average to not significantly slow down API responses.
- Eventual consistency across regions is acceptable, provided limits are strictly enforced eventually (e.g., within seconds).

*Design trade-offs:*
1. **Algorithm Choice (Token Bucket vs. Sliding Window Log):** A Token Bucket is memory efficient and fast but allows bursts of traffic, whereas a Sliding Window Log provides precise control but consumes significant memory and compute per request. *Resolution:* Token Bucket is chosen for extreme scale and low memory footprint, aligning with Meta's high throughput needs.
2. **Storage Engine (Redis vs. Memcached vs. Local Memory):** Storing counts centrally in Redis provides accuracy but introduces network hops. Local memory within API gateways is incredibly fast but leads to fragmented counts. *Resolution:* A hybrid approach using local memory for rapid checks backed by asynchronous batch updates to a distributed cache (like Memcached or Redis) balances speed and accuracy.
3. **Consistency vs. Latency:** Synchronous cross-region replication ensures strict limits but causes unacceptable latency for global users. *Resolution:* Eventual consistency using async replication ensures low latency at the cost of allowing slight, temporary overages during spikes.

*Failure/edge case:* 
- **Thundering Herd after a Regional Failover:** If a datacenter goes offline, all traffic shifts to a secondary datacenter, causing the local rate limiter cache to experience a massive influx of un-cached users, potentially overwhelming the backing datastore.
- **Defensible resolution:** Implement probabilistic early expiration and request jittering (request coalescing) on the cache layer. Introduce a circuit breaker to default to "allow" if the underlying cache/datastore fails to respond within 5ms to prevent bringing down the entire API for rate limiting reasons.

## Self-review rubric
*Caveat: This rubric is candidate-created guidance for self-evaluation during mock interviews. It is absolutely not an official Meta scorecard, rubric, or leveling guide.*

| Dimension | Performance Signal (What to aim for) | Concrete Evidence/Examples |
| :--- | :--- | :--- |
| **Problem Scoping** | Proactively identifies system constraints and clarifications without prompting. | Candidate asks about read/write ratio, acceptable latency, and cross-region replication needs before designing. |
| **Architecture Choice** | Selects scalable datastores and caching layers with sound reasoning. | Chooses RocksDB for write-heavy persistent storage and justifies Memcached for read-heavy caching, citing specific Meta architecture (e.g., TAO). |
| **Trade-off Analysis** | Clearly articulates what is being sacrificed for what benefit. | "I'm choosing eventual consistency here to prioritize the 5ms latency requirement, which might lead to brief stale reads." |
| **Edge Case Handling** | Anticipates failures at scale and proposes concrete mitigations. | Identifies cache stampede risks and proposes lease-based caching or probabilistic early expiration to mitigate. |

## Sample answer outlines

### Outline 1: Design Scenario (Distributed Rate Limiter)
- **Clarification:** Acknowledge requirements (100M+ QPS, <5ms latency). Ask if we need strict enforcement or if slight overages are acceptable (assume eventual consistency is okay).
- **High-level Design:** API Gateway routes requests to a Rate Limiter service. The service checks local memory cache first, then falls back to a distributed cache (e.g., Redis or Memcached).
- **Deep Dive (Data Model & Algorithm):** Use Token Bucket. Store buckets as hashes: `User_ID: {Tokens_Remaining: int, Last_Refill_Time: timestamp}`. 
- **Trade-off Discussion:** Discuss the trade-off between using a centralized Redis cluster (accurate but slower) vs. local gateway caching + async sync (fast but allows over-limit bursts). Decide on local caching with async sync to prioritize the <5ms latency requirement.
- **Bottlenecks & Edge Cases:** Address the "hot key" problem if a single user sends millions of requests. Mitigate by sharding the rate limit counters or implementing local load balancer drop logic for abusive IPs before they hit the main rate limiter.

### Outline 2: Behavioral Follow-up (Navigating a Disagreement on Tech Debt)
*Prompt: Tell me about a time you had to push back on a fast delivery to address tech debt.*
- **Context:** While working on a critical microservice, the team was pushed to launch a feature in two weeks. However, the existing legacy database schema was causing frequent deadlocks under load.
- **Action:** I analyzed the trade-off: launching fast would meet the deadline but risk cascading failures at peak hours. I gathered latency metrics and deadlock logs to quantify the risk. I proposed a phased rollout, separating the schema migration (1 week) from the feature launch (1 week), pushing the deadline by a few days but ensuring stability.
- **Reasoning:** I prioritized reliability over pure speed because the cost of a major outage outweighed the benefit of an early launch. It demonstrated a calculated trade-off (delaying the launch) for long-term scalability.
- **Result:** The team agreed. We migrated the schema without downtime, and the subsequent launch handled a 3x traffic spike without any deadlocks.
