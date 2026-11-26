# Video Recommendations — Design

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: A large-scale video recommendation engine delivering personalized content (e.g., a "Home Feed" or "Up Next" feed).
- Core user value: Keep users engaged by serving highly relevant, high-quality video content tailored to their implicit and explicit preferences, while also supporting creator discovery and platform health.

### Functional Requirements
- [x] FR1: Produce personalized "up-next" or feed video recommendations for active user sessions based on historical data.
- [x] FR2: Rank candidate videos using a combination of expected engagement signals (clicks, watch time) and value signals (likes, shares).
- [x] FR3: Support context-aware personalization (device, location, time of day) and ensure freshness of content.
- [x] FR4: Capture real-time user interaction feedback (implicit and explicit) to continuously update feature stores and improve model performance.
- [x] FR5: Ensure a robust diversity mechanism so users don't see repetitive content from the same creator or strictly one topic.
- [x] FR6: System must provide endpoints for querying model metadata and health.
- [x] FR7: System should have a fallback strategy when personalized recommendation engines fail.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% core serving |
| Read latency | p95 < 50ms tail latency SLA |
| Write latency | < 1-2 seconds for stream processing feedback ingestion |
| Throughput | 231,000 avg QPS; 700,000 peak QPS |
| Consistency | Eventual consistency for feedback loops; strong consistency for account management |
| Durability | High durability for user historical watch history and models |
| Scalability | Must scale gracefully under viral traffic bursts |
| Fault Tolerance | Degrades gracefully rather than outright failing |

### Constraints
- Regulatory/compliance: Must comply with GDPR/CCPA for user data deletion, right to be forgotten, and consent for tracking.
- Content constraints: Must filter out unsafe, age-restricted (if applicable), or prohibited content early in the pipeline.
- Catalog scale: The pool of candidate videos exceeds 1 Billion items.
- Engineering Cost Constraints: Inference costs for neural models must be bounded to remain profitable per user session.
- Client Device Constraints: Payloads must be minimal to support low-bandwidth 3G mobile users globally.

### Out of Scope
- Video ingestion, transcoding, encoding, and CDN delivery mechanisms.
- Search query parsing and traditional inverted-index search execution (though search embeddings are used as features).
- User authentication and general account management.
- Monetization and ad injection logic (ads are handled by a separate ad-serving system).

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

*Note: The following traffic metrics are illustrative scenario assumptions, not verified facts.*
Assume 1B DAU and 20 recommendation requests/user/day.

### Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | 1 Billion | scenario assumption input |
| Requests/user/day | 20 | scenario assumption input |
| Daily request attempts | 20 Billion | DAU × requests/user (1B × 20) |
| Daily successful requests | 18 Billion | Assuming 10% blocked (rate limit/bot/invalid) |
| Avg QPS (attempts) | 231,481 | 20B / 86400 seconds |
| Avg QPS (successful) | 208,333 | 18B / 86400 seconds |
| Peak QPS (attempts) | ~700,000 | avg attempts × ~3.02 (burst factor) |
| Peak QPS (successful) | ~630,000 | avg successful × ~3.02 (burst factor) |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| Interaction Events | 200 Bytes | 4 TB (20B * 200B) | ~1.46 PB |
| Feature Embeddings | 1 KB/user | 1 TB (1B users) | - |
| Video Metadata | 2 KB/video | 2 TB (1B videos) | - |

