# Problem: Semantic Embedding Cache

## 1. Problem Statement
Design an in-memory Semantic Cache for LLM responses. Traditional caches use exact string matching (or hashing) on the input query. In Generative AI, users often ask the exact same conceptual question using slightly different phrasing (e.g., "What is the capital of France?" vs. "Tell me the capital of France"). 

To eliminate redundant LLM inference (which is slow and expensive), this cache must evaluate the semantic similarity between the user's query and previously cached queries.

## 2. Requirements

### Functional Requirements
* **Exact Match Fallback**: Must support deterministic exact string matching (via hash) to bypass expensive vector comparisons when identical queries are submitted.
* **Semantic Matching**: Must calculate the cosine similarity between the incoming query embedding and cached query embeddings.
* **Similarity Threshold**: Must support a configurable threshold `tau` (e.g., 0.90). If the best match's similarity is `>= tau`, it is considered a cache hit.
* **Namespace Isolation**: Must support multi-tenancy. A query from Tenant A must not return a cached response generated for Tenant B.

### Non-Functional Requirements
* **Capacity Bounding**: The cache must not grow indefinitely. It must evict the least recently used (LRU) entries when reaching a maximum capacity.
* **TTL Expiration**: Cache entries must expire after a configurable time-to-live (TTL).

## 3. Constraints
* The implementation must be entirely in-memory.
* Do not use external vector databases or external caching services (like Redis or Pinecone).
* Vectors (embeddings) will be provided as standard lists/arrays of floats.

## 4. Contract & Scope Boundaries
* **Microcomponent Scope**: The scope of this project is strictly limited to a single microcomponent.
* **Required Fixtures**: It must include explicit normal, error, cancellation, and privacy fixtures for comprehensive testing.
* **Provider Independence**: The implementation must strictly rely on model and provider-independent interfaces rather than integrating with specific vendor APIs.
