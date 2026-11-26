# Vector Databases - Interview Q&A

## Fundamentals

### Q1: What is a vector database and how does it differ from a traditional database?

**Answer:**

A vector database is a specialized database designed to store and search high-dimensional embedding vectors using similarity search. Unlike traditional databases that match exact values or keywords, vector databases find items by semantic similarity.

**Key differences:**

| Aspect | Traditional Database | Vector Database |
|--------|---------------------|-----------------|
| **Data Type** | Structured (rows, columns) or documents | High-dimensional vectors (embeddings) |
| **Query Type** | Exact match, keyword search, SQL queries | Similarity search (nearest neighbors) |
| **Indexing** | B-trees, hash indexes | ANN indexes (HNSW, IVF, PQ) |
| **Metrics** | Equality, range comparisons | Distance metrics (cosine, L2, dot product) |
| **Use Cases** | CRUD operations, transactions | Semantic search, recommendations, RAG |

**Example:**
```
Traditional: SELECT * FROM products WHERE id = 123
Vector DB: Find 5 products most similar to "wireless headphones"
           → Embeds query → Finds nearest vectors → Returns similar products
```

---

### Q2: Explain the three main distance metrics used in vector search and when to use each.

**Answer:**

**1. Cosine Similarity**
```
Formula: cos(θ) = (A · B) / (||A|| × ||B||)
Range: [-1, 1] where 1 = identical, 0 = orthogonal

When to use:
✓ Text embeddings (most common)
✓ When magnitude doesn't matter (only direction)
✓ Normalized vectors

Example: Semantic text search, document similarity
```

**2. Euclidean Distance (L2)**
```
Formula: √Σ(ai - bi)²
Range: [0, ∞) where 0 = identical

When to use:
✓ When magnitude matters
✓ Image embeddings
✓ Spatial data
✓ Unnormalized vectors

Example: Face recognition, image similarity
```

**3. Dot Product**
```
Formula: Σ(ai × bi)
Range: (-∞, +∞)

When to use:
✓ When both direction AND magnitude matter
✓ Recommendation systems (popularity + relevance)
✓ Pre-normalized vectors (equivalent to cosine)

Example: Collaborative filtering, ranking with popularity
```

**Interview tip:** For text embeddings from models like OpenAI or Cohere, use cosine similarity since they produce normalized vectors. If vectors are L2-normalized, cosine and dot product give identical rankings (but dot product is faster).

---

### Q3: What is the difference between exact search and Approximate Nearest Neighbor (ANN) search?

**Answer:**

**Exact Search (Brute Force)**
```python
def exact_search(query, vectors, k=5):
    distances = []
    for vec in vectors:  # O(n) comparisons
        dist = cosine_similarity(query, vec)  # O(d) per comparison
        distances.append((vec, dist))
    return top_k(distances)  # O(n log k)

# Total: O(n × d) - impractical for millions of vectors
```

**ANN Search (Approximate)**
```python
def ann_search(query, index, k=5):
    # Index navigates to nearby vectors in O(log n) or O(√n)
    candidates = index.search_candidates(query)  # Much smaller than n
    return top_k(candidates)

# Total: O(log n × d) or O(√n × d) - practical at scale
```

**Trade-offs:**

| Aspect | Exact Search | ANN Search |
|--------|--------------|------------|
| **Accuracy** | 100% recall | 90-99% recall |
| **Speed** | O(n × d) | O(log n × d) or O(√n × d) |
| **Scalability** | < 100K vectors | Millions to billions |
| **Memory** | O(n × d) | O(n × d) + index overhead |

**When each makes sense:**
- **Exact**: Small datasets (<10K), compliance requires exactness, benchmarking
- **ANN**: Production systems at scale, 95%+ recall is acceptable, latency matters