### Decision Notes
- **Which estimate forces a design choice?** With 1 Billion videos in the catalog and a strict tail latency SLA of p95 < 50ms, scoring the entire catalog per request is computationally impossible. We *must* use a Multi-Stage Recommendation Funnel (Candidate Generation -> Light Ranking -> Heavy Ranking -> Policy Reranking).
- **What assumption is most uncertain?** Peak QPS could spike significantly during viral global events, necessitating robust throttling, graceful degradation, and autoscaling.
- **Why is 1-Year storage relevant?** 1.46 PB of uncompressed interaction logs dictates we need a scalable data lake (like S3/GCS with Iceberg/Hudi) rather than traditional relational databases for our offline model training data.
- **Additional Considerations**: To maintain the SLA under 700K peak QPS, caching of both heavy ranker results for common contexts and intermediate feature sets is mandatory, not optional. The multi-stage pipeline is crucial.
- **Network Bandwidth**: Total peak outbound bandwidth must differentiate successful operations from attempts. Successful responses (630,000 QPS × 5 KB = ~3.15 GB/s) deliver full recommendations, whereas blocked attempts (70,000 QPS × 200 bytes = ~14 MB/s) return small error payloads (e.g., 429 Too Many Requests). Total peak bandwidth is ~3.16 GB/s.
- **Vector DB RAM Sizing**: 1 Billion videos * 512 dimensions * 4 bytes (Float32) = ~2 TB of RAM just for raw dense embeddings, necessitating a clustered Vector Database (like distributed Milvus).
- **Total System Cost Estimation**: Keeping all vector embeddings in RAM requires significant compute resources, pushing us toward ANN algorithms (like HNSW) which heavily rely on RAM for performance. We must actively prune low-value items to stay within budget constraints.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: gRPC for internal service-to-service calls (low latency); REST/GraphQL for client-facing API Gateway.
- Auth model: OAuth 2.0 / JWT tokens passed via headers.
- Rate limiting policy: Token bucket per user ID to prevent scraping, coupled with global load shedding during degraded states.

### Core Endpoints

```http
POST /api/v1/recommendations/up-next
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "u_987654321",
  "context": {
    "current_video_id": "v_123456",
    "device_type": "mobile",
    "network": "4g",
    "locale": "en-US",
    "client_timestamp": 1718293847
  },
  "limit": 20
}
```

**Response Example:**
```json
{
  "recommendations": [
    {
      "video_id": "v_789012",
      "title": "Machine Learning in 5 Minutes",
      "thumbnail_url": "https://cdn.example.com/v_789012.jpg",
      "creator_id": "c_456",
      "duration": 300,
      "view_count": 1500000
    },
    {
      "video_id": "v_998877",
      "title": "System Design Explained",
      "thumbnail_url": "https://cdn.example.com/v_998877.jpg",
      "creator_id": "c_123",
      "duration": 1800,
      "view_count": 500000
    }
  ],
  "request_id": "req_abc123"
}
```

```http
POST /api/v1/recommendations/feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "u_987654321",
  "video_id": "v_123456",
  "event_type": "watch_time",
  "dwell_ms": 145000,
  "percentage_completed": 0.85,
  "client_timestamp": 1718293992
}
```

```http
GET /api/v1/recommendations/health
GET /api/v1/recommendations/model-metadata
```

### Error Model
- `400 Bad Request`: Invalid request schema or missing context.
- `401/403 Unauthorized/Forbidden`: Missing or expired JWT / unauthorized.
- `404 Not Found`: User or Video not found context.
- `409 Conflict`: Conflict / concurrent duplicate interactions.
- `429 Too Many Requests`: Rate limit exceeded.
- `500/503 Internal Server Error`: Internal dependency failure (should trigger fallback mechanisms to ensure graceful degradation).

### Concrete Normal Worked Trace
1. **Client Request**: The mobile app issues a `POST /api/v1/recommendations/up-next` call with the user's JWT and `context` containing the currently playing `video_id`.
2. **Gateway & Auth**: The API Gateway validates the JWT, checks the token bucket for the user's IP/ID, and routes the request to the Recommendation Service.
3. **Candidate Generation**: The Recommendation Service fetches the user's embeddings from the Feature Store (Redis) and queries the Vector DB (Milvus) using an ANN search to retrieve 1,000 similar candidate videos based on the user embedding and current context.
4. **Light & Heavy Ranking**: The service applies a lightweight GBDT ranker to filter to 100 items, and then scores those 100 items using a GPU-hosted MMoE Heavy Ranker predicting probabilities for clicks and watch time.
5. **Hydration & Reranking**: The top 20 ranked IDs are hydrated with full metadata (titles, thumbnail URLs) from DynamoDB. The Policy Reranker applies diversity constraints (e.g., max 2 videos per creator).
6. **Response**: The final list is serialized into JSON and returned to the client with a `200 OK`.

