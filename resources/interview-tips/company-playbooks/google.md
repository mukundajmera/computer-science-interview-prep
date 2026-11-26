# Google Playbook: Public Context and Sources

## Purpose and caveats

This playbook outlines public architecture context and topics commonly associated with Google L5/L6 software engineering interviews. Any discussion of specific company levels, titles (e.g., L5, L6), and leveling rubrics serves as non-official preparation context unless explicitly supported by an official public source. All unverified capacity, latency, accuracy, compression, and vendor-scale figures should be treated as hypothetical scenario assumptions, not as verified facts.

## Public architecture/interview context

Google interviews frequently assess an engineer's ability to operate efficiently at immense scale. The technical focus spans high-level system design and low-level algorithmic clean code. The following foundational topics reflect the scope typically examined:

- **Planetary-scale design reasoning:** Designing systems that function globally with robust multi-region deployment strategies. Discussions often revolve around how to handle cross-region data replication, minimize latency for global users, achieve Exabyte-scale storage, and ensure high availability (e.g., 99.999% uptime guarantees) despite inevitable hardware or network failures. Traffic spikes require elastic scaling strategies and graceful degradation.

- **Algorithmic clean code:** Interviewees are expected to write code that is production-ready, well-structured, testable, and robust against edge cases. This involves analyzing and optimizing both time and space complexity, using standard library constructs effectively, and avoiding unnecessary complexity.

- **Spanner:** Google's globally distributed, synchronously replicated database. Spanner represents the concept of global strong consistency combined with high availability and relational semantics (SQL), heavily leveraging TrueTime to order transactions globally.

- **Borg:** A large-scale cluster management system that manages the scheduling and execution of jobs across thousands of machines. Borg (which heavily influenced Kubernetes) isolates application logic from underlying hardware infrastructure and emphasizes resource allocation, failure recovery, and isolation.

- **MapReduce (Historical/Uncertain):** A pioneering model for large-scale distributed data processing involving a `Map` phase to filter/sort data and a `Reduce` phase to aggregate it. While extremely influential in the evolution of big data (e.g., logs analysis and index generation), its direct operational use in modern Google systems may be historically bounded or superseded by modern stream and batch processing frameworks like FlumeJava or Dataflow. Its performance and scale numbers are considered assumptions rather than current guarantees.

- **API design clarity:** High emphasis on clean, versioned APIs. This includes understanding the trade-offs between resource-oriented REST and strictly-typed gRPC, implementing idempotency for safe retries on mutating requests (using idempotency keys), handling pagination (e.g., cursor-based) to manage memory load, and maintaining backwards compatibility.

- **Common system-design scenarios:** Candidates may be asked to reason through large-scale design problems such as:
  - Designing a massive file storage and collaboration system (e.g., Google Drive equivalents).
  - Building a global counter system for tracking high-frequency events (e.g., video views).
  - Creating mapping and routing services requiring geospatial indexing.
  - Designing distributed rate limiters handling high-throughput distributed state.

## Sources consulted

- **Spanner: Google’s Globally-Distributed Database**
  - URL: https://research.google/pubs/pub39966/
  - Publication Date: 2012
  - Access Date: 2023-10-23
  - Context: Describes the design and capabilities of Spanner, including its use of TrueTime for global consistency.

- **Large-scale cluster management at Google with Borg**
  - URL: https://research.google/pubs/pub43438/
  - Publication Date: 2015
  - Access Date: 2023-10-23
  - Context: Details the architecture of Borg, Google's cluster manager that runs hundreds of thousands of jobs across thousands of machines.

- **MapReduce: Simplified Data Processing on Large Clusters**
  - URL: https://research.google/pubs/pub62/
  - Publication Date: 2004
  - Access Date: 2023-10-23
  - Context: Outlines the MapReduce programming model for processing massive datasets, though its active use at scale today is treated as a historical foundation for modern equivalents.
## Candidate preparation

*Candidate Disclaimer: The following guidance is based on anecdotal candidate reports and public study frameworks. It is not an official Google scorecard or rubric, and it does not guarantee hiring outcomes. It serves strictly as level-aware preparation context.*

