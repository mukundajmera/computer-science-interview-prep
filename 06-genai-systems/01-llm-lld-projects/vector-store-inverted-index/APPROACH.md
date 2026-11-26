# Vector Store & Inverted Index: Algorithm Approach

This document analyzes the algorithmic approaches to vector retrieval, grounding the discussion in the actual behavior of the `InMemoryVectorStore` implemented in `vector_store.py`.

## 1. Algorithmic Strategies

Vector databases rely heavily on the balance between search speed and recall accuracy. There are three primary paradigms:

### A. Brute Force Exact KNN (Implemented)
The `query_similarity` / `querySimilarity` method performs a brute-force scan.
*   **Mechanism**: Iterates through all `N` vectors in `self.vectors`, calculating the similarity metric (cosine) between the query and each stored vector.
*   **Complexity**: 
    *   Time: `O(N * d + N log K)`, where `N` is the number of vectors, `d` is the dimension, and `K` is the number of requested neighbors.
    *   Space: `O(N * d)` to store all vectors.
*   **Verdict**: Guarantees perfect recall, but computationally infeasible for datasets larger than a few hundred thousand embeddings.

### B. Graph-Based Approximate Search (Implemented, Single Layer)
The `approximate_search` / `approximateSearch` method implements a greedy walk on a single-layer adjacency graph.
*   **Mechanism**: Starts at `self.entry_point` and greedily explores neighbors using a min-heap to prioritize nodes mathematically closer to the query vector.
*   **Complexity**:
    *   Time: `O(log N * d)` on average for well-connected graphs. The traversal path is logarithmic, and at each step, `d` operations are performed for distance computation.
    *   Space: `O(N * d + N * M)` where `M` is the maximum number of connections per node.
*   **Limitations**: As implemented, deleting nodes (`delete_vector` / `deleteVector`) can partition the graph, isolating clusters of nodes and severely damaging recall since there is no background graph repair.

## 2. Limitations & Privacy Boundaries
*   **Limitations**: 
    *   The single-layer graph can become trapped in local optima during greedy searches.
    *   Node deletion (`delete_vector` / `deleteVector`) does not re-heal graph partitions, risking structural collapse over time.
    *   Memory bound: the system stores raw float lists. A million 1536-dimensional vectors would require several gigabytes of RAM.
*   **Privacy Boundaries**: The implementation provides no multi-tenant isolation or RBAC (Role-Based Access Control). Any caller interacting with the `InMemoryVectorStore` instance has full visibility into all ingested documents and arbitrary metadata. Filtering is purely mechanical, not cryptographic.

