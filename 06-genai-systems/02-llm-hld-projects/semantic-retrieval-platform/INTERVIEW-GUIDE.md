# Interview Guide for Semantic Retrieval Platform

## Overview
This guide provides interviewers with structured questions, expected answers, and red flags for candidates designing the Semantic Retrieval Platform. The platform serves as the retrieval infrastructure (chunking, embedding, vector search, ACL filtering) for downstream GenAI applications.

---

## 1. Requirements & Scoping Phase

**Prompt:** "Design the retrieval backend that internal teams will use to build their RAG copilots. It must handle 50M document chunks and strictly enforce tenant ACLs."

### What to look for:
- **Scope Boundary:** Do they realize this is *not* the LLM generation phase? They should explicitly state that final response generation is out of scope.
- **Data Freshness:** Do they ask how quickly an updated document needs to be searchable?
- **Security:** Do they immediately recognize the complexity of multi-tenant vector search?

### Red Flags 🚩
- Candidate starts designing LangChain/Agent loops.
- Fails to ask about the expected vector dimension or volume (critical for memory sizing).

---

## 2. Estimation Phase (Vector Memory Math)

**Question:** "Given 50M chunks using a 1536-dimensional embedding model, how much memory does the vector index require, and how would you optimize it?"

### Expected Strong Answer:
- **Raw Math:** 50M × 1536 dims × 4 bytes (FP32) ≈ 307 GB.
- **Graph Overhead:** Mentions that HNSW adds ~50-100% overhead, pushing total memory to ~450-600 GB.
- **Optimization:** Proposes **Scalar Quantization (INT8)** to compress vectors to 1 byte per dimension (76.8 GB raw), massively reducing infrastructure costs with minimal recall loss.

### Weak Answer / Red Flags 🚩
- Assumes vectors are stored on disk like traditional DB rows (ANN search requires RAM).
- Fails to calculate the raw byte size.
- Suggests IVF-PQ immediately without mentioning the severe recall drop compared to HNSW+INT8.

---

## 3. Architecture & Filtering (The Core Problem)

**Question:** "How do you enforce ACLs during a semantic search to ensure a user only retrieves chunks they are permitted to see?"

### Expected Strong Answer:
- Must discuss the **Single-Stage Filtered Search** approach.
- Explains why alternatives fail:
  - **Post-filtering:** Retrieves top-K from the vector DB, then filters in the app layer. **Flaw:** Catastrophic recall drop. If the user only has access to 1 rare document, the top-K might all belong to other users, resulting in an empty response even if a match exists.
  - **Pre-filtering:** Fetches allowed IDs from Postgres, then passes them to the vector DB. **Flaw:** HNSW graph fragmentation. Navigating the graph fails because most adjacent nodes are blocked.
- **Correct Solution:** The vector DB engine dynamically evaluates metadata/ACL bitsets *during* the graph traversal, bypassing unauthorized nodes but continuing to expand neighbors.

### Weak Answer / Red Flags 🚩
- "I'll just query Postgres for their documents, then embed those documents on the fly." (Terrible latency).
- Sticking stubbornly to post-filtering without realizing the recall drop.

---

## 4. Hybrid Search & Ranking

**Question:** "Vector search is bad at exact UUID or error code lookups. How do you solve this?"

### Expected Strong Answer:
- Proposes **Hybrid Search** (Dense Vectors + Sparse Keyword search like BM25).
- Explains how to merge the two ranked lists using **Reciprocal Rank Fusion (RRF)**: `Score = 1 / (k + rank)`.
- Discusses optionally adding a **Cross-Encoder Reranker** for the top 50 results to improve precision, while acknowledging the 50-150ms latency penalty.

### Weak Answer / Red Flags 🚩
- Attempts to train a custom embedding model to understand UUIDs.
- Has no strategy for combining scores from different retrieval algorithms.

---

## 5. Operations & Migration

**Question:** "OpenAI releases `text-embedding-v3` with better recall. How do you migrate the platform with zero downtime?"

### Expected Strong Answer:
- Outlines a **Dual-Index Migration**:
  1. Stand up a new Vector DB collection.
  2. Run a background job to re-embed the 50M raw text chunks with the new model.
  3. Start dual-writing new ingestions to both V2 and V3 indices.
  4. Perform shadow testing (send async traffic to V3) to compare latency and recall parity.
  5. Cutover read traffic at the API Gateway/Tenant config level.

