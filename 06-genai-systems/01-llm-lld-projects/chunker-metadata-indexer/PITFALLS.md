# Chunker-Metadata-Indexer Pipeline - Common Pitfalls

## Common pitfalls
1. **O(N^2) string slicing during chunking:** Repeatedly concatenating or slicing very large strings incorrectly can lead to quadratic time complexity instead of the required O(n).
2. **Incorrect overlap logic:** Mishandling chunk overlaps, leading to either missing characters, infinite loops (if step size becomes zero or negative), or duplicating chunks indefinitely.
3. **Coupling chunking with embedding generation or indexing:** Putting the embedding model call directly inside the `DocumentChunker` or `ChunkingStrategy`, making it impossible to unit-test chunking without an LLM or embedding API.
4. **Stateful Chunking Strategies:** Storing document-specific state (like current position or document text) inside a shared `ChunkingStrategy` instance, making it unsafe for concurrent processing.
5. **Brittle Metadata Extraction:** Hardcoding metadata keys or logic into the chunking loop rather than using an independent, extensible `MetadataExtractor` component.
6. **Failing to handle edge cases:** Such as documents shorter than the chunk size, overlap being larger than the chunk size, or documents with no natural boundaries (e.g., extremely long strings without punctuation in a sentence-based chunker).

## Why these fail interviews
- **Breaks Non-Functional Requirements:** O(n) performance and stateless chunking are explicit requirements. Violating them shows a lack of attention to system constraints.
- **Violates Single Responsibility Principle (SRP):** Tightly coupling chunking, extraction, and embedding breaks extensibility (Open/Closed Principle) and makes the system hard to test and maintain.
- **Causes Production Bugs:** Incorrect overlap logic or stateful strategies will lead to data corruption, duplicated embeddings, and memory leaks in a real-world pipeline.

## Mitigations
- **Use pointers/indices:** Implement chunking by moving `start` and `end` indices over the text instead of repeatedly modifying strings. Slice only when yielding the final chunk.
- **Validate configuration early:** Ensure `overlap < chunk_size` in the strategy constructor and throw an exception if invalid.
- **Keep strategies stateless:** The `chunk` method should take the document as input, process it, and return chunks. Do not store the document or intermediate state on `self`.
- **Use the Strategy Pattern:** Isolate the chunking algorithm behind an interface (`ChunkingStrategy`). Similarly, separate metadata extraction into its own class (`MetadataExtractor`).
- **Pass embeddings explicitly:** Design the index backend to accept a chunk and an embedding separately, or use a dependency-injected interface to fetch embeddings, avoiding direct API calls in the chunking logic.

## Cross-links
- [GenAI Top Interview Pitfalls](../../PITFALLS.md)
- [GenAI Design Patterns](../../00-concepts/genai-design-patterns/README.md)
