# Follow-ups: Semantic Embedding Cache

## Mandatory Interview Baseline
- O(1) exact match
- O(N) semantic similarity with `tau` threshold
- LRU eviction based on ordered structures
- TTL expiration (and immediate cancellation via TTL <= 0)
- Tenant isolation
- Strict input validation for empty queries/vectors and mismatched dimensions

## Optional Staff Follow-ups
*Note: All follow-ups below represent optional, unimplemented extensions and are not part of the mandatory interview baseline.*

### 1. How would you scale this to millions of cached queries?
A linear scan $O(N)$ for semantic similarity will degrade latency unacceptably. We would need to introduce an Inverted File Index (IVF) or a Hierarchical Navigable Small World (HNSW) graph to perform Approximate Nearest Neighbor (ANN) search, trading a slight bit of accuracy for $O(\log N)$ or sub-linear search times. We would likely transition from an in-memory application cache to a distributed Vector Database (like Milvus, Pinecone, or RedisVL).

### 2. How do you handle cache invalidation for system prompts?
If the underlying LLM system prompt changes (e.g., the assistant's persona is updated), all previously cached responses are now invalid, even if the semantic query matches. We would need to implement cache versioning, where the cache key includes a hash of the current system prompt or application configuration version.

### 3. Can we return partial matches?
Currently, if a similarity is `> tau`, we return the exact cached response. A follow-up feature could involve returning the cached response alongside the similarity score. If the score is between 0.85 and 0.95, the application layer might decide to inject the cached response into the LLM context as a "few-shot example" rather than returning it directly to the user, allowing the LLM to synthesize a slightly better answer faster.
