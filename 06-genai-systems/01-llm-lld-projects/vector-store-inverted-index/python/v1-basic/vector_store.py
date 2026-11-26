import math
import heapq
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class VectorEntry:
    id: str
    vector: List[float]
    metadata: Dict[str, Any]

def cosine_similarity(v1: List[float], v2: List[float], eps: float = 1e-9) -> float:
    if len(v1) != len(v2):
        raise ValueError("Dimensions do not match.")
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2 + eps)

class InMemoryVectorStore:
    def __init__(self, dimension: int, M: int = 5):
        self.dimension = dimension
        self.vectors: Dict[str, VectorEntry] = {}
        # HNSW-inspired graph layer for approximate nearest neighbors
        self.graph: Dict[str, List[str]] = {}
        self.M = M
        self.entry_point: Optional[str] = None

    def add_vector(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension must be {self.dimension}.")
            
        new_entry = VectorEntry(id=id, vector=vector, metadata=metadata)
        self.vectors[id] = new_entry
        self.graph[id] = []
        
        if self.entry_point is None:
            self.entry_point = id
            return
            
        # Connect to nearest neighbors for the HNSW-inspired graph
        neighbors = self.query_similarity(vector, top_k=self.M)
        
        for neighbor_entry, _ in neighbors:
            neighbor_id = neighbor_entry.id
            if neighbor_id != id:
                self.graph[id].append(neighbor_id)
                if len(self.graph[neighbor_id]) < self.M:
                    self.graph[neighbor_id].append(id)

    def delete_vector(self, id: str) -> bool:
        if id not in self.vectors:
            return False
            
        del self.vectors[id]
        
        if id in self.graph:
            neighbors = self.graph.pop(id)
            for neighbor in neighbors:
                if neighbor in self.graph and id in self.graph[neighbor]:
                    self.graph[neighbor].remove(id)
                    
        if self.entry_point == id:
            if self.vectors:
                self.entry_point = next(iter(self.vectors.keys()))
            else:
                self.entry_point = None
                
        return True

    def query_similarity(self, query_vector: List[float], top_k: int = 5, filter_meta: Optional[Dict[str, Any]] = None) -> List[Tuple[VectorEntry, float]]:
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension must be {self.dimension}.")
            
        results = []
        for entry in self.vectors.values():
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

    def approximate_search(self, query_vector: List[float], top_k: int = 5, filter_meta: Optional[Dict[str, Any]] = None) -> List[Tuple[VectorEntry, float]]:
        """HNSW-inspired graph layer for approximate nearest neighbors."""
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension must be {self.dimension}.")
            
        if self.entry_point is None:
            return []
            
        visited = {self.entry_point}
        candidates = []
        
        entry_sim = cosine_similarity(query_vector, self.vectors[self.entry_point].vector)
        heapq.heappush(candidates, (-entry_sim, self.entry_point))
        
        best_results = []
        
        while candidates:
            neg_sim, current_id = heapq.heappop(candidates)
            current_sim = -neg_sim
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
                    
            if len(best_results) == top_k and current_sim < best_results[-1][0]:
                break
                
            for neighbor_id in self.graph.get(current_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    neighbor_entry = self.vectors[neighbor_id]
                    sim = cosine_similarity(query_vector, neighbor_entry.vector)
                    
                    if len(best_results) < top_k or sim > best_results[-1][0]:
                        heapq.heappush(candidates, (-sim, neighbor_id))
                        
        return [(entry, sim) for sim, entry in best_results]
