# Code Walkthrough: Semantic Embedding Cache

## Core Components

1.  **Cosine Similarity (`cosine_similarity`)**:
    The core mathematical function that drives semantic matching. It calculates the dot product divided by the product of the magnitudes. We include safeguards against division by zero in case of empty or zero vectors.

2.  **The LRU Structure (`TenantCache`)**:
    We leverage Python's `collections.OrderedDict`.
    *   **Insertion**: When a new query is added, its hash is used as the key.
    *   **Capacity Limit**: The `_evict_if_needed()` helper checks if `len(self.exact_cache) > capacity`. If so, it removes elements from the front (`popitem(last=False)`).
    *   **LRU Update**: Upon a cache hit, we call `self.exact_cache.move_to_end(key)`, updating its recency status.

3.  **The Matching Logic (`TenantCache.get`)**:
    *   **Phase 1 (Exact Match)**: We hash the incoming query and perform an $O(1)$ dictionary lookup. If it hits and is not expired, we return immediately.
    *   **Phase 2 (Semantic Match)**: If Phase 1 fails, we iterate linearly over the `OrderedDict` values. We calculate cosine similarity for each non-expired entry. If we find a maximum similarity that exceeds `self.tau`, we treat it as a hit, update the LRU order, and return the response.

4.  **Isolation (`SemanticCache`)**:
    A simple wrapper dictionary `namespaces`. Every `put` and `get` requires a `tenant_id`. If the tenant doesn't exist during a `get`, it's an immediate miss. If it doesn't exist during a `put`, a new `TenantCache` is instantiated dynamically.
