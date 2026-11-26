# Chunker–Metadata–Indexer - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies document types, chunking preservation (overlap vs boundaries), embedding dimensionality, and index query semantics. |
| Domain model quality | 20% | Clean separation of `Document`, `Chunk`, `ChunkingStrategy`, `MetadataExtractor`, and `IndexBackend`. |
| Pipeline correctness | 25% | Generates chunks with correct positional metadata, maintains robust overlapping logic, and extracts metadata fully before indexing. |
| Search and index | 25% | Implements accurate brute-force cosine similarity, separates index from chunking, and maintains consistent chunk-to-embedding mappings. |
| Extensibility and communication | 15% | Uses the Strategy pattern for chunking, allows pluggable index backends, and explains transitions from v1 in-memory to v3 production vector DBs. |

## Performance bands
- `1/5`: tightly coupled script that splits text and stores it directly into a list without abstractions or proper overlap logic.
- `3/5`: defines abstractions but leaks state between chunks, uses hard-coded metadata extraction, or struggles with cosine similarity correctness.
- `5/5`: stateless pipeline components, clean Strategy pattern for chunking, precise overlap character math, and O(k*d) deterministic index search.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