**Interview insight:** Most production vector DBs use ANN. The key is tuning index parameters (e.g., HNSW's `ef` parameter) to balance recall vs latency.

---

## Indexing Algorithms

### Q4: Explain how HNSW (Hierarchical Navigable Small World) works and why it's popular.

**Answer:**

**HNSW Structure:**
```
Layer 2 (sparse):    A ───────────────── D
                     │                    │
Layer 1 (medium):    A ──── B ──── C ──── D ──── E
                     │      │      │      │      │
Layer 0 (dense):     A─B─C─D─E─F─G─H─I─J─K (all vectors)

Search path for query Q (starting at A):
1. Layer 2: Jump from A to D (greedy, closest at this layer)
2. Layer 1: From D, find E is closer
3. Layer 0: From E, navigate to exact neighbors

Logarithmic hops through layers → O(log n) search
```

**How it works:**

1. **Construction:**
   - Each vector inserted at Layer 0
   - Probabilistically promoted to higher layers (like skip list)
   - Connected to M nearest neighbors per layer

2. **Search:**
   - Start at highest layer, enter at a random node
   - Greedily jump to closest neighbor
   - When stuck (no closer neighbor), descend to next layer
   - Repeat until Layer 0, return k-nearest neighbors

**Why it's popular:**

| Advantage | Impact |
|-----------|--------|
| **High recall** | 95-99% with proper tuning |
| **Fast search** | O(log n) average, ~1ms for millions of vectors |
| **Parallel queries** | Read-only structure, highly concurrent |
| **Incremental updates** | Can add vectors without full rebuild |
| **Robust** | Performs well across diverse datasets |

**Parameters to tune:**
- **M**: Connections per node (higher = better recall, more memory)
- **efConstruction**: Search neighbors during build (higher = better quality)
- **efSearch**: Search scope during query (higher = better recall, slower)

**Trade-off:** Memory usage is O(n × d × M), which is 2-10× the raw vector data. For memory-constrained systems, consider IVF or product quantization.

---

### Q5: When would you choose IVF (Inverted File Index) over HNSW?

**Answer:**

**IVF Characteristics:**
```
1. Cluster vectors into N partitions (centroids via k-means)
2. Build inverted index: partition → list of vectors

Query:
├─ Find nearest centroids (nprobe parameter)
├─ Search only vectors in those partitions
└─ Much smaller search space than full dataset

Example:
1M vectors → 1000 partitions → ~1000 vectors per partition
nprobe=10 → Search 10,000 vectors instead of 1M (100× speedup)
```

**Choose IVF when:**

| Scenario | Reason |
|----------|--------|
| **Very large datasets (100M+)** | IVF scales better than HNSW at billion-scale |
| **Memory-constrained** | IVF has lower memory overhead than HNSW |
| **Batch queries** | Can parallelize partition searches efficiently |
| **Combined with PQ** | IVF-PQ for massive compression (common in Faiss) |
| **Static dataset** | IVF is efficient if vectors don't change often |

**Choose HNSW when:**

| Scenario | Reason |
|----------|--------|
| **High recall required** | HNSW typically achieves higher recall |
| **Real-time updates** | HNSW handles incremental inserts better |
| **Medium datasets (1M-100M)** | Sweet spot for HNSW |
| **Low-latency queries** | HNSW usually faster than IVF |
| **Untuned workload** | HNSW more forgiving with default settings |

**Hybrid approach (IVF-HNSW):**
Some systems use IVF for coarse partitioning, then HNSW within each partition for fine-grained search (best of both worlds).

**Interview insight:** Mention that Facebook's Faiss library popularized IVF-PQ for billion-scale similarity search, while standalone HNSW is the default in most modern vector DBs (Weaviate, Qdrant, Pinecone).

---

### Q6: What is Product Quantization (PQ) and when would you use it?

**Answer:**

**Product Quantization** compresses vectors by splitting them into sub-vectors and quantizing each independently.

**How it works:**
```
Original vector (768 dimensions):
[0.12, 0.87, -0.34, ..., 0.56]  (768 × 4 bytes = 3072 bytes)

PQ (8 sub-vectors of 96 dims each):
1. Split into 8 sub-vectors
2. Cluster each sub-space into 256 centroids (codebook)
3. Represent each sub-vector by 1 byte (centroid ID)

Compressed: [42, 189, 7, ..., 201]  (8 bytes)

Compression: 3072 bytes → 8 bytes (384× reduction!)
```

**Distance computation:**
```
Instead of full vector distance:
1. Look up sub-vector centroids from codebooks
2. Compute distance on compressed representation
3. Slight loss in accuracy, huge speed/memory gain
```

**Use PQ when:**

| Scenario | Why |
|----------|-----|
| **Billions of vectors** | Cannot fit full vectors in memory |
| **Memory budget is tight** | 10-100× compression without external storage |
| **Moderate recall OK** | PQ degrades recall by 5-15% |
| **Batch processing** | Parallelizes well on GPUs |

**Trade-offs:**

| Aspect | No Compression | PQ | PQ + IVF |
|--------|---------------|-----|----------|
| **Memory** | 100% | 1-10% | 1-5% |
| **Recall** | 100% | 85-95% | 80-90% |
| **Speed** | Baseline | 5-10× faster | 50-100× faster |
| **Flexibility** | ✅ | ❌ (lossy) | ❌ (lossy) |

**Real-world usage:**
- **Facebook (Faiss)**: IVF-PQ for billion-scale image search
- **Spotify**: Music recommendation at scale
- **Pinterest**: Visual search with compression

**Interview tip:** Mention that PQ is essential for massive scale (billions of vectors) but modern vector DBs (Pinecone, Weaviate) often hide this complexity. If asked about memory optimization, bring up PQ as the go-to technique.

---

## System Design

### Q7: Design a vector database from scratch. What are the key components?

**Answer:**

**High-level architecture:**
```
┌─────────────────────────────────────────────────────────┐
│                    Vector Database                      │
├─────────────────────────────────────────────────────────┤
│  API Layer (REST/gRPC)                                  │
│  ├─ Insert(vectors, metadata)                           │
│  ├─ Search(query_vector, top_k, filters)                │
│  └─ Delete(ids)                                         │
├─────────────────────────────────────────────────────────┤
│  Query Engine                                            │
│  ├─ Query Parser (extract filters)                      │
│  ├─ Pre-filter or Post-filter logic                     │
│  └─ Result Merger (distributed search)                  │
├─────────────────────────────────────────────────────────┤
│  Index Manager                                           │
│  ├─ Index Type: HNSW, IVF, or Flat                      │
│  ├─ Build/Rebuild logic                                 │
│  └─ In-memory or Disk-backed                            │
├─────────────────────────────────────────────────────────┤
│  Storage Layer                                           │
│  ├─ Vector Storage (binary blobs or columnar)           │
│  ├─ Metadata Storage (key-value or SQL)                 │
│  └─ WAL (Write-Ahead Log for durability)                │
├─────────────────────────────────────────────────────────┤
│  Distributed Components (for scale)                     │
│  ├─ Sharding (consistent hashing or range-based)        │
│  ├─ Replication (primary-replica)                       │
│  └─ Coordinator (query routing)                         │
└─────────────────────────────────────────────────────────┘
```

**Key design decisions:**

**1. Indexing Strategy**
```
Options:
├─ HNSW: High recall, medium memory, real-time inserts
├─ IVF: Scalable, lower memory, batch-friendly
└─ Flat: Small datasets (<10K), exact search

Choice: Start with HNSW for versatility
```

**2. Storage**
```
In-memory vs Disk:
├─ In-memory: Fast, limited by RAM
├─ Disk (SSD): Higher latency, unlimited scale
└─ Hybrid: Hot data in memory, cold on disk

Choice: Memory-mapped files (mmap) for balance
```

**3. Metadata Filtering**
```
Pre-filter:
├─ Apply filters before ANN search
├─ Smaller search space → faster
└─ Risk: Too restrictive filter → poor recall

Post-filter:
├─ Run ANN search, then filter results
├─ Better recall
└─ Wastes compute on filtered-out results

Choice: Hybrid - filter if selective enough, else post-filter
```

**4. Distributed Architecture**
```
Sharding:
├─ Shard by vector ID (consistent hashing)
├─ Each shard has own index
└─ Query all shards, merge top-k results

Replication:
├─ Primary-replica per shard
├─ Writes to primary, reads from any replica
└─ Raft or Paxos for consensus
```

**5. Consistency Model**
```
Eventual consistency:
├─ Async replication
├─ Higher throughput
└─ Acceptable for most ML workloads

Strong consistency:
├─ Sync replication
├─ Lower throughput
└─ Needed for critical applications
```

**Follow-up questions to anticipate:**
- How do you handle updates? (Rebuild index or incremental)
- How do you scale writes? (Batch inserts, async indexing)
- How do you ensure durability? (WAL, checkpoints)

---

### Q8: How would you implement metadata filtering in a vector database? Discuss pre-filtering vs post-filtering.

**Answer:**

**Scenario:** Search for "software engineer jobs" with filter: `location='San Francisco' AND salary>150000`

**1. Post-Filtering (Naive)**
```python
def search_post_filter(query_vector, filters, k=10):
    # Step 1: Run ANN search for top N (N > k to account for filtering)
    candidates = index.search(query_vector, k=100)

    # Step 2: Filter results
    filtered = [c for c in candidates if matches_filters(c, filters)]

    # Step 3: Return top k
    return filtered[:k]

# Problem: If only 5/100 match filters, we don't get k=10 results
# Need to over-fetch (search k=1000 or more) → wasteful
```

**2. Pre-Filtering (Selective)**
```python
def search_pre_filter(query_vector, filters, k=10):
    # Step 1: Get IDs matching filters from metadata DB
    filtered_ids = metadata_db.query(filters)  # e.g., 10K IDs

    # Step 2: Search only filtered vectors
    # Option A: Build temporary index (slow)
    # Option B: Partition index by common filters (better)
    candidates = index.search_subset(query_vector, filtered_ids, k)

    return candidates

# Problem: If filter is too selective (10 IDs), ANN index ineffective
```

**3. Hybrid Approach (Production-Ready)**
```python
def search_hybrid(query_vector, filters, k=10):
    # Estimate filter selectivity
    matching_count = metadata_db.count(filters)
    total_count = index.size()
    selectivity = matching_count / total_count

    if selectivity < 0.01:  # Very selective (<1%)
        # Pre-filter: Small subset, use filtered IDs
        filtered_ids = metadata_db.query(filters)
        return index.search_subset(query_vector, filtered_ids, k)

    elif selectivity > 0.5:  # Not selective (>50%)
        # Post-filter: Most vectors match, search all then filter
        candidates = index.search(query_vector, k * 2)
        return [c for c in candidates if matches(c, filters)][:k]

    else:  # Medium selectivity
        # Partitioned index: Pre-build indexes per common filter
        partition = get_partition(filters)  # e.g., location-based shard
        return partition.search(query_vector, k)

# Best of both worlds
```

**Production considerations:**

| Aspect | Implementation | Trade-off |
|--------|----------------|-----------|
| **Index partitioning** | Separate indexes per common filter (e.g., country, category) | More memory, faster filtered queries |
| **Bitmap indexes** | Roaring bitmaps for metadata (fast AND/OR) | Metadata-first search, then vector lookup |
| **HNSW with filters** | Extend HNSW to skip filtered-out nodes during graph traversal | Integrated filtering, complex implementation |
| **Two-stage ranking** | Coarse filter → ANN search → Fine re-rank | Balanced approach |

**Real-world examples:**

- **Qdrant**: Payload-first filtering with bitmap indexes
- **Weaviate**: Pre-filter if selective, post-filter otherwise
- **Pinecone**: Metadata indexes for hybrid search
- **Milvus**: Scalar indexes alongside vector indexes

**Interview tip:** Emphasize that the right approach depends on filter selectivity. Show you understand the trade-offs and can reason about when each makes sense.

---

### Q9: Your vector search system is experiencing high latency (500ms per query). How would you debug and optimize?

**Answer:**

**Step-by-step debugging:**

**1. Instrument and measure:**
```
Break down query into stages:
├─ API parsing: ~1ms
├─ Metadata filtering: ~50ms
├─ ANN search: ~400ms ← Bottleneck
├─ Post-filtering: ~30ms
└─ Result serialization: ~20ms

Total: 501ms
```

**2. Identify root cause:**

| Possible Issue | Diagnostic | Fix |
|----------------|------------|-----|
| **Index too large for memory** | Check RAM usage, swap activity | Shard the index, add more memory |
| **Poor ANN index tuning** | Low recall → searching too many candidates | Increase `efSearch` (HNSW), reduce `nprobe` (IVF) |
| **Disk I/O bottleneck** | High disk latency, slow SSD | Move to faster SSD, use memory-mapped files |
| **No warm cache** | First query slow, subsequent fast | Pre-warm index on startup |
| **Unoptimized distance computation** | CPU-bound | Use SIMD instructions, GPU acceleration |
| **Metadata filter too broad** | Post-filtering many results | Switch to pre-filtering, add metadata index |
| **Single-threaded search** | CPU underutilized | Parallelize search across partitions |

**3. Optimization strategies:**

**A. Tune index parameters**
```python
# HNSW tuning
index = HNSW(
    M=16,              # Default: 16 (increase for better recall)
    ef_construction=200,  # Build quality (higher = better but slower)
    ef_search=50       # Query param: increase for better recall
)

# Experiment:
ef_search=32 → 200ms, 90% recall
ef_search=64 → 300ms, 95% recall ← Good balance
ef_search=128 → 450ms, 98% recall ← Diminishing returns
```

**B. Implement caching**
```python
# Cache query embeddings
embedding_cache = LRU(maxsize=10000)

# Cache search results for popular queries
result_cache = LRU(maxsize=1000)

# Reduces embedding model calls (100ms+) and repeat searches
```

**C. Shard and parallelize**
```python
# Distribute across 4 shards
shards = [Shard(index_0), Shard(index_1), Shard(index_2), Shard(index_3)]

# Parallel search
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(shard.search, query, k=10) for shard in shards]
    results = [f.result() for f in futures]

# Merge top-k from each shard
final_results = merge_top_k(results, k=10)

# Reduces latency from 400ms → 120ms (4× shards + merge overhead)
```

**D. Hardware acceleration**
```python
# Option 1: Use SIMD (AVX2, AVX-512)
distances = simd_cosine_similarity(query, vectors)  # 2-4× faster

# Option 2: GPU acceleration (for large batches)
distances = gpu_cosine_similarity(query, vectors)  # 10-100× faster
```

**E. Approximate aggressively**
```python
# Reduce search quality for speed
index.ef_search = 20  # Very approximate, 50ms latency, 85% recall

# Then re-rank top candidates with exact distance
candidates = index.search(query, k=100)  # Fast approximate
reranked = exact_search(query, candidates, k=10)  # Slow but small set
```

**4. Monitoring and alerting:**
```
Metrics to track:
├─ p50, p95, p99 latency
├─ QPS (queries per second)
├─ Recall @ 10 (sample queries)
├─ Cache hit rate
├─ Index build time
└─ Memory usage

Alert on:
├─ p99 latency > 1 second
├─ Recall < 90%
├─ Cache hit rate < 60%
```

**Interview follow-up:** "After optimization, we achieved 100ms latency with 95% recall. Next steps would be A/B testing to ensure user metrics (CTR, engagement) didn't degrade, then rolling out the changes."

---

### Q10: How would you design a vector database for a RAG (Retrieval-Augmented Generation) system serving 1M daily active users?

**Answer:**

**Requirements gathering:**
```
Scale:
├─ 1M DAU → ~10M queries/day → 120 QPS average, 600 QPS peak
├─ 10M documents → ~1B chunks (100 chunks/doc) → 1B vectors
├─ Embedding: 1536 dims (OpenAI ada-002) → 6 KB per vector → 6 TB raw

Latency SLA:
├─ p50 < 100ms (RAG retrieval step)
├─ p95 < 300ms
├─ p99 < 1 second

Durability:
├─ No data loss (documents are source of truth, but rebuilding is expensive)
├─ Eventual consistency OK (minutes stale acceptable)
```

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  ├─ API Gateway (rate limiting, auth)                           │
│  └─ Load Balancer                                               │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Query Node 1  │ │ Query Node 2  │ │ Query Node N  │  (Stateless)
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Shard 1     │ │   Shard 2     │ │   Shard N     │
│ (200M vectors)│ │ (200M vectors)│ │ (200M vectors)│
│  - Primary    │ │  - Primary    │ │  - Primary    │
│  - Replica 1  │ │  - Replica 1  │ │  - Replica 1  │
│  - Replica 2  │ │  - Replica 2  │ │  - Replica 2  │
└───────────────┘ └───────────────┘ └───────────────┘

Metadata DB (PostgreSQL or DynamoDB):
├─ Document ID, chunk ID, source URL, timestamp
└─ Indexed for fast filtering
```

**Key design decisions:**

**1. Sharding strategy:**
```
Shard by tenant ID (multi-tenant) or document ID:
├─ 5 shards × 200M vectors each
├─ Each shard fits in memory (200M × 6 KB = 1.2 TB with overhead)
└─ Query all shards in parallel, merge top-k

Replication:
├─ 3 replicas per shard (N=3)
├─ Writes to primary, reads from any replica
└─ Async replication (eventual consistency)
```

**2. Index choice:**
```
HNSW:
├─ 1B vectors → 5 shards × 200M each → 200M per index (manageable)
├─ Memory: ~3 TB per shard (vector data + HNSW graph)
├─ Hardware: 32 GB RAM × 100 nodes → 3.2 TB (fit with buffer)

Alternative (if memory-constrained):
├─ IVF-PQ: 6 TB → 60 GB compressed (100× reduction)
├─ Trade-off: 90% recall vs 98% with HNSW
```

**3. Caching:**
```
L1: Query embedding cache (Redis)
├─ Cache user queries → embeddings
├─ Avoid re-embedding popular queries (100ms saved)
├─ LRU, 100K queries, ~1 GB

L2: Search result cache (Redis)
├─ Cache top-k results for popular queries
├─ TTL: 5 minutes (staleness acceptable)
├─ ~10 GB

L3: Document cache (Redis)
├─ Cache retrieved document chunks for LLM
├─ Avoid fetching from S3 repeatedly
```

**4. Write path:**
```
Document ingestion:
1. User uploads document → S3
2. Async worker: Chunk → Embed → Write to vector DB
3. Batch inserts (1000 chunks at a time)
4. Index rebuild: Incremental (HNSW supports inserts)

Write throughput:
├─ 10K new documents/day → 1M chunks/day
├─ Batch insert: 1M / 86400s = ~12 chunks/sec (low)
└─ No special optimization needed
```

**5. Read path:**
```
Query flow:
1. User query → Query Node (load balanced)
2. Embed query (cache hit or call embedding API)
3. Fan-out search to all 5 shards (parallel)
4. Each shard:
   ├─ Apply metadata filters (pre-filter if selective)
   ├─ HNSW search (top-20 per shard)
   └─ Return results
5. Merge top-20 from each shard → global top-10
6. Fetch document chunks from metadata DB or cache
7. Return to LLM for RAG

Latency breakdown:
├─ Embedding: 50ms (cached) or 150ms (API call)
├─ Parallel shard search: 80ms (HNSW)
├─ Merge + fetch metadata: 20ms
└─ Total: 100-200ms (within SLA)
```

**6. Monitoring and alerting:**
```
Metrics:
├─ Query latency (p50, p95, p99)
├─ Recall @ 10 (offline eval on golden set)
├─ Cache hit rate (embedding, results)
├─ Shard health (replica lag, disk usage)
└─ Document ingestion rate

Alerts:
├─ p99 latency > 1 second → Page on-call
├─ Recall < 90% → Investigate index degradation
├─ Replica lag > 5 minutes → Check replication
```

**7. Disaster recovery:**
```
Backup:
├─ Daily snapshot of each shard → S3
├─ Metadata DB: Continuous backup (point-in-time recovery)
└─ Documents in S3 (source of truth)

Recovery:
├─ Shard failure: Promote replica to primary (<1 min)
├─ Full cluster loss: Restore from S3, rebuild indexes (hours)
```

**Cost estimate:**
```
Infrastructure:
├─ 5 shards × 3 replicas = 15 nodes
├─ Each node: 256 GB RAM, 2 TB SSD, 32 cores
├─ AWS r6i.8xlarge: $2/hr × 15 = $30/hr = $21K/month

Storage:
├─ Vector data: 6 TB (replicated 3×) = 18 TB
├─ S3 (documents): 1 TB = $23/month
├─ Total storage: ~$400/month

Embedding API:
├─ 10M queries/day × $0.0001/query = $1K/day = $30K/month

Total: ~$51K/month
```

**Optimization ideas to reduce cost:**
- Use IVF-PQ to reduce memory footprint (fewer/cheaper nodes)
- Cache embeddings aggressively (reduce API calls)
- Tier storage (hot data in memory, cold on disk)

**Interview follow-up:** Discuss how you'd evolve this as the system grows (e.g., federated search across multiple collections, multi-region deployment).

---

## Advanced Topics

### Q11: How would you implement hybrid search (combining keyword and vector search)?

**Answer:**

**Hybrid search** combines traditional keyword search (BM25) with semantic vector search for better relevance.

**Architecture:**
```
Query: "best laptop for programming"

┌─────────────────────────────────────────────────┐
│             Hybrid Search Engine                │
├─────────────────────────────────────────────────┤
│  1. Keyword Search (BM25):                      │
│     - Index documents with inverted index       │
│     - Fast exact keyword matching               │
│     - Results: [doc_5, doc_12, doc_23]          │
│                                                 │
│  2. Vector Search (Semantic):                   │
│     - Embed query → similarity search           │
│     - Results: [doc_8, doc_12, doc_19]          │
│                                                 │
│  3. Fusion (Combine rankings):                  │
│     - Reciprocal Rank Fusion (RRF)              │
│     - Score normalization + weighted sum        │
│     - Final: [doc_12, doc_5, doc_8, ...]        │
└─────────────────────────────────────────────────┘
```

**Fusion strategies:**

**1. Reciprocal Rank Fusion (RRF)**
```python
def reciprocal_rank_fusion(results_keyword, results_vector, k=60):
    scores = {}

    # Keyword search results
    for rank, doc_id in enumerate(results_keyword):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    # Vector search results
    for rank, doc_id in enumerate(results_vector):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)

    # Sort by combined score
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Example:
# Keyword: [doc_A (rank 1), doc_B (rank 2), doc_C (rank 3)]
# Vector:  [doc_B (rank 1), doc_D (rank 2), doc_A (rank 3)]
#
# Scores:
# doc_A: 1/(60+1) + 1/(60+3) = 0.0164 + 0.0159 = 0.0323
# doc_B: 1/(60+2) + 1/(60+1) = 0.0161 + 0.0164 = 0.0325 ← Top
# doc_C: 1/(60+3) = 0.0159
# doc_D: 1/(60+2) = 0.0161
#
# Final ranking: [doc_B, doc_A, doc_D, doc_C]
```

**2. Weighted Sum (Score Normalization)**
```python
def weighted_hybrid_search(query, alpha=0.7):
    # Keyword search (BM25 scores)
    keyword_results = bm25_search(query)  # [(doc, score), ...]

    # Vector search (cosine similarity scores)
    vector_results = vector_search(embed(query))  # [(doc, score), ...]

    # Normalize scores to [0, 1]
    keyword_scores = normalize(keyword_results)
    vector_scores = normalize(vector_results)

    # Weighted combination
    combined = {}
    for doc, score in keyword_scores:
        combined[doc] = alpha * score

    for doc, score in vector_scores:
        combined[doc] = combined.get(doc, 0) + (1 - alpha) * score

    return sorted(combined.items(), key=lambda x: x[1], reverse=True)