### Weak Answer / Red Flags 🚩
- Attempts to mix V2 and V3 embeddings in the same index.
- Suggests an in-place update that requires downtime.


---

## 6. Observability and Troubleshooting Scenarios

**Question:** "A downstream RAG application team complains that retrieval latency has spiked to 500ms (violating our 200ms SLA). How do you debug and resolve this?"

### Expected Strong Answer:
- **Trace Propagation:** First, look at the distributed traces (e.g., Datadog, Jaeger) to identify the specific bottleneck. Is the delay in the Embedding generation API, the Vector DB ANN search, the ACL filter evaluation, or the Cross-Encoder reranker?
- **Hypothesis 1 (Embedding API):** If the external embedding provider is throttling us or degrading, implement a fallback semantic cache (Redis) or route traffic to a secondary provider model.
- **Hypothesis 2 (Graph Fragmentation):** If the Vector DB search is slow, check if the HNSW graph requires rebuilding/compaction due to a massive recent influx of write operations.
- **Hypothesis 3 (Reranker Overload):** If the cross-encoder is slow, check GPU utilization. Implement load shedding by dynamically disabling the reranker during peak traffic spikes to prioritize latency over marginal recall improvements.

### Weak Answer / Red Flags 🚩
- Candidate panics and says "scale up the database" without investigating the root cause.
- Fails to recognize that the embedding step (an external network call) is the most likely culprit for sudden latency spikes.

---

## 7. Scaling the Ingestion Pipeline

**Question:** "A massive new enterprise tenant signs up and initiates a bulk sync of 10 million documents. How do you ensure this doesn't degrade performance for existing tenants?"

### Expected Strong Answer:
- **Queue Separation:** Proposes using a separate Kafka topic or a dedicated consumer group for bulk ingestion jobs to prevent them from blocking the real-time CDC updates of existing tenants.
- **Rate Limiting (Backpressure):** Ensures the chunking and embedding workers are throttling their requests to the embedding API to stay within Token-Per-Minute (TPM) quotas.
- **Physical Partitioning:** Suggests routing the new tenant's embeddings to a completely new Vector DB shard or collection, avoiding HNSW graph rebuild penalties on the multi-tenant cluster.

### Weak Answer / Red Flags 🚩
- Tries to process 10 million documents synchronously via a REST API call.
- Does not account for API rate limits from the embedding provider.

---

## 8. Security and Compliance

**Question:** "How do we ensure that an engineer debugging the system cannot simply run a query that returns sensitive executive payroll documents from the HR tenant?"

### Expected Strong Answer:
- **Service Principals & Trust:** Explains that the retrieval API must strictly enforce that the caller provides a cryptographic token (e.g., JWT) representing the end-user. The API Gateway validates the token and extracts the `user_id` and `groups`.
- **Zero Trust Architecture:** The retrieval service does not accept a simple `tenant_id=HR` override parameter. It uses the validated claims from the JWT to construct the ACL bitset for the single-stage filter.
- **Audit Logging:** Every query executed against the Vector DB must log the principal identity and the metadata of the chunks retrieved, storing the logs in a tamper-evident system (like an immutable S3 bucket or Splunk) for compliance audits.

### Weak Answer / Red Flags 🚩
- Candidate assumes internal network security is enough (violates Zero Trust).
- Trusts client-provided metadata filters without cryptographic validation.

---

## 9. Evaluation Criteria (Rubric Summary)

When scoring a candidate across this 45-minute interview, evaluate them on the following spectrum:

- **Strong Hire (Staff/Principal Level):** Proactively brings up Scalar Quantization and memory math before being asked. Explains the exact mechanical failure of post-filtering. Designs a resilient, multi-tiered ingestion pipeline with CDC and DLQs. Understands the latency cost of cross-encoders and proposes RRF for hybrid search.
- **Hire (Senior Level):** Correctly identifies the need for HNSW. Understands multi-tenant isolation and advocates for single-stage filtering. Can walk through a dual-index migration strategy. Might need a hint on the exact memory math but understands vectors are RAM-heavy.
- **No Hire (Mid/Junior Level):** Confuses the retrieval platform with an LLM chat application. Tries to store vectors in Postgres without specialized indexing. Cannot explain how an ANN graph works or why ACL filtering breaks it. Tries to solve all relevance problems by "fine-tuning the LLM."
Ensure the candidate consistently frames their answers within the context of a highly scalable, multi-tenant platform infrastructure.

