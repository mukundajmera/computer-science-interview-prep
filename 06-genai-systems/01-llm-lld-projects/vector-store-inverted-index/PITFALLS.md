# Vector Store & Inverted Index: Common Pitfalls

Based on the current architecture and mechanics of `InMemoryVectorStore`, engineers must be aware of several critical limitations and operational pitfalls.

## 1. Graph Partitions Under Node Deletion
The single-layer graph is highly fragile to node deletion because the system lacks a background repair or re-wiring mechanism.

### Concrete Counterexample (HNSW Healing Failure) (HNSW Healing Failure) (HNSW Healing Failure) (HNSW Healing Failure)
Consider the implemented `delete_vector(id)` logic:
```python
if id in self.graph:
    neighbors = self.graph.pop(id)
    for neighbor in neighbors:
        if neighbor in self.graph and id in self.graph[neighbor]:
            self.graph[neighbor].remove(id)
```
*   **The Issue**: When Node B is deleted, it removes itself from its neighbors (Node A and Node C). However, it *does not* connect Node A and Node C together to bridge the gap.
*   **The Partition**: If Node B was the only bridge between the cluster containing A and the cluster containing C, the graph splits into two disconnected partitions.
*   **Impact**: Future calls to `approximate_search` starting at an `entry_point` in cluster A will be completely unable to discover vectors in cluster C, silently ruining recall.

## 2. In-Traversal Filter Degradation (Post-filter / In-filter)
Using the `filter_meta` in the `approximate_search` can severely degrade recall due to how the greedy walk operates.

*   **Mechanism**: The search greedily walks towards neighbors that are spatially closest to the query vector. 
*   **The Pitfall**: If a highly restrictive metadata filter is applied, the algorithm may explore nodes, calculate similarity, but reject them from `best_results` due to the filter. It might exhaust its candidate queue without ever finding enough nodes that satisfy the filter, even if valid nodes exist elsewhere in the graph. The greedy nature prevents it from exploring "worse" spatial paths to find "better" metadata matches.

## 3. The Curse of Dimensionality
The system computes distances via `cosine_similarity`. 
*   In low dimensions (e.g., 2D or 3D), space is dense.
*   In high dimensions (e.g., 1536 as output by many LLM embedding models), distance metrics begin to lose their discriminative power. The distance to the nearest neighbor approaches the distance to the farthest neighbor, making the exact KNN scan (`query_similarity`) computationally heavy for diminishing semantic returns. 
*   The raw storage of these float lists in `self.vectors` means memory consumption scales linearly `O(N * d)`, quickly exhausting RAM for large datasets.

*Note: The pitfall outlined above regarding graph partition under node deletion serves as a concrete counterexample to proper HNSW healing mechanics.*
