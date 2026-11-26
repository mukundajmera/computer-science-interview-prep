# Retriever-Ranker - Follow-Up Questions

## Follow-up questions
1. How would you handle tied scores across multiple rankers or tied overall scores?
2. If the scale of scores from the dense and sparse retrievers are vastly different, how would you normalize them before combining them with alpha weights?
3. How would you optimize the hybrid retrieval to be faster (e.g., executing dense and sparse retrieval concurrently)?
4. How would you handle the case where a document matches in sparse retrieval but is completely missing from dense retrieval results, or vice-versa?
5. How would you explain the ranking decisions to a user who asks "Why was this result ranked first?"
6. How would you adapt this pipeline to retrieve millions of documents (which can't be held in memory)?
7. How does the pipeline's memory and CPU usage scale with the number of query text tokens or vector dimensions?

## Variants and extensions
1. **Asynchronous Orchestration:** Implement an async pipeline utilizing asyncio/Futures so that dense retrieval and sparse retrieval happen simultaneously.
2. **Dynamic Alpha Weighting:** Determine the alpha weight at runtime based on query characteristics (e.g., mostly keywords vs. full conversational question).
3. **Reciprocal Rank Fusion (RRF):** Implement RRF instead of linear score combination to mitigate uncalibrated raw scores between different retrievers.
4. **Approximate Nearest Neighbors (ANN):** Replace brute force cosine similarity with HNSW or IVF indices for scaled dense retrieval.
5. **Cross-Encoder Re-Ranking:** Instead of simple weight-based or round-robin ranking, pass the top-k results through a heavier cross-encoder LLM model to recalculate relevance scores.

## Interviewer probes to prepare
- "Why use interfaces (abstract classes) for Retrievers and Rankers instead of hardcoding the pipeline steps?"
- "What happens if alpha=0.5 but the dense scores range from 0.8-1.0 while sparse scores range from 0.0-0.2? Does alpha=0.5 actually mean equal weighting in practice?"
- "Why does the RoundRobinRanker interleave results instead of merging them? In what use cases is round robin better than weighted scoring?"
- "How do you ensure the Pipeline remains completely DB-agnostic?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
- [Approach & Patterns](./APPROACH.md)