### Explicit Consistency/Security Boundary
- **Eventual Consistency**: Real-time user interactions (clicks, skips) are streamed through Kafka and processed by Flink. There is an accepted eventual consistency boundary where features (and thus recommendations) may lag up to 1 minute behind actual user actions during normal load, and gracefully degrade during partitions.
- **Strong Consistency/Security**: Privacy rules, account blocking, and age restrictions form a strict security boundary. The API Gateway and Policy Reranker enforce strong consistency on these policies. A blocked user or deleted video is immediately omitted from responses, overriding any eventual consistency in the recommendation models.

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- **User Profile & History**: Demographics, past 100 video watch history, watch time completion rates, search query embeddings.
- **Video Metadata & Embeddings**: Video ID, duration, category, creator ID, visual/audio dense embeddings, text embeddings (title, description).
- **Interaction Events**: Clicks, watch time, likes, shares, skips, implicit feedback (scrolling past).

### Storage Choices
- **Primary Feature Store**: Feast or Hopsworks. Stores real-time and batch-computed features for both users (User Tower) and items (Item Tower). Reason: Fast low-latency lookups during the ranking phase.
- **Vector Database (Candidate Generation)**: A managed vector database product like Milvus or Pinecone. Reason: Approximate Nearest Neighbor (ANN) algorithms (e.g., HNSW, ScaNN) running within these products search across a 1B item catalog requiring specialized index structures. Note: The ANN algorithm (HNSW/ScaNN) is the mathematical search method, whereas Milvus/Pinecone are the operational database products hosting the algorithm; they are not interchangeable terms.
- **Event Streaming**: Apache Kafka. Reason: Decouples high-throughput user interactions (231K QPS) from the Flink processors updating the Feature Store.
- **Offline Data Lake**: S3 / GCS + Apache Iceberg/Hudi. Reason: Long-term storage of interaction logs for offline model training (Spark/Ray).
- **Metadata DB**: DynamoDB / Cassandra. Reason: Highly available Key-Value lookups for basic video metadata (Title, Thumbnail URL) right before returning the final response.

### Key Access Patterns
1. **Read path query**: Lookup user embeddings from Feature Store, query Vector DB for top 1k candidates, fetch item features for top 1k, run through models, hydrate metadata.
2. **Write path mutation**: Process user click/watch stream, update in-session real-time features.
3. **Secondary lookup**: Retrieve specific video metadata to construct the final UI payload.

### Partition and Index Notes
- Partition key: User ID for interaction history to ensure session locality and reduce cross-partition reads in the Feature Store.
- Hot key risk: Viral videos. Addressed by multi-tier caching (CDN, edge caches) and dynamic broadcast of viral item embeddings to local caches in ranking nodes.
- Required indexes: Vector indexes (HNSW/IVF) in the Vector DB for low-latency similarity search.

---

## 5. 🏗️ High-Level Architecture

### Component List
- **API Gateway / Load Balancer**: Handles auth, routing, and rate limiting.
- **Stateless App Tier (Recommendation Service)**: Orchestrates the multi-stage funnel.
- **Data Stores**: Feature Store (Feast/Hopsworks), Vector DB product (e.g., Milvus, which implements ANN algorithms like HNSW), Metadata DB.
- **Async Pipeline**: Kafka + Flink for real-time feature updates.
- **Observability and Control Plane**: Grafana, Prometheus, distributed tracing (Jaeger).

### Read Path (Recommendation Funnel)
1. Request enters API gateway with session context.
2. **Candidate Generation**: Fetch user embeddings, query Vector DB using ANN, retrieve 1,000 candidates.
3. **Light Ranking**: Filter 1,000 -> 100 using lightweight models (GBDT) and cached item features.
4. **Heavy Ranking**: Filter 100 -> 20 using complex MMoE (Multi-Gate Mixture-of-Experts) model scoring `p(Click)`, `p(WatchTime)`, `p(Like)`, `p(Share)`.
5. **Policy Reranking**: Apply business rules (diversity, freshness, deduplication).
6. **Hydration**: Fetch video titles/thumbnails from Metadata DB for the final 20.
7. Gateway returns final 20 recommendations.

### Write Path (Feedback Loop)
1. Client emits interaction event (e.g., watch time 80%).
2. API Gateway publishes event to Kafka topic.
3. Apache Flink consumes Kafka stream, aggregates in-session features (e.g., "watched 3 gaming videos").
4. Flink updates the real-time Feature Store (Feast/Hopsworks).
5. Next recommendation request fetches updated features.