# alpha=0.7 → 70% keyword, 30% semantic
# Tune alpha based on use case (exact matches vs semantic)
```

**When to use each approach:**

| Use Case | Strategy | Reason |
|----------|----------|--------|
| **Exact match important** (product SKU, name) | Higher keyword weight (α=0.8) | User knows exact term |
| **Semantic understanding needed** (support docs) | Higher vector weight (α=0.3) | User describes problem |
| **Balanced** (e-commerce search) | RRF or α=0.5 | Combine both |

**Production considerations:**

1. **Separate indexes:**
   - Inverted index (Elasticsearch) for keywords
   - Vector index (Pinecone, Weaviate) for semantics
   - Federate queries and merge results

2. **Single database (Weaviate, Qdrant):**
   - Built-in hybrid search support
   - Both indexes co-located
   - Lower latency (no network hop)

3. **Query analysis:**
   - Short queries (1-2 words) → favor keyword
   - Long queries (sentences) → favor semantic
   - Adjust α dynamically based on query

**Interview insight:** Mention that Elasticsearch 8.0+ supports vector search natively (kNN plugin), enabling true hybrid search in a single system.

---

### Q12: Explain how you would handle vector database updates (inserts, updates, deletes) at scale.

**Answer:**

Vector databases face unique challenges with updates because indexes (especially HNSW) are optimized for read performance and don't support efficient in-place updates.

**Update strategies:**

**1. Inserts:**

**Approach A: Incremental Insert (HNSW)**
```python
# HNSW supports real-time inserts
def insert_vector(vector, metadata):
    # Add to index (O(log n) with graph traversal)
    index.add(vector)

    # Add metadata to separate store
    metadata_db.insert(vector.id, metadata)

