# Chunker–Metadata–Indexer - Follow-Up Questions

## Follow-up questions
1. How would you handle very large documents that don't fit in memory?
2. How would you change your strategy implementation if we switch from fixed-size text chunking to semantic chunking (e.g. splitting by topic changes)?
3. How would you optimize the brute-force O(n) search in `InMemoryIndex` as the number of entries scales to millions?
4. How would you modify the pipeline to handle multi-modal documents, like images or tables mixed with text?
5. How would you handle partial failures during batch indexing?
6. How would you perform filtered search (e.g., matching a metadata tag as well as vector similarity)?

## Variants and extensions
1. **Semantic Chunking:** Implement a chunker that leverages small local LLMs or embeddings to identify semantic boundaries rather than just sentence breaks or character limits.
2. **Token-Aware Chunking:** Implement a `ChunkingStrategy` that chunks based on token count using a specific tokenizer (e.g. tiktoken) rather than character length.
3. **External Index Adapters:** Implement an adapter for a real vector database like FAISS, Pinecone, Qdrant or Milvus.
4. **Hierarchical Indexing:** Implement document summarization before chunking to index at different levels of granularity (e.g. document level, section level, chunk level).

## Interviewer probes to prepare
- "Why use the Strategy pattern for chunking? How does this make testing easier?"
- "How does the Template Method pattern help when implementing new chunking strategies?"
- "What is the memory overhead of storing embeddings in `InMemoryIndex`, and how does this change with dimension `d`?"
- "How do you ensure chunk boundaries don't split important context mid-sentence?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
- [Approach & Patterns](./APPROACH.md)