### Failure-aware Path
- **Dependency timeout behavior**: If a downstream service (like Feature Store) times out, we use cached fallback values or skip the heavy computation to hit latency targets.
- **Retry policy + idempotency**: Idempotent feedback API design handles retries; read requests are inherently idempotent but typically do not retry if they exceed total budget.
- **Degraded mode**: Fall back to simple popularity-based, pre-computed lists.

---

## 6. 🔍 Deep Dives (Pick 1-2)

### Deep Dive A: Two-Tower Neural Network for Candidate Generation
- **Bottleneck**: Searching 1 Billion videos accurately in under 10ms.
- **Chosen pattern**: Two-Tower architecture. The model consists of two separate deep neural networks (towers).
  - **User Tower**: Processes user-side features. Inputs include user demographics, past 100 video watch history, historical watch time completion rates, and recent search query embeddings. It outputs a fixed-size dense vector representing the user's current state and interests.
  - **Item Tower**: Processes item-side features. Inputs include video ID, video duration, category, creator ID, and rich multi-modal visual/audio/text embeddings. It outputs a fixed-size dense vector.
  - **Training**: Trained offline using a contrastive loss function (e.g., InfoNCE), pushing the embeddings of clicked/watched videos closer to the user embedding, and pushing negative samples (unseen or skipped videos) further away.
  - **Serving**: The Item Tower embeddings are pre-computed offline or near-line and loaded into the Vector DB (Milvus/ScaNN). During inference, only the User Tower needs to be executed to generate the query embedding, which is then used for the sub-millisecond Approximate Nearest Neighbor (ANN) search.
- **Alternative considered**: Exact k-NN Search. Exact search is O(N) and too slow for 1B items.
- **Trade-off accepted**: ANN provides 95%+ recall at sub-millisecond latency, slightly trading off perfect accuracy for massive speed gains.
- **Integration with other candidates**: We also run parallel generators for Collaborative Filtering, Popularity, and Creator Subscriptions to form a diverse candidate pool of 1,000 videos.

### Deep Dive B: Exploration vs. Exploitation & Cold Start
- **Bottleneck**: Breaking filter bubbles and solving the "Cold Start" problem for brand new content.
- **Chosen pattern**: Multi-Armed Bandits (LinUCB / Thompson Sampling).
  - A pure exploitation model will only recommend historically proven popular items, trapping users in filter bubbles ("echo chambers") and failing to gather data on new videos.
  - To solve this, the pipeline allocates a small, controlled portion of the candidate slots (e.g., 5-10%) to exploration.
  - New videos are given an artificially high uncertainty bound. The Thompson Sampling algorithm samples from a distribution of expected rewards. For new items with high variance (uncertainty), there's a chance the sampled score will beat out a known good item, allowing the new video to be surfaced.
  - As users interact (or ignore) the explored video, Flink processes the feedback, the uncertainty bound shrinks, and the true expected value emerges, transitioning the item from exploration to exploitation seamlessly.
- **Alternative considered**: Epsilon-greedy (random exploration).
- **Trade-off accepted**: Bandits require more complex real-time feedback processing (to update the distributions quickly) compared to simple random epsilon, but yield much higher quality exploration without significantly degrading user experience.

### Deep Dive C: Multi-Stage Recommendation Funnel Details
- **Candidate Generation (Retrieval)**: 
  - *Funnel Size*: 1 Billion catalog -> 1,000 candidates.
  - *Algorithm/Product*: Approximate nearest neighbor (ANN) search using HNSW/ScaNN hosted on Milvus/Pinecone.
  - *Budget*: ~10ms latency total; essentially $0 compute cost per item (Vector math).
  - *Target Metric*: Recall (ensuring relevant items are retrieved).
  - *Benchmark Workload*: Evaluated on a 1B item embedding corpus (Float32, 512-dim), user-tower model serving, tested on multi-node Milvus cluster with 231k QPS concurrency.
  - We also run parallel generators for Collaborative Filtering, Popularity, and Creator Subscriptions to form a diverse candidate pool.