# Pros: Real-time, no downtime
# Cons: Each insert rebuilds graph connections (expensive for batches)
```

**Approach B: Batch Insert + Rebuild**
```python
# Buffer inserts, rebuild index periodically
def batch_insert(vectors):
    # Accumulate in buffer
    buffer.add_all(vectors)

    # Rebuild index every hour or at 100K vectors
    if buffer.size() > 100000 or time_since_rebuild() > 1h:
        new_index = build_index(existing_vectors + buffer)
        swap_index(new_index)  # Atomic swap
        buffer.clear()

# Pros: Efficient for large batches
# Cons: Stale data until rebuild (eventual consistency)
```

**Approach C: Dual Index (Write Path)**
```python
# Maintain two indexes: primary (large) + delta (small, recent)
def insert_vector(vector):
    delta_index.add(vector)  # Fast insert

    # Periodically merge delta → primary
    if delta_index.size() > 10000:
        merge_indexes(primary, delta)
        delta_index.clear()

def search(query, k):
    # Search both indexes
    primary_results = primary_index.search(query, k)
    delta_results = delta_index.search(query, k)

    # Merge top-k
    return merge_results(primary_results, delta_results, k)

# Pros: Balance freshness and performance
# Cons: Complex merging logic
```

**2. Updates (Modify existing vector):**

**Problem:** Vectors don't have a natural "update" operation—you can't change embeddings without recomputing them.

**Solution:**
```python
def update_vector(vector_id, new_metadata=None, new_embedding=None):
    # Option 1: Delete + Insert (most common)
    delete_vector(vector_id)
    insert_vector(new_embedding or recompute_embedding(), new_metadata)

    # Option 2: Metadata-only update (fast)
    if new_embedding is None:
        metadata_db.update(vector_id, new_metadata)  # No index change

