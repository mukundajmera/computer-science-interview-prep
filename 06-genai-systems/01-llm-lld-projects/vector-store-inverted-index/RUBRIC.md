# Vector Store & Inverted Index: Evaluation Rubric

This rubric evaluates the actual, verified implementation of the `InMemoryVectorStore` provided in the codebase.

## 1. Similarity Math (Cosine Similarity)
*   **Dimensions Mismatch Invariant**: Validates `len(v1) == len(v2)` and raises `ValueError` if violated.
*   **Zero-Length Magnitude Invariant**: Correctly checks `if norm_v1 == 0 or norm_v2 == 0:` returning `0.0` instead of division by zero.
*   **Dimensions Mismatch Invariant**: Validates `len(v1) == len(v2)` and raises `ValueError` if violated.
*   **Zero-Length Magnitude Invariant**: Correctly checks `if norm_v1 == 0 or norm_v2 == 0:` returning `0.0` instead of division by zero.
*   **Dimensions Mismatch Invariant**: Validates `len(v1) == len(v2)` and raises `ValueError` if violated.
*   **Zero-Length Magnitude Invariant**: Correctly checks `if norm_v1 == 0 or norm_v2 == 0:` returning `0.0` instead of division by zero.
*   **Dimensions Mismatch Invariant**: Validates `len(v1) == len(v2)` and raises `ValueError` if violated.
*   **Zero-Length Magnitude Invariant**: Correctly checks `if norm_v1 == 0 or norm_v2 == 0:` returning `0.0` instead of division by zero.
The core metric for semantic closeness is `cosine_similarity(v1, v2)`. 
*   **Correctness Invariant**: The function must correctly validate dimensions, compute the unnormalized dot product, compute the Euclidean norm for both vectors, and return the normalized similarity: `dot_product / (norm_v1 * norm_v2 + eps)`.
*   **Failure Handling**: If the dimensions of `v1` and `v2` mismatch, it strictly raises a `ValueError("Dimensions do not match.")`.
*   **Edge Cases**: Zero-length or zero-magnitude vectors correctly return `0.0` rather than causing a division-by-zero, thanks to the explicit `if norm_v1 == 0 or norm_v2 == 0: return 0.0` check and the `eps=1e-9` constant padding the denominator.

## 2. Graph Connectivity (HNSW-inspired Single Layer)
The structural integrity of the Navigable Small World relies on correct edge formations.
*   **Correctness Invariant**: When `add_vector` runs, if the graph is empty, it assigns itself as the `entry_point`. If not, it executes an exact KNN search (`query_similarity`) to find its `M` closest neighbors. 
*   **Bidirectionality**: It correctly forms bidirectional edges: the new node points to the neighbor, and if the neighbor has `< M` connections, it points back to the new node (`if len(self.graph[neighbor_id]) < self.M: self.graph[neighbor_id].append(id)`).

## 3. Filtering Semantics
Metadata filtering works mechanically differently depending on the search type.
*   **Exact Search (Pre-filter)**: In `query_similarity`, filtering acts strictly as a pre-filter. A node is evaluated against `filter_meta`, and if it fails, the computation `continue`s, avoiding the expensive similarity math completely.
*   **Approximate Search (In-traversal)**: In `approximate_search`, filtering happens during traversal. Because the graph must be navigated based on spatial closeness, similarity math *must* be calculated to reach neighbors. Nodes that fail the `filter_meta` check are simply skipped when accumulating `best_results`, but their edges are still used to explore.

## 4. Memory Profiling
Because this is an `InMemoryVectorStore`, data structure choices dictate capacity.
*   **Storage Profiles**: The `self.vectors` dictionary stores raw `VectorEntry` dataclasses containing string IDs, metadata dicts, and raw float lists. `self.graph` maintains adjacency lists as arrays of string IDs.
*   **Limitations**: This Python structure lacks memory optimization. Millions of high-dimensional vectors will consume gigabytes of RAM. *(Note: Advanced memory profiling like quantization is an unimplemented extension).*

*Note: This rubric applies strictly to the exact dimensions mismatch invariant and zero-length magnitude failure cases implemented in both Java and Python.*