---

## 6. Observability and Troubleshooting Scenarios

**Question:** "A downstream RAG application team complains that retrieval latency has spiked to 500ms (violating our 200ms SLA). How do you debug and resolve this?"

### Expected Strong Answer:
- **Trace Propagation:** First, look at the distributed traces (e.g., Datadog, Jaeger) to identify the specific bottleneck. Is the delay in the Embedding generation API, the Vector DB ANN search, the ACL filter evaluation, or the Cross-Encoder reranker?
- **Hypothesis 1 (Embedding API):** If the external embedding provider is throttling us or degrading, implement a fallback semantic cache (Redis) or route traffic to a secondary provider model.
- **Hypothesis 2 (Graph Fragmentation):** If the Vector DB search is slow, check if the HNSW graph requires rebuilding/compaction due to a massive recent influx of write operations.
- **Hypothesis 3 (Reranker Overload):** If the cross-encoder is slow, check GPU utilization. Implement load shedding by dynamically disabling the reranker during peak traffic spikes to prioritize latency over marginal recall improvements.

### Weak Answer / Red Flags 🚩
- Candidate panics and says "scale up the database" without investigating the root cause.
- Fails to recognize that the embedding step (an external network call) is the most likely culprit for sudden latency spikes.

---

## 7. Scaling the Ingestion Pipeline

**Question:** "A massive new enterprise tenant signs up and initiates a bulk sync of 10 million documents. How do you ensure this doesn't degrade performance for existing tenants?"

### Expected Strong Answer:
- **Queue Separation:** Proposes using a separate Kafka topic or a dedicated consumer group for bulk ingestion jobs to prevent them from blocking the real-time CDC updates of existing tenants.
- **Rate Limiting (Backpressure):** Ensures the chunking and embedding workers are throttling their requests to the embedding API to stay within Token-Per-Minute (TPM) quotas.
- **Physical Partitioning:** Suggests routing the new tenant's embeddings to a completely new Vector DB shard or collection, avoiding HNSW graph rebuild penalties on the multi-tenant cluster.

### Weak Answer / Red Flags 🚩
- Tries to process 10 million documents synchronously via a REST API call.
- Does not account for API rate limits from the embedding provider.

---

## 8. Security and Compliance

**Question:** "How do we ensure that an engineer debugging the system cannot simply run a query that returns sensitive executive payroll documents from the HR tenant?"

### Expected Strong Answer:
- **Service Principals & Trust:** Explains that the retrieval API must strictly enforce that the caller provides a cryptographic token (e.g., JWT) representing the end-user. The API Gateway validates the token and extracts the `user_id` and `groups`.
- **Zero Trust Architecture:** The retrieval service does not accept a simple `tenant_id=HR` override parameter. It uses the validated claims from the JWT to construct the ACL bitset for the single-stage filter.
- **Audit Logging:** Every query executed against the Vector DB must log the principal identity and the metadata of the chunks retrieved, storing the logs in a tamper-evident system (like an immutable S3 bucket or Splunk) for compliance audits.

### Weak Answer / Red Flags 🚩
- Candidate assumes internal network security is enough (violates Zero Trust).
- Trusts client-provided metadata filters without cryptographic validation.

---

## 9. Evaluation Criteria (Rubric Summary)

When scoring a candidate across this 45-minute interview, evaluate them on the following spectrum:

- **Strong Hire (Staff/Principal Level):** Proactively brings up Scalar Quantization and memory math before being asked. Explains the exact mechanical failure of post-filtering. Designs a resilient, multi-tiered ingestion pipeline with CDC and DLQs. Understands the latency cost of cross-encoders and proposes RRF for hybrid search. Defends technical choices against rigorous pushback.
- **Hire (Senior Level):** Correctly identifies the need for HNSW. Understands multi-tenant isolation and advocates for single-stage filtering. Can walk through a dual-index migration strategy. Might need a hint on the exact memory math but understands vectors are RAM-heavy.
- **No Hire (Mid/Junior Level):** Confuses the retrieval platform with an LLM chat application. Tries to store vectors in Postgres without specialized indexing. Cannot explain how an ANN graph works or why ACL filtering breaks it. Tries to solve all relevance problems by "fine-tuning the LLM."


## 10. Evaluating Ingestion Resilience