# In practice: Updates are rare in vector DBs
# Documents change → Re-chunk → Re-embed → New vectors
```

**3. Deletes:**

**Approach A: Soft Delete (Tombstone)**
```python
def delete_vector(vector_id):
    # Mark as deleted in metadata
    metadata_db.set_deleted(vector_id, True)

    # Don't remove from index immediately
    # Filter out during query
    def search(query, k):
        results = index.search(query, k * 2)  # Over-fetch
        return [r for r in results if not metadata_db.is_deleted(r.id)][:k]

# Pros: Fast delete (no index modification)
# Cons: Index grows with deleted vectors (compaction needed)
```

**Approach B: Lazy Compaction**
```python
def compact_index():
    # Periodically rebuild index without deleted vectors
    if deleted_ratio() > 0.2:  # 20% deleted
        active_vectors = get_non_deleted_vectors()
        new_index = build_index(active_vectors)
        swap_index(new_index)

# Schedule compaction:
# - Nightly (low traffic period)
# - When deleted % exceeds threshold
```

**Approach C: Immediate Delete (HNSW)**
```python
def delete_vector(vector_id):
    # Remove from HNSW graph
    index.remove(vector_id)  # Rewire connections

    # Remove from metadata
    metadata_db.delete(vector_id)

# Pros: Clean, no wasted space
# Cons: Expensive (graph rewiring is O(M × log n))
```

**Scaling strategies:**

**4. Partitioning for high write throughput:**
```
Shard by time or tenant:
├─ Shard 1: Documents from 2024-01 (immutable, frozen index)
├─ Shard 2: Documents from 2024-02 (immutable)
├─ Shard 3: Documents from 2024-03 (active, accepts writes)
└─ Shard 4: Delta index (newest, real-time inserts)

