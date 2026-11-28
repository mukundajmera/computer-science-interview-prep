"""
Vector Store & Inverted Index - v2-extended.

A deliberate step up from ``v1-basic/vector_store.py``. It keeps the v1 public
API names (``VectorEntry``, ``cosine_similarity``, ``InMemoryVectorStore`` with
``add_vector`` / ``delete_vector`` / ``query_similarity`` /
``approximate_search``) and the v1 default traversal semantics, while
implementing three improvements that the project's own documents name:

1. **Graph repair on delete** (PITFALLS 1: "Graph Partitions Under Node
   Deletion"). v1's ``delete_vector`` severs links without re-wiring, which
   partitions the single-layer graph, and it can even leave *dangling*
   references to the deleted id in asymmetric adjacency lists (a node whose
   back-link was blocked by the M cap), which later crashes the greedy walk
   with a KeyError. v2 removes the deleted id from every adjacency list and
   re-links each former neighbor to its nearest remaining vector (capacity
   permitting), a simple deterministic healing heuristic that keeps the graph
   connected in the documented counterexample.

2. **Recall controls for approximate search** (PITFALLS 2: filter degradation
   and greedy local optima). ``approximate_search`` accepts an ``ef_search``
   exploration budget: while the budget lasts, neighbors are queued even when
   the v1 early-stop condition would prune them, so the walk escapes local
   optima. With ``strict_recall=True`` and a ``filter_meta`` that the walk
   under-fills, the search falls back to a pre-filtered exact scan, trading
   latency for guaranteed filtered recall.

3. **Thread safety and input hardening** (the in-memory store is meant to be
   shared). All public operations are serialized under an ``RLock``; the
   constructor validates ``dimension`` and ``M``; re-adding an existing id
   replaces the entry cleanly instead of duplicating adjacency links as v1
   does.

Standard library only. Python 3.8 compatible. The v1 simulation boundaries
still apply: no real HNSW hierarchy, no compression, no multi-tenant
isolation (APPROACH.md section 2).
"""

import heapq
import math
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class VectorEntry:
    """One stored embedding: unique id, raw float vector, filter metadata."""
    id: str
    vector: List[float]
    metadata: Dict[str, Any]


def cosine_similarity(v1: List[float], v2: List[float], eps: float = 1e-9) -> float:
    """
    Cosine similarity between two equal-length vectors.

    Identical formula to v1 (including the eps placement) so results are
    comparable across versions. O(d) time. Zero-norm vectors return 0.0.
    """
    if len(v1) != len(v2):
        raise ValueError("Dimensions do not match.")
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2 + eps)