**Question:** "The Kafka cluster goes down for 30 minutes. What happens to the ingestion pipeline, and how does the system recover?"

### Expected Strong Answer:
- **Client Impact:** The synchronous API Gateway should immediately return a `503 Service Unavailable` for new ingestion requests to apply backpressure to upstream clients, rather than accepting requests and dropping them.
- **Recovery:** Once Kafka is restored, the CDC connectors (Debezium) tracking the upstream databases will resume reading the Postgres WAL from their last committed offset. There is no data loss.
- **Thundering Herd:** The candidate should note that upon recovery, the embedding workers will face a massive backlog. The system must autoscale the embedding workers to clear the backlog, while ensuring they do not exceed the embedding provider's rate limits.

### Weak Answer / Red Flags 🚩
- Candidate assumes the data is lost.
- Suggests queuing the requests in the API Gateway's RAM (which will OOM crash the gateway).

---

## 11. Chunking and Relevance

**Question:** "We find that our semantic search often returns chunks that mention the right keywords but lack the context to be useful for the LLM. How do we fix this?"

### Expected Strong Answer:
- Proposes **Parent-Child Document Retrieval** or **Auto-Merging Retrieval**. The text is chunked into small, precise blocks for the vector search (the "child"), but the metadata contains a pointer to the surrounding paragraph or section (the "parent"). The platform retrieves the small chunk but returns the larger parent chunk to the LLM to provide full context.
- Proposes **Document Summaries**. Run a background job to summarize large documents. Embed the summary. If the query matches the summary, return the entire document or its top sections.

### Weak Answer / Red Flags 🚩
- Suggests "just making the chunks bigger" without realizing that dilutes the vector and ruins recall.
- Suggests changing the embedding model as a first step (ignoring the chunking strategy entirely).

---

## 12. Final Behavioral Signals
Throughout the technical interview, evaluate how the candidate handles ambiguity and constraints.
- **Did they ask about cost?** A senior engineer knows that vector search is expensive. If they design a massive IVF-PQ system without asking for the budget, that's a yellow flag.
- **Did they focus on the API contract?** A platform engineer should care deeply about the developer experience of the downstream RAG teams. If they rush past the API design, they may struggle in a platform role.
- **Are they pragmatic?** Do they jump straight to training a custom embedding model, or do they pragmatically suggest using an off-the-shelf model and focusing engineering effort on the retrieval infrastructure?

## 13. System Monitoring and Alarms

**Question:** "What are the three most critical alarms you would configure for this platform in production?"

### Expected Strong Answer:
- **Alarm 1: Vector DB Memory Utilization > 85%.** Vector DBs store the ANN graph in RAM. If they OOM (Out of Memory) crash, the entire cluster goes down, and rebuilding the index into RAM takes significant time.
- **Alarm 2: Ingestion Queue Lag > 5 Minutes.** This indicates that the Debezium/Kafka pipeline is falling behind, meaning the freshness SLA is breached and users are searching stale data.
- **Alarm 3: Retrieval p95 Latency > 250ms.** If the search query is slow, it breaks the downstream LLM's Time-To-First-Token (TTFT) budget, resulting in a poor user experience.

### Weak Answer / Red Flags 🚩
- Mentions generic CPU/Disk metrics without understanding that Memory is the lifeblood of vector search.
- Fails to monitor the asynchronous ingestion queue, treating ingestion as a fire-and-forget process.

---

## 14. Trade-offs in Chunking Overlap

**Question:** "Why do we overlap our text chunks, and what is the trade-off of increasing the overlap size?"

### Expected Strong Answer:
- **Why overlap:** To ensure that semantic context isn't severed at an arbitrary boundary (e.g., cutting a sentence in half).
- **Trade-off:** Increasing the overlap (e.g., from 50 tokens to 200 tokens) increases the total number of chunks generated per document. This linearly increases the API cost for generating embeddings and linearly increases the memory required in the Vector DB to store those chunks. The candidate must state that overlap is a direct trade-off between recall quality and infrastructure cost.

### Weak Answer / Red Flags 🚩
- Does not understand what chunk overlap is.
- Thinks overlap is free and suggests overlapping 90% of the chunk.

---

## 15. The Cold Start Scenario

**Question:** "The system has been running perfectly. Suddenly, the entire vector database cluster restarts. What happens next?"