Query: Search all shards in parallel, merge results

Benefits:
✓ Immutable shards → No index churn, optimal performance
✓ Active shard → Small, fast to rebuild
✓ Horizontal scale writes (add new shards)
```

**5. Write-Ahead Log (WAL) for durability:**
```python
def insert_vector(vector, metadata):
    # 1. Write to WAL (append-only log)
    wal.append({"op": "insert", "vector": vector, "metadata": metadata})

    # 2. Write to index (asynchronous)
    async_index_write(vector)

    # 3. Write to metadata DB
    metadata_db.insert(vector.id, metadata)

# On crash:
# - Replay WAL to recover uncommitted inserts
# - Rebuild index from WAL + metadata DB
```

**Production example (Weaviate):**
```
Write path:
1. WAL append (durable)
2. In-memory HNSW insert (fast)
3. Async flush to disk (batched)
4. Background compaction (merge segments)

Read path:
1. Search in-memory index (hot data)
2. Search disk segments (cold data)
3. Merge results

Handles 10K inserts/sec per shard
```

**Interview follow-up:** "What's your strategy for handling schema changes (adding new fields to metadata)?"

**Answer:** Metadata schema is flexible (key-value or JSON), so adding fields is easy. Vector dimension changes require re-embedding all documents (expensive). Use versioned collections to run new embeddings in parallel, then cutover.

---

## Key Takeaways for Interviews

1. **Understand the fundamentals**: Know distance metrics, ANN algorithms (HNSW, IVF), and trade-offs

2. **Think at scale**: 1M vectors is trivial; 1B vectors requires thoughtful design (sharding, compression)

3. **Balance accuracy vs performance**: ANN is approximate—know how to tune recall/latency trade-off

4. **Metadata filtering is critical**: Most production queries filter by tenant, date, category, etc.

5. **Embeddings are expensive**: Cache aggressively, batch API calls, consider self-hosted models

6. **Hybrid search is common**: Pure vector search misses exact matches; combine with keyword search

7. **Monitoring and evaluation**: Track recall, latency, and cost—not just uptime

8. **RAG is the killer app**: Most interviews ask about vector DBs in context of RAG systems

9. **Know the ecosystem**: Pinecone (managed), Weaviate (hybrid), Milvus (scale), pgvector (simple)

10. **Updates are hard**: Vector indexes are read-optimized; design for append-heavy workloads

---

**Recommended preparation:**
- Build a simple vector store (see Python code example in this directory)
- Run Weaviate or Chroma locally, experiment with queries
- Read Pinecone, Weaviate, or Qdrant architecture blogs
- Practice designing RAG systems end-to-end
