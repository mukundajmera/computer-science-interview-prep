# Retriever-Ranker - Common Pitfalls

## Common pitfalls
1. **Coupling to Specific Vector DBs:** Implementing retrieval logic with hard dependencies on specific vector database SDKs (like Pinecone or Qdrant) instead of defining standard abstractions.
2. **Ignoring Score Normalization:** Failing to normalize scores from dense and sparse retrievers before combining them, resulting in one method dominating the hybrid score (e.g., dense cosine similarity 0-1 range vs sparse TF-IDF open-ended scores).
3. **No Reciprocal Rank Fusion (RRF):** Adding scores naively across different retrieval algorithms instead of using robust methods like Reciprocal Rank Fusion when absolute scores are incompatible or uncalibrated.
4. **Poor Deduplication Logic:** Returning the same document multiple times from different retrievers (e.g., dense and sparse) because chunk IDs are not merged correctly before ranking.
5. **Inefficient Ranking:** Sorting the entire retrieval corpus instead of using O(N log K) heap-select approaches for top-k elements, leading to performance degradation on large retrieval sets.
6. **Violating SRP in Orchestration:** Mixing the orchestrating pipeline, retriever fetching logic, and ranker ordering logic into a single monolithic class.

## Why these fail interviews
- **Breaks Open/Closed Principle:** If a new retrieval source or reranker strategy requires modifying existing class methods rather than plugging in a new subclass, extensibility is lost.
- **Incorrect Results:** Poor score normalization and deduplication directly degrade the end quality of RAG (Retrieval-Augmented Generation) pipelines, as irrelevant or duplicated context will be passed to the LLM.
- **Poor Performance:** O(N log N) sorting for top-K instead of O(N log K) reveals a lack of fundamental algorithmic scaling awareness in a system meant to process potentially large volumes of candidate documents.

## Mitigations
- **Use Strategy Pattern:** Define `Retriever` and `Ranker` ABCs/interfaces. Pass implementations to a `RetrievalPipeline`.
- **Implement RRF:** If merging incompatible scores, use Reciprocal Rank Fusion ($1 / (k + rank)$) to merge based on position rather than raw score.
- **Proper Normalization:** If blending scores (e.g., $\alpha \cdot dense\_score + (1-\alpha) \cdot sparse\_score$), scale both sets of scores to [0.0, 1.0] using min-max normalization before blending.
- **Merge by ID:** Store retrieved results in a dictionary/map keyed by `chunk_id` during the hybrid aggregation phase to naturally handle deduplication, then sum or blend scores.
- **Top-K Efficiency:** Use `heapq.nlargest` (Python) or `PriorityQueue` (Java) to efficiently extract the top-K elements without full sorts.

## Cross-links
- [GenAI Top Interview Pitfalls](../../PITFALLS.md)
- [GenAI Design Patterns](../../00-concepts/genai-design-patterns/README.md)
