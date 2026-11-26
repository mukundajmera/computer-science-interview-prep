# RAG and Vector DB Quiz

4 questions covering chunking strategies and semantic boundaries.

### Question 1
Which chunking strategy is most appropriate for processing structured but lengthy financial reports (like 10-Ks) to ensure a complete paragraph isn't split mid-sentence?

A) Byte-level chunking at every 1024 bytes
B) Fixed-size chunking of 512 tokens with 0 overlap
C) Token-based chunking matching the embedding model's max context
D) Recursive character splitting with sentence boundary awareness



### Question 2
When scaling a Vector Database for a RAG system to handle over a billion high-dimensional embeddings under strict memory constraints, which indexing strategy provides the best trade-off by significantly reducing RAM usage while maintaining acceptable retrieval latency?

A) Flat Exact Nearest Neighbor (k-NN) scan
B) HNSW (Hierarchical Navigable Small World) without quantization
C) IVF-PQ (Inverted File with Product Quantization)
D) Traditional B-Tree with sparse BM25 indices


### Question 3
When optimizing a RAG system for queries that contain both domain-specific acronyms (requiring exact keyword matching) and broad conceptual questions (requiring semantic understanding), which retrieval pipeline design provides the most effective trade-off between recall and precision?

A) Pure dense retrieval using a high-dimensional sentence transformer model
B) Pure sparse retrieval (BM25) over the entire document corpus
C) Hybrid search combining sparse (BM25) and dense embeddings, followed by a cross-encoder re-ranking step
D) Running dense retrieval first and only falling back to sparse retrieval if zero semantic results are found

### Question 4
When designing a Vector DB schema for multi-tenant SaaS applications, which isolation strategy provides the strictest data separation to prevent cross-tenant leakage while minimizing the operational overhead of managing numerous index clusters?

A) Storing all tenants in a single global index with metadata filtering applied at query time
B) Creating a separate dedicated physical index cluster for each individual tenant
C) Utilizing namespace-level or collection-level isolation within a single shared cluster
D) Hashing tenant IDs directly into the vector embeddings