class InMemoryVectorStore:
    """
    In-memory vector store with a single-layer NSW-style adjacency graph.

    v2 adds graph repair on delete, an ef_search exploration budget and
    strict_recall exact fallback for filtered approximate search, and RLock
    serialization for concurrent use. Insertion and default traversal match
    v1 semantics exactly.
    """

    def __init__(self, dimension: int, M: int = 5):
        """Validates configuration and initializes empty storage. O(1)."""
        if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
            raise ValueError("dimension must be a positive integer.")
        if not isinstance(M, int) or isinstance(M, bool) or M <= 0:
            raise ValueError("M must be a positive integer.")
        self.dimension = dimension
        self.vectors: Dict[str, VectorEntry] = {}
        # HNSW-inspired graph layer for approximate nearest neighbors
        self.graph: Dict[str, List[str]] = {}
        self.M = M
        self.entry_point: Optional[str] = None
        self._lock = threading.RLock()

    def add_vector(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """
        Inserts (or cleanly replaces) a vector and links it to its M nearest
        neighbors. O(N * d) for the neighbor scan.
        """
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension must be {self.dimension}.")

        with self._lock:
            if id in self.vectors:
                # v2: replacing an id removes its old links first, so no
                # duplicate or stale adjacency entries survive.
                for neighbors in self.graph.values():
                    while id in neighbors:
                        neighbors.remove(id)
                self.graph[id] = []

            new_entry = VectorEntry(id=id, vector=vector, metadata=metadata)
            self.vectors[id] = new_entry
            self.graph.setdefault(id, [])

            if self.entry_point is None:
                self.entry_point = id
                return

            # Connect to nearest neighbors for the HNSW-inspired graph
            neighbors = self.query_similarity(vector, top_k=self.M)

            for neighbor_entry, _ in neighbors:
                neighbor_id = neighbor_entry.id
                if neighbor_id != id and neighbor_id not in self.graph[id]:
                    self.graph[id].append(neighbor_id)
                    if len(self.graph[neighbor_id]) < self.M and id not in self.graph[neighbor_id]:
                        self.graph[neighbor_id].append(id)

    def delete_vector(self, id: str) -> bool:
        """
        Removes a vector, cleans every dangling reference to it, and heals the
        graph by re-linking each former neighbor to its nearest remaining
        vector (capacity permitting). O(N * M + degree * N * d).
        """
        with self._lock:
            if id not in self.vectors:
                return False

            del self.vectors[id]
            former_neighbors = [n for n in self.graph.pop(id, []) if n in self.graph]

            # v1 only removed id from its mutual neighbors, leaving dangling
            # references in asymmetric lists; v2 scrubs every list.
            for neighbors in self.graph.values():
                while id in neighbors:
                    neighbors.remove(id)

            # Healing heuristic (PITFALLS 1): bridge the gap left by the
            # deleted node so its former neighbors stay connected.
            for neighbor_id in former_neighbors:
                if len(self.graph[neighbor_id]) >= self.M:
                    continue
                nearest = self._nearest_remaining(neighbor_id)
                if nearest is not None:
                    self.graph[neighbor_id].append(nearest)
                    if len(self.graph[nearest]) < self.M and neighbor_id not in self.graph[nearest]:
                        self.graph[nearest].append(neighbor_id)

            if self.entry_point == id:
                if self.vectors:
                    self.entry_point = next(iter(self.vectors.keys()))
                else:
                    self.entry_point = None

            return True

    def _nearest_remaining(self, id: str) -> Optional[str]:
        """
        Nearest other stored vector to ``id`` by cosine similarity, excluding
        ids already adjacent to it. Deterministic tie-break on id. O(N * d).
        """
        source = self.vectors[id]
        already_linked = set(self.graph.get(id, []))
        best_id: Optional[str] = None
        best_sim = float("-inf")
        for other_id in sorted(self.vectors.keys()):
            if other_id == id or other_id in already_linked:
                continue
            sim = cosine_similarity(source.vector, self.vectors[other_id].vector)
            if sim > best_sim:
                best_sim = sim
                best_id = other_id
        return best_id

    def query_similarity(self, query_vector: List[float], top_k: int = 5,
                         filter_meta: Optional[Dict[str, Any]] = None) -> List[Tuple[VectorEntry, float]]:
        """
        Brute-force exact KNN scan with metadata pre-filtering.

        O(N * d + N log K); guarantees 100% recall.
        """
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension must be {self.dimension}.")

        with self._lock:
            results = []
            for entry in list(self.vectors.values()):
                if filter_meta:
                    match = True
                    for k, v in filter_meta.items():
                        if entry.metadata.get(k) != v:
                            match = False
                            break
                    if not match:
                        continue

                sim = cosine_similarity(query_vector, entry.vector)
                results.append((sim, entry))

            # Exact KNN scan using heapq.nlargest for O(N log K)
            top_results = heapq.nlargest(top_k, results, key=lambda x: x[0])
            return [(entry, sim) for sim, entry in top_results]

    def approximate_search(self, query_vector: List[float], top_k: int = 5,
                           filter_meta: Optional[Dict[str, Any]] = None,
                           ef_search: Optional[int] = None,
                           strict_recall: bool = False) -> List[Tuple[VectorEntry, float]]:
        """
        Greedy walk over the HNSW-inspired single-layer graph.

        With ``ef_search=None`` the traversal is exactly the v1 walk. When
        ``ef_search`` is set, at least that many node expansions are performed:
        while the budget lasts, neighbors are queued even when the v1 pruning
        rule would skip them, which escapes greedy local optima. When
        ``strict_recall`` is set and a metadata filter leaves fewer than
        ``top_k`` results, the result is completed with a pre-filtered exact
        scan (PITFALLS 2). Average O(ef_search * M * d) for the walk.
        """
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension must be {self.dimension}.")
        if ef_search is not None and ef_search <= 0:
            raise ValueError("ef_search must be a positive integer when set.")

        with self._lock:
            if self.entry_point is None:
                return []

            visited = {self.entry_point}
            candidates: List[Tuple[float, str]] = []

            entry_sim = cosine_similarity(query_vector, self.vectors[self.entry_point].vector)
            heapq.heappush(candidates, (-entry_sim, self.entry_point))

            best_results: List[Tuple[float, VectorEntry]] = []
            expansions = 0

            while candidates:
                neg_sim, current_id = heapq.heappop(candidates)
                current_sim = -neg_sim
                expansions += 1
                entry = self.vectors[current_id]

                # Check filter
                match = True
                if filter_meta:
                    for k, v in filter_meta.items():
                        if entry.metadata.get(k) != v:
                            match = False
                            break
                if match:
                    best_results.append((current_sim, entry))
                    best_results.sort(key=lambda x: x[0], reverse=True)
                    if len(best_results) > top_k:
                        best_results.pop()

                budget_open = ef_search is not None and expansions < ef_search
                if (len(best_results) == top_k
                        and current_sim < best_results[-1][0]
                        and not budget_open):
                    break

                for neighbor_id in self.graph.get(current_id, []):
                    if neighbor_id in visited or neighbor_id not in self.vectors:
                        continue
                    visited.add(neighbor_id)
                    neighbor_entry = self.vectors[neighbor_id]
                    sim = cosine_similarity(query_vector, neighbor_entry.vector)

                    if budget_open or len(best_results) < top_k or sim > best_results[-1][0]:
                        heapq.heappush(candidates, (-sim, neighbor_id))

            if strict_recall and filter_meta and len(best_results) < top_k:
                # v2 fallback (PITFALLS 2): complete under-filled filtered
                # results with a pre-filtered exact scan.
                have = {entry.id for _, entry in best_results}
                for entry in self.vectors.values():
                    if entry.id in have:
                        continue
                    match = True
                    for k, v in filter_meta.items():
                        if entry.metadata.get(k) != v:
                            match = False
                            break
                    if match:
                        sim = cosine_similarity(query_vector, entry.vector)
                        best_results.append((sim, entry))
                best_results.sort(key=lambda x: x[0], reverse=True)
                best_results = best_results[:top_k]

            return [(entry, sim) for sim, entry in best_results]