- **Light Ranking**:
  - *Funnel Size*: 1,000 -> 100.
  - *Algorithm*: Gradient Boosted Decision Trees (GBDT) or lightweight logistic regression. We avoid heavy neural networks here.
  - *Budget*: ~10ms total (~0.01ms per item).
  - *Target Metric*: Area Under Curve (AUC) for generic engagement.
  - *Benchmark Workload*: Model evaluated on CPU-only instances, 1,000 items/request, 231k QPS concurrency.
- **Heavy Ranking**:
  - *Funnel Size*: 100 -> 20.
  - *Algorithm*: Multi-Gate Mixture-of-Experts (MMoE) scoring. This model produces probabilities for multiple user actions simultaneously: `p(Click)`, `p(WatchTime)`, `p(Like)`, `p(Share)`.
  - *Budget*: ~20ms total (~0.2ms per item).
  - *Target Metric*: NDCG (Normalized Discounted Cumulative Gain) maximizing long-term watch time and value.
  - *Benchmark Workload*: MMoE model evaluated on GPU inference instances (e.g., Nvidia T4/A10G), scoring 100 items/request, 231k QPS concurrency.
  - The final score is a weighted sum: `Score = w1*p(Click) + w2*expected_watch_time + w3*p(Like) + w4*p(Share)`.
- **Policy Reranking**: 
  - *Funnel Size*: 20 items reordered/filtered.
  - *Budget*: <5ms latency.
  - *Target Metric*: Diversity score, creator fairness metrics.
  - *Benchmark Workload*: Evaluated via in-memory CPU heuristics checking historical constraints.
  - Final adjustments for diversity (e.g. max 2 videos per creator), topic deduplication, freshness, creator fairness.
- **Caching Considerations**: Heavy ranking results for specific item sets can be cached in a high-speed layer if they share similarities across multiple users with similar profiles.

### Deep Dive D: Feature Store and Stream Ingestion
- **Real-Time Feature Store**: We use Feast (or Hopsworks) to serve features at low latency. The Feature Store abstracts away the underlying storage layer (Redis/Memcached for online, S3/BigQuery for offline).
- **Streaming Event Ingestion**: Interactions (clicks, skips, full watches) flow from the user client to an API Gateway, which immediately produces an event to Apache Kafka.
- **Stateful Processing**: Apache Flink consumes these Kafka streams. It maintains windows and state to compute aggregated features like "number of gaming videos watched in the last 15 minutes."
- **Feedback Loop Integration**: These aggregated, real-time features are immediately written back to the Feature Store (Redis). Consequently, the very next recommendation request from that user will incorporate this latest state, enabling immediate personalization.

### Deep Dive E: Failure Modes and Resilience
- **Feature store timeout degradation to light ranker**: Feature freshness limits are strictly bounded (e.g., < 1 minute freshness target for real-time interactions, staleness up to 15 minutes allowed). If the primary Feast/Hopsworks cluster fails to return user features within the strict p95 latency budget, the system gracefully degrades. It skips the MMoE heavy ranker entirely and falls back to a purely Light Ranker (GBDT) path using slightly stale cached user embeddings.
- **Cold-start timeout**: If the exploration Bandit times out waiting for uncertainty bound convergence, it falls back to a chronologically sorted feed of newly uploaded content bounded by 100 items.
- **Policy reranking timeout**: If the complex diversity/fairness heuristics evaluation times out (exceeding its ~5ms budget), it returns the raw heavy ranker output, simply bounded to the top 20 and naively deduplicated.
- **Bad model rollout**: Serve by `model_version`, canary per cohort, rollback the ranker, and replay logged requests offline to measure impact.
- **Vector DB Outage**: In case of a major Vector DB issue, candidate generation falls back to a purely cached, pre-computed popularity list and fast collaborative filtering lookups.

