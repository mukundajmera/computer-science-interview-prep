# Embedding Service - Follow-Up Questions

## Follow-up questions
1. How would you handle dynamic batching with timeout windows to maximize GPU throughput?
2. How do you handle quantization (e.g. float32 to int8 or binary embeddings) to reduce cache size?
3. How would you route embedding requests across multiple regional model endpoints for high availability?
4. How do you handle dimensional projection (e.g. Matryoshka embeddings)?
5. How would you detect embedding drift when updating the underlying model?

## Variants and extensions
- Multi-modal embeddings (CLIP image + text).
- Distributed cache backends (Redis vector cache).
- Matryoshka 2D truncation.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