Preparation for Google's systems design interviews requires candidates to move beyond standard component memorization and instead focus on rigorous, level-aware design reasoning. 
- **L4 Candidates:** Should focus on providing an intuitive, functional minimum viable product (MVP). The core API must make sense, the data model should satisfy basic queries, and common bottlenecks must be identified.
- **L5 Candidates:** Are expected to heavily weigh trade-offs and drive technical decisions. You should be able to contrast different storage systems, evaluate synchronous versus asynchronous processing, and discuss CAP theorem implications in the context of the specific scenario.
- **L6/L7 Candidates:** Must drive the conversation entirely, preemptively identifying hidden bottlenecks, multi-tenant failure domains, and complex distributed system edge cases. An L6/L7 candidate should optionally provide a failure trace with assumptions, proving that the system can gracefully degrade during catastrophic events (e.g., regional network partitions).

## Practice scenario

**Scenario:** Design a globally available document-indexing or metadata service (e.g., for Google Drive). Make scale, API, consistency, and failure trade-offs explicit.

**Requirements & Constraints (Hypothetical Assumptions):**
- **Scale:** The system must handle 100 billion documents, with a steady ingestion rate of 100,000 updates per second globally. Read queries are 1,000,000 QPS globally. 
- **Latency:** Read latency must remain under 50ms at the P99 percentile. Ingestion processing can be asynchronous but must be visible within a 5-second window (eventual consistency SLA).
- **Availability:** Ensure 99.99% uptime. 
- **Payload:** Each document metadata payload is approximately 2KB. The total storage requirement is around 200TB, before accounting for replication.

**Design Trade-offs:**
1. **Consistency vs. Availability (Storage Layer):** 
   - *Trade-off:* We could use a strongly consistent distributed SQL database (like Spanner) or an eventually consistent NoSQL store (like Cassandra/Bigtable). 
   - *Resolution:* Given the requirement for low read latency (50ms P99) and a loose 5-second ingestion SLA, an eventually consistent NoSQL approach with cross-region asynchronous replication is preferable for the read path. This approach trades immediate strong consistency across regions for higher availability and lower read latency.
2. **Storage Layout (Row vs. Column):**
   - *Trade-off:* A row-oriented database provides fast single-document lookups, while a column-oriented database is optimized for analytical aggregations.
   - *Resolution:* Since this is a metadata/indexing service where primary access is likely single-document retrieval or filtering by specific attributes, a wide-column store (like Bigtable) is appropriate. It scales horizontally well and supports fast prefix scans.
3. **Synchronous vs. Asynchronous Ingestion:**
   - *Trade-off:* Blocking the client until the document is fully indexed ensures the client knows the system state but risks high latency and cascading failures during traffic spikes. Asynchronous ingestion using a message broker (e.g., Pub/Sub) decouples the client but requires handling retry logic and dead-letter queues.
   - *Resolution:* Implement asynchronous ingestion via a distributed queue. The API immediately returns an HTTP 202 (Accepted) response with an idempotency/tracking ID. Background workers process the queue and update the indexing storage.

**Failure/Edge Case Resolution:**
- *Failure Case:* A massive, sudden region-wide network partition severs connectivity to the primary metadata database cluster in US-East.
- *Defensible Resolution (Graceful Degradation):* The global load balancer automatically reroutes traffic to US-West and EU-West. The system continues to operate in a degraded state: reads may serve slightly stale data (violating the 5-second ingestion visibility SLA, but preserving system availability), while writes are temporarily buffered in regional multi-tenant message queues (e.g., Pub/Sub) until connectivity to the primary cluster is fully restored.

## Self-review rubric

*Rubric Disclaimer: This is an anecdotal, candidate-created self-assessment matrix for practice purposes. It is not an official company scorecard and does not guarantee any hiring outcomes.*