**Named Failure Histories:**
- *Feature Store Partition*: State owned by Redis (serving layer). During a network partition timeout, the ranking service skips the remote lookup and fails over to a local stale cache. No replay is performed for missed reads. The system retains the p95 latency SLA by absorbing the loss in feature freshness (graceful degradation).
- *Async Stream Ingestion Lag*: State owned by Kafka/Flink (feedback ingestion). During severe cluster load or lag, real-time features go stale (exceeding the 1-minute freshness target). Once recovered, Flink replays events from the saved Kafka offset. The system retains exactly-once processing for feature aggregates, ensuring the offline model training dataset remains perfectly consistent, even if online serving experienced temporary staleness.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Pipeline Architecture | Multi-stage cascade (Retrieval -> Light -> Heavy) | Single massive Deep Learning model | Single model scoring 1B items violates p95 < 50ms latency constraint. | Quantum computing becomes cheap or specialized ASICs evolve. |
| Vector Index | Approximate Nearest Neighbor (ScaNN / HNSW) | Exact k-NN Search | Exact search is O(N) and too slow for 1B items; ANN offers 95%+ recall at sub-millisecond latency. | Recall drops below acceptable thresholds. |
| Real-time Features | Apache Flink + Feast/Hopsworks | Batch updates only (Airflow + Spark) | Batch-only cannot adapt to in-session intent shifts (e.g., user suddenly bingeing a new topic). | Real-time infrastructure cost exceeds engagement revenue gains. |
| Ranking Objective | MMoE (Multi-objective utility) | Simple CTR (Click-Through Rate) | Optimizing purely for clicks leads to clickbait proliferation. MMoE balances quality (watch time) and value. | Introduction of radically new feedback mechanisms. |
| Exploration | Bounded Policy (Bandits) | No exploration (Pure Exploit) | Avoids local optimum lock-in and allows new creators to surface. | User churn due to poor exploration content. |
| Feedback Store | Kafka Stream -> Data Lake | Direct write to Data Lake | Kafka buffers immense traffic (700K peak QPS) and isolates ingestion from processing latency. | Event size grows 100x requiring different buffering mechanism. |
| Embeddings Setup | Two-Tower Models | Single Matrix Factorization | Capture complex relationships better than standard collaborative filtering matrix factorization. | Graph Neural Network computation becomes feasible. |
| Caching | Aggressive heavy ranker caching | No caching for personalized feeds | Strict p95 latency requirements at 700k QPS demand caching to avoid computing the heavy ranker for every user. | Heavy Ranker latency decreases dramatically. |
| Metadata DB | DynamoDB/Cassandra | PostgreSQL | We need extremely fast, highly concurrent key-value lookups for hydration. Relational guarantees aren't needed for thumbnails. | Requirements evolve to need complex JOINs. |
| Data Lake | S3 + Iceberg | HDFS + Hive | Cloud-native, decoupled storage and compute, strong ACID semantics for streaming ingestion. | Cost of S3 egress exceeds acceptable bounds. |

---

## 8. 🔮 Follow-up Questions

1. **What changes at 10x scale?**
   - At 10x scale, feature store read capacity becomes a bottleneck. We would need deeper multi-tier caching architectures for features and likely a more distributed vector database topology. We might also need to shard user state across multiple Redis clusters serving the feature store.
2. **What fails first under a regional outage?**
   - Typically, cross-region state replication (e.g., global real-time features) will fall behind. We would route traffic to surviving regions but serve slightly stale recommendations. Real-time feedback processing in the failed region would need to be replayed from cross-region Kafka mirrors.
3. **How does the design change for strict consistency?**
   - Recommendation systems generally do not require strict consistency; trying to enforce it (e.g., for watch history) would unnecessarily impact availability and latency. However, if billing/monetization for creator payouts was tied directly to these event streams, we'd need exact-once processing semantics in Flink and idempotent sinks.
4. **How do you reduce cloud cost by 30%?**
   - Aggressively prune the item catalog before candidate generation (e.g., archive completely dead videos to cold storage), cache heavy ranker outputs for non-logged-in users (or users with very generic profiles), and reduce Flink processing windows to run mini-batches every 5 seconds instead of true continuous streaming.
5. **How do you support multi-region rollout?**
   - Deploy regional clusters of the Recommendation Service, Feature Store replicas, and Vector DBs. Route users to the closest region using latency-based DNS routing. User interaction data is asynchronously replicated to a global data lake for unified model training.

---

## 9. 🧩 Variants and Extensions

