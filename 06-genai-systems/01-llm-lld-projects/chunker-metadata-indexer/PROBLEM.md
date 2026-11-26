# Chunker–Metadata–Indexer Pipeline

## Problem Statement

Design a document ingestion pipeline that splits raw text into retrieval-friendly chunks, extracts metadata for each chunk, and stores chunk–embedding pairs in a pluggable index backend. The system should be extensible enough that new chunking strategies and embedding index backends can be added without modifying existing code.

---

## Functional Requirements

1. **Multiple Chunking Strategies**: Support fixed-size, sentence-based, and paragraph-based chunking
2. **Configurable Overlap**: Allow chunk overlap (in characters) to preserve context across boundaries
3. **Metadata Extraction**: Automatically tag every chunk with positional info, source document reference, word count, character count, and custom key-value tags
4. **Index Abstraction**: Provide a backend-agnostic index interface with `add`, `search`, and `delete` operations
5. **In-Memory Backend**: Ship a default in-memory index that performs brute-force cosine-similarity search
6. **Pipeline Orchestration**: Expose a single entry point that accepts a document and produces indexed, metadata-tagged chunks
7. **Deterministic Chunking**: Given the same document and strategy configuration, produce identical chunks every run

---

## Non-Functional Requirements

1. **Extensibility**: Adding a new chunking strategy or index backend must not require changes to existing classes (Open/Closed Principle)
2. **Stateless Chunking**: The chunking pipeline itself must be stateless — all state lives in the index
3. **Performance**: Chunking and metadata extraction should be O(n) in document length
4. **Testability**: Every component must be independently unit-testable
5. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively

---

## Constraints & Assumptions

- Input documents are plain UTF-8 text (no binary formats)
- Embeddings are represented as `List[float]` — the system does **not** generate real embeddings; callers supply them or a stub is used
- Chunk IDs are UUID-based and globally unique
- Overlap is specified in characters and must be less than chunk size
- Sentence detection uses a simple heuristic (`.`, `!`, `?` followed by whitespace) — not a full NLP tokenizer
- The in-memory index uses brute-force cosine similarity; production backends (FAISS, Pinecone, etc.) are out of scope for v1

---

## Sample Interactions

```
1. Caller creates a Document(text="...", source="report.pdf")
2. Caller selects a ChunkingStrategy (e.g., FixedSizeChunker(chunk_size=200, overlap=50))
3. DocumentChunker.chunk(document) → List[Chunk]
4. MetadataExtractor.extract(chunks, document) → List[Chunk] (now metadata-enriched)
5. For each chunk, caller (or pipeline) generates an embedding vector
6. IndexBackend.add(chunk, embedding) stores the pair
7. IndexBackend.search(query_embedding, top_k=5) → ranked list of results
8. IndexBackend.delete(chunk_id) removes a single entry
```

---

## Clarifying Questions to Ask

1. "What is the expected average document length?"
2. "Should chunking preserve word boundaries, or is mid-word splitting acceptable?"
3. "Do we need to support overlapping metadata across chunks (e.g., shared headings)?"
4. "What embedding dimensionality should the index expect?"
5. "Is real-time incremental indexing required, or batch-only?"
6. "Should the index support filtered search (e.g., by metadata tag)?"
7. "Do we need persistence, or is in-memory sufficient for the interview scope?"
8. "How should very short documents (shorter than chunk size) be handled?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| Document | Raw input text with source metadata |
| Chunk | A slice of a document with ID and position info |
| ChunkingStrategy | Algorithm for splitting a document into chunks |
| DocumentChunker | Orchestrator that applies a strategy to a document |
| MetadataTag | Key-value pair attached to a chunk |
| MetadataExtractor | Derives and attaches metadata to chunks |
| IndexBackend | Abstract store for chunk–embedding pairs |
| IndexEntry | A single record in the index (chunk + embedding) |
| InMemoryIndex | Brute-force in-memory implementation of IndexBackend |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core chunking strategies, metadata extraction, in-memory index with cosine search |
| v2-extended | Filtered search by metadata, batch indexing, token-aware chunking, pipeline class |
| v3-optimized | Approximate nearest-neighbor index stub, async pipeline, embedding cache, persistence adapter |