| Dimension | Needs Improvement | Meets Expectations | Concrete Evidence / Examples |
| :--- | :--- | :--- | :--- |
| **Requirements Gathering** | Jumps straight to architecture; misses explicit scale constraints. | Explicitly states assumptions (QPS, storage, latency SLAs) and bounds the problem. | "Assuming 100K writes/sec at 2KB each, network bandwidth is 200MB/s, fitting well within commodity link limits." |
| **System Architecture** | Draws a generic "Client -> Load Balancer -> DB" diagram without domain context. | Divides the system into clear read/write paths and isolates components by scalability needs. | Separates the ingestion pipeline (API, Queue, Workers) from the read path (Cache, Read Replicas). |
| **Trade-off Articulation** | Chooses a database "because it's fast" or "because it scales." | Compares at least two viable alternatives and justifies the choice based on scenario constraints. | "I chose Cassandra over Postgres because the 1M QPS read load requires horizontal scaling that exceeds a single primary's capacity." |
| **Failure Handling** | Assumes the "happy path"; ignores component failures or network partitions. | Identifies specific single points of failure and describes degraded operation or failover mechanisms. | "If the Redis cluster partitions, the read path falls back to the database, shedding load for non-critical background jobs to protect DB availability." |
| **Data Modeling** | Designs a monolithic table without partitioning strategy. | Chooses appropriate partition and sort keys for the distributed store to avoid hot spots. | "I will use a hash of the tenant ID as the partition key to evenly distribute the 100K writes/sec across Cassandra nodes." |

## Sample answer outline

### Scenario Response: Globally Available Document-Indexing Service
**1. Scope and Numbers:**
- State the core assumptions: 100 billion documents, 100K write QPS, 1M read QPS.
- Storage capacity: 100B * 2KB = 200TB base storage. With replication (3x), ~600TB total.
- Network bandwidth: 1M QPS * 2KB = 2GB/sec read bandwidth globally.

**2. High-Level API:**
- `PUT /v1/documents/{doc_id}/metadata` (Requires an idempotency key to handle retries safely)
- `GET /v1/documents/{doc_id}/metadata`

**3. Architecture & Data Flow:**
- **Write Path:** Client -> Global API Gateway -> Message Broker (Pub/Sub) -> Ingestion Workers -> Distributed NoSQL Store (Bigtable/Cassandra).
- **Read Path:** Client -> Global API Gateway -> Distributed Cache (Memcached/Redis) -> NoSQL Store.

**4. Deep Dive & Trade-offs:**
- *Data Model:* Use a partition key based on `doc_id` or a hashed tenant ID to ensure even data distribution and avoid hot partitions.
- *Consistency:* Explain the choice of eventual consistency for global reads. Read-after-write consistency can be maintained for the writer by caching their write locally or routing them to the same region.
- *Scale:* Explain how adding worker nodes scales the write path, while adding read replicas or cache nodes independently scales the read path.

**5. Failure Scenarios:**
- Discuss what happens if a downstream indexer crashes (the message remains unacknowledged and is safely picked up by another worker).
- Address hot-key issues (e.g., a viral document causing a massive read spike) by implementing local L1 caching in the API tier.

### Technical/Behavioral Follow-up
**Follow-up Question:** *How would your system handle a sudden 100x spike in ingestion requests from a single misconfigured enterprise tenant, and how do you ensure other tenants aren't starved?*

**Response Outline:**
- **Identify the Risk:** A 100x spike (10M writes/sec) will overwhelm the message broker or the ingestion workers, leading to queue backup and starvation (the noisy neighbor problem) for other tenants on the platform.
- **Immediate Mitigation (Rate Limiting):** Implement a distributed rate limiter at the API Gateway using a Token Bucket algorithm, keyed by tenant ID. This immediately sheds the excess load, returning a `429 Too Many Requests` response.
- **Architectural Isolation (Trade-off):** We could physically isolate the tenant into a dedicated queue, but that increases operational overhead. Instead, we use logical isolation: the API Gateway routes traffic into "high-throughput" and "standard" queues based on historical tenant behavior profiles. 
- **Graceful Degradation:** If the rate limiter fails or allows traffic through, the ingestion workers should employ backpressure, or the queue should support priority load shedding. This ensures that the SLA for standard tenants is preserved even if the misconfigured tenant experiences severe indexing delays. This explicit prioritization is key to ensuring noisy neighbors do not compromise the overall service.