- **Variant 1 (Short-form Video, e.g., TikTok/Reels)**: Dwell times are much shorter, interactions are binary (swipe vs. watch), and real-time Flink processing becomes even more critical as user intent shifts in seconds. The recommendation window is typically just one video, so the latency bounds are even tighter.
- **Variant 2 (E-commerce Recommendations)**: Introduces strict inventory constraints (out of stock items must not be recommended) and focuses heavily on `p(Conversion)` and `p(Add-to-Cart)`. The candidate pool is often smaller, but metadata updates (price changes) are more frequent.
- **Variant 3 (News Feed)**: Heavily prioritizes freshness and recency over long-term relevance. Requires extremely fast index updates as news breaks. The half-life of an item is measured in hours rather than months.
- **Variant 4 (Cost-optimized startup)**: Use managed services (e.g., AWS Personalize, Pinecone) instead of building custom Two-Tower models and managing Feast/Flink clusters.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I skipped clarifying requirements
- [x] I did estimates that did not influence design
- [x] I added sharding/queueing without scale justification
- [x] I did not mention failure handling
- [x] I did not articulate trade-offs explicitly
- [x] I left no time for summary

---

## 11. 🧮 Scoring Rubric (Self-Evaluation)

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) | Your Score |
|---|---|---|---|---|
| Requirements handling | Vague | Mostly clear | Prioritized + quantified | 5 |
| Architecture clarity | Boxes only | Basic flow | End-to-end + failure-aware | 5 |
| Technical depth | Tool names | Some rationale | Pattern + metric-driven rationale | 5 |
| Trade-off quality | None | Some | Explicit and contextual | 5 |
| Communication | Disorganized | Understandable | Structured + concise | 5 |

---

## 12. ✅ Wrap-up Summary (Final 60-90 Seconds)

Use this closing pattern:
1. **Restate key requirements and constraints:** To summarize, we've designed a highly scalable video recommendation engine capable of serving personalized content to 1 Billion Daily Active Users, maintaining a p95 tail latency under 50ms.
2. **Summarize core architecture choice:** Given the massive catalog size of over 1 Billion videos, the core of our system relies on a Multi-Stage Recommendation Funnel rather than attempting to score every item. We use a Two-Tower Neural Network coupled with Approximate Nearest Neighbor search (like Milvus or ScaNN) to rapidly generate candidates, followed by a Light Ranker (GBDT) and an MMoE Heavy Ranker to score items based on a multi-objective utility function.
3. **Call out one intentional trade-off:** An intentional trade-off was allocating a portion of our serving traffic to exploration using Multi-Armed Bandits (Thompson Sampling), accepting a short-term hit to known engagement in exchange for discovering new content and solving the cold-start problem.
4. **Mention one scale-evolution step:** As the system evolves and potentially scales to 10x traffic, managing the read/write load on the real-time Flink ingestion pipeline and Feature Store will be critical to capturing in-session intent shifts seamlessly.

---

## 13. 🗺️ Requirement-to-Section Review

| Acceptance Criterion | Design Section satisfying it |
|---|---|
| 1. Daily request math is recomputable; average/peak factor distinct/assumed. | `2. Back-of-Envelope Estimation` (explicitly models 1B * 20 / 86400 as average; 3.02x peak as assumption). |
| 2. Candidate counts, per-item cost/latency budget, recall/quality metric, and benchmark workload for each stage. | `6. Deep Dives (Deep Dive C)` (details explicitly added for Candidate Gen, Light Ranking, Heavy Ranking, Policy Reranking). |
| 3. ANN algorithm and named product distinguished; model/feature/version/index assumptions explicit. | `4. Core Entities` & `5. Architecture` (distinguishes HNSW/ScaNN algorithm from Milvus/Pinecone product). |
| 4. Feature-store timeout, stale features, cold-start and policy reranking have bounded graceful fallback. | `6. Deep Dives (Deep Dive E)` (adds explicit traces for these timeouts). |
| 5. Two named failure histories show state owner, timeout/replay behavior, and retained guarantee. | `6. Deep Dives (Deep Dive E)` (details *Feature Store Partition* and *Async Stream Ingestion Lag*). |
| 6. Explicit requirement-to-section review accounts for every deliverable. | `13. Requirement-to-Section Review` (this section). |

---

## 📌 Final Checklist

- [x] Requirements and constraints captured
- [x] Estimates tied to decisions
- [x] APIs and entities are coherent
- [x] Read/write paths are explicit
- [x] Deep dive completed
- [x] Trade-offs stated
- [x] Follow-ups addressed
- [x] Strong summary delivered

---
**Real-world reference**: See how YouTube solved this in the [YouTube case study](../../case-studies/youtube-video/)
