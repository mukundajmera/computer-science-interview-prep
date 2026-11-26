# Evaluation Rubric: Semantic Embedding Cache

## Grading Levels
* **L4 (Minimum Accepted):** Intuitive minimum example is present. The `SemanticCache` correctly implements exact matching and fallback to semantic matching.
* **L5 (Strong):** Understands trade-offs. Can explain why an $O(N)$ linear scan is used here vs. Approximate Nearest Neighbor (ANN) search, and understands the limits of in-memory caching vs. vector databases.
* **L6/L7 (Exceptional):** Optional failure trace with assumptions. The candidate correctly handles exact isolation of cross-tenant data and gracefully manages time abstraction with deterministic behavior.

*Note: Ensure to distinguish simulations/proof sketches from deployed systems/formal verification in the context of these implementations.*

## Functional Correctness (50%)
* [ ] **Exact Match Fallback**: Does the cache reliably bypass vector math when the exact string hash is already cached?
* [ ] **Semantic Matching**: Is the cosine similarity calculated correctly and evaluated against the `tau` threshold?
* [ ] **Highest Similarity Selection**: Does the semantic scan return the *best* match above the threshold, or does it incorrectly return the *first* match it finds?
* [ ] **Tenant Isolation**: Are queries strictly segregated by `tenant_id`?
* [ ] **Input Validation**: Are empty queries, empty vectors, and vectors of mismatched dimensions rejected with a `ValueError`?

## Eviction & Expiration (30%)
* [ ] **LRU Eviction**: Are the oldest, least-accessed items successfully removed when capacity bounds are exceeded?
* [ ] **TTL Expiration**: Are items reliably ignored/deleted after their absolute expiration timestamp passes?
* [ ] **Cancellation via TTL**: Does a TTL of 0 or less correctly trigger immediate expiration?
* [ ] **LRU Refresh on Semantic Hit**: If a cached item is retrieved via semantic similarity (not exact match), is its LRU status correctly refreshed?

## Code Quality & Design (20%)
* [ ] **Time Abstraction**: Are time lookups abstracted or injected (e.g., passing `current_time`) to allow deterministic unit testing?
* [ ] **Data Structure Efficiency**: Is an ordered structure (like `OrderedDict`) used to make LRU operations $O(1)$ rather than manually shifting list indices?
