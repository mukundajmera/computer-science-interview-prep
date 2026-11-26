## Common pitfalls
1. Missing cache key namespace for different embedding models or dimensions, causing collision bugs.
2. Inefficient batching that embeds all items individually rather than batching cache misses.
3. Floating point zero division when performing L2 normalization on empty or zero vectors.
4. Memory leaks due to unbounded cache growth without eviction or TTL expiration.
5. Inconsistent vector dimensionality across calls if models are swapped without validation.

## Why these fail interviews
- Exposes lack of understanding of high-throughput ML inference bottlenecks.
- Causes silent mathematical corruption (cache key collisions across different vector spaces).

## Mitigations
- Include `(model_name, dimension, text_hash)` in cache keys.
- Deduplicate batch inputs and query cache first, only embedding the delta.
- Check epsilon / zero norm before vector division.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
