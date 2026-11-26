# GenAI RAG and Vectors Flashcards

40 question-only flashcards for GenAI RAG, vector databases, and embeddings interview preparation.

Source alignment:
- [RAG Architecture](../06-genai-systems/00-concepts/rag-architecture/)
- [Model Routing & Orchestration](../06-genai-systems/00-concepts/model-routing-orchestration/)
- [Token Economics](../06-genai-systems/00-concepts/token-cost-latency/)
- [Prompting, Tools & Agents](../06-genai-systems/00-concepts/prompting-tools-agents/)
- [Safety, Evaluation & Governance](../06-genai-systems/00-concepts/safety-eval/)
- [GenAI LLD Projects](../06-genai-systems/01-llm-lld-projects/)
- [GenAI HLD Projects](../06-genai-systems/02-llm-hld-projects/)

---

### Card 1
Front: What makes RAG an evidence pipeline rather than just a vector database plus an LLM?

### Card 2
Front: Why might you choose to index a corpus instead of fine-tuning an LLM on the same data?

### Card 3
Front: How does a standard dense retriever match user queries to document chunks?

### Card 4
Front: What is the role of an embedding model in a vector database system?

### Card 5
Front: Why are large chunks sometimes problematic for dense retrieval precision?

### Card 6
Front: How does chunking overlap help mitigate context fragmentation?

### Card 7
Front: What is the difference between sparse retrieval (like BM25) and dense retrieval?

### Card 8
Front: How does Reciprocal Rank Fusion (RRF) combine sparse and dense retrieval results?

### Card 9
Front: Why is Exact Nearest Neighbor (k-NN) search typically too slow for production systems?

### Card 10
Front: What is Approximate Nearest Neighbor (ANN) search, and what trade-off does it make?

### Card 11
Front: In HNSW (Hierarchical Navigable Small World), what does the parameter 'M' control?

### Card 12
Front: In HNSW, what does the parameter 'efConstruction' influence during index building?

### Card 13
Front: How does the 'efSearch' parameter in HNSW affect retrieval at query time?

### Card 14
Front: What is the difference between a bi-encoder and a cross-encoder model?

### Card 15
Front: Why use a cross-encoder for reranking instead of using it for the initial retrieval?

### Card 16
Front: What is the 'lost-in-the-middle' phenomenon in large context windows?

### Card 17
Front: How can document sorting before prompt assembly mitigate lost-in-the-middle effects?

### Card 18
Front: What role does a query router play in a complex RAG system?

### Card 19
Front: How can query rewriting or expansion improve retrieval recall?

### Card 20
Front: What is hypothetical document embeddings (HyDE) and when is it useful?

### Card 21
Front: Why might a vector database use Product Quantization (PQ)?

### Card 22
Front: How does scalar quantization reduce the memory footprint of an embedding index?

### Card 23
Front: What happens when you change your embedding model but don't re-index your documents?

### Card 24
Front: How can metadata filtering improve both the speed and accuracy of vector search?

### Card 25
Front: What is the difference between pre-filtering and post-filtering in vector databases?

### Card 26
Front: What is hybrid search in the context of a vector database?

### Card 27
Front: How do you evaluate the retrieval quality of a RAG pipeline (e.g., using nDCG or MRR)?

### Card 28
Front: What is the role of an LLM-as-a-judge in evaluating RAG generation quality?

### Card 29
Front: What are common techniques to reduce hallucination when the retriever finds irrelevant context?

### Card 30
Front: Why might long-context LLMs not completely eliminate the need for RAG?

### Card 31
Front: How does multi-hop reasoning (e.g., using ReAct or agentic RAG) differ from single-shot RAG?

### Card 32
Front: What is a semantic cache and how does it reduce latency and cost in GenAI applications?

### Card 33
Front: How does the chunk size affect the embedding model's ability to capture specific facts vs. general themes?

### Card 34
Front: What are hierarchical or parent-child chunking strategies?

### Card 35
Front: How does a graph-based RAG system differ from a pure vector-based approach?

### Card 36
Front: What is the impact of embedding dimensionality on storage and search performance?

### Card 37
Front: How can you handle versioning or updates to documents in a live vector database?

### Card 38
Front: What is sparse vector representation (e.g., SPLADE) and how does it compare to dense embeddings?

### Card 39
Front: How does instruction-tuned embedding (like Instructor) differ from standard embeddings?

### Card 40
Front: What are the latency bottlenecks in a standard query-retrieve-rerank-generate pipeline?