### Expected Strong Answer:
- The API Gateway immediately starts returning 503s or falling back to a degraded sparse search (if available) for retrieval queries.
- The Vector DB must load the HNSW graph and the vectors from persistent storage (SSD/NVMe) back into RAM. Depending on the size (e.g., 100s of GBs), this could take several minutes.
- The candidate should propose architectures to mitigate this, such as **memory-mapped files (mmap)** which allow the OS to page the index into memory faster, or running a hot-standby replica cluster in a different AZ that can take the traffic while the primary restarts.

### Weak Answer / Red Flags 🚩
- Assumes the vector DB is immediately available after a restart (like Postgres).
- Fails to realize the massive I/O bottleneck of loading terabytes of vectors into RAM.

---

## 16. Wrapping Up the Interview
- Leave 5 minutes for the candidate to ask questions.
- A strong candidate will ask about the specific downstream use cases (e.g., "Are these chatbots, or batch analytics?") because they know the use case dictates the latency/recall tradeoffs.
- A strong candidate will also ask about the scale of the engineering team operating the platform, showing they understand the operational burden of managing complex data infrastructure like Kafka and Milvus.

## 17. Deep Dive: Reranking Strategies

**Question:** "We implemented a cross-encoder reranker, and our precision improved, but our p95 latency jumped to 800ms. How do we fix this without removing the reranker entirely?"

### Expected Strong Answer:
- **Candidate Pruning (Reduce top-K):** The most direct fix is to reduce the number of candidates passed to the reranker. If we are currently fetching 100 from the vector DB and reranking all 100, we should test fetching 100 but only reranking the top 20.
- **Model Distillation:** Replace the massive cross-encoder (e.g., `bge-reranker-large`) with a smaller, distilled version (e.g., `bge-reranker-base` or a custom ONNX-quantized model) deployed on specialized inference hardware (Triton/TensorRT).
- **Caching:** Cache the reranked results for identical queries in Redis.
- **Asynchronous Reranking (for specific UI patterns):** If the UI allows streaming, return the fast ANN results immediately to render the UI, and stream the reranked order seconds later (though this is complex for LLM generation).

### Weak Answer / Red Flags 🚩
- Suggests "optimizing the database query" (the database isn't the bottleneck, the GPU transformer inference is).
- Fails to understand the O(N) scaling relationship between the number of candidates and reranker latency.

---

## 18. Evaluating the 'Build vs Buy' Discussion

**Question:** "Why should we hire a team to build this platform instead of just paying for Pinecone Serverless and LangSmith?"

### Expected Strong Answer:
- **Data Privacy & Residency:** As an enterprise, we cannot send our highly sensitive internal documents (HR, Legal, M&A) to a multi-tenant SaaS provider. We need absolute VPC isolation.
- **Custom Security Requirements:** Out-of-the-box solutions often lack the capability to seamlessly integrate our complex internal Active Directory / SAML groups directly into the vector search path via Single-Stage Filtering.
- **Cost at Scale:** While Pinecone is cheap to start, storing 50M+ vectors with high QPS demands becomes exorbitant. By building it in-house with Milvus/Qdrant, we can leverage open-source INT8 scalar quantization to slash our AWS bill by 75% compared to the SaaS markup.

### Weak Answer / Red Flags 🚩
- "Because it's fun to build it ourselves." (Lacks business pragmatism).
- Fails to articulate the security and cost inflection points that justify an internal platform team.

---

## 19. Final Calibration for the Interviewer
When writing your feedback, focus on these three pillars:
1. **Infrastructure Chops:** Did they understand Kafka, Postgres, and K8s? Can they design a distributed system that doesn't fall over under load?
2. **Vector Math / GenAI Intuition:** Do they know the difference between HNSW and IVF? Do they understand why a 1536-dimensional float array uses so much RAM? Do they know what RRF is?
3. **Security Posture:** Did they treat the ACL requirement as an afterthought, or did they place it at the core of the vector search engine? 

A candidate who excels in all three is a very strong hire. A candidate who only knows the Infrastructure but fails the Vector Math is a solid backend engineer, but might need significant ramp-up time on a GenAI team.

---

## 20. Advanced Chunking Scenarios

**Question:** "A tenant uploads a 500-page highly structured legal contract. Standard 512-token chunking destroys the meaning because clauses are separated from their section headers. How does the platform handle this?"

### Expected Strong Answer:
- **Format-Aware Parsing:** The ingestion pipeline must use a parser (like LlamaParse or Unstructured) that understands document hierarchy (H1, H2, H3).
- **Hierarchical Chunking:** The chunking algorithm is configured to split *only* on structural boundaries (e.g., never split in the middle of a clause).
- **Metadata Enrichment:** The chunker explicitly injects the parent headers into the chunk's metadata (e.g., `section: "Article 4. Term and Termination"`), so even if the chunk itself just says "This agreement shall last for 5 years", the vector and the metadata retain the structural context.

### Weak Answer / Red Flags 🚩
- Suggests increasing the chunk size to 500 pages (breaking the embedding model limits).
- Suggests manually tagging the document before uploading.

---

## 21. Disaster Recovery of the Vector DB

**Question:** "The entire AWS Region goes down. We fail over to our secondary region. Our Postgres database was asynchronously replicated, but our Vector DB in the secondary region is completely empty. How do we recover?"

### Expected Strong Answer:
- **Snapshot Restoration:** The primary region should have been taking daily snapshots of the Vector DB (the HNSW graph and vectors) and storing them in an S3 bucket replicated across regions (Cross-Region Replication). The secondary region boots up and loads the latest snapshot into memory.
- **Replay the Delta:** The secondary region then reads from the replicated Postgres WAL (or the replicated Kafka topic) to replay the ingestion events that occurred between the time of the snapshot and the outage.
- This achieves a low RPO (Recovery Point Objective) and a moderate RTO (Recovery Time Objective).

### Weak Answer / Red Flags 🚩
- Suggests re-embedding all 50M chunks from scratch (which would take days and cost thousands of dollars in API fees).

## 22. Designing for Data Locality and Compliance
**Question:** "Our new European subsidiary refuses to use our US-based infrastructure due to GDPR. How do we adapt our architecture to support them without duplicating our entire engineering team?"

### Expected Strong Answer:
- Proposes a **Multi-Region / Hub-and-Spoke** architecture.
- The Control Plane (API Gateway, Job Metadata) can remain centralized (or distributed globally) but must route traffic dynamically based on the tenant.
- The Data Plane (Ingestion Workers, Vector DB, Postgres Document Store) must be fully replicated in the `eu-central-1` region.
- Documents uploaded by the European tenant are routed specifically to the European ingestion cluster, ensuring the raw text and the embeddings never leave EU soil.

### Weak Answer / Red Flags 🚩
- Suggests just running the app in the US and setting up a VPN. (Fails to understand data residency laws).
- Suggests maintaining two separate codebases for the US and EU deployments.

## 23. Troubleshooting Model Drift
**Question:** "Six months after launch, users are complaining that the search results are getting worse, even though we haven't changed the codebase. What is happening?"

### Expected Strong Answer:
- Identifies **Data Drift / Corpus Evolution**. The type of documents being uploaded has fundamentally changed (e.g., the company shifted from writing text manuals to uploading dense legal contracts).
- Identifies that the chosen chunking strategy (e.g., 512 tokens with 10% overlap) or the original embedding model may not be suited for this new data type.
- Proposes a solution: Implement telemetry to track the "empty hit rate" or the "re-ranker disagreement rate". Launch an initiative to curate a new golden dataset representing the new legal contracts, and evaluate different chunking strategies and embedding models offline to adapt to the new data shape.

### Weak Answer / Red Flags 🚩
- Blames the vector database for being slow. (Confuses latency with recall/quality).

## 24. Optimizing the Top-K
**Question:** "Our cross-encoder reranker takes 2ms per chunk. A user queries a tenant with 10 million documents. If we retrieve the top 1000 chunks from the vector database, reranking takes 2 seconds. How do we keep our P95 latency under 200ms?"

### Expected Strong Answer:
- Recognize the mathematical constraint: We can only afford to rerank a maximum of ~50-70 chunks (taking ~100-140ms, leaving 60ms for network, HNSW search, and payload assembly).
- Proposes **Dynamic Top-K Truncation:** We request the top 500 from the Vector DB. Before passing them to the reranker, we look at the raw HNSW distance scores. If the score drops off a cliff after the 30th chunk, we dynamically truncate the list at 30, and only pass those 30 to the reranker, saving massive compute time.

### Weak Answer / Red Flags 🚩
- Suggests adding more GPUs. (More GPUs scale throughput/concurrency, but a single sequential request processing 1000 chunks through a single model will still take 2 seconds).
