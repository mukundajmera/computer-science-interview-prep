import time
import math
import hashlib
from collections import OrderedDict
from typing import List, Dict, Optional, Tuple, Any

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Computes the cosine similarity between two vectors.
    
    Complexity: O(D) where D is the dimensionality of the vectors.
    
    Raises:
        ValueError: If the vectors have different lengths or are empty.
    """
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same length")
    if not v1 or not v2:
        raise ValueError("Vectors cannot be empty")
    
    dot_prod = sum(a * b for a, b in zip(v1, v2))
    norm_1 = math.sqrt(sum(a * a for a in v1))
    norm_2 = math.sqrt(sum(b * b for b in v2))
    
    if norm_1 == 0 or norm_2 == 0:
        return 0.0
        
    return dot_prod / (norm_1 * norm_2)

def compute_hash(query: str) -> str:
    """
    Computes a SHA-256 hash for a given string query.
    
    Complexity: O(K) where K is the length of the string query.
    """
    encoded_query = query.encode('utf-8')
    return hashlib.sha256(encoded_query).hexdigest()

class CacheEntry:
    """
    Represents a single entry in the semantic cache.
    Stores the original query, its vector embedding, the generated response,
    and the absolute expiration time.
    """
    def __init__(self, query: str, embedding: List[float], response: Any, expiration_time: float) -> None:
        """
        Initializes a new cache entry.
        
        Complexity: O(1)
        """
        self.query = query
        self.embedding = embedding
        self.response = response
        self.expiration_time = expiration_time

    def is_expired(self, current_time: float) -> bool:
        """
        Checks if the cache entry has expired based on the current time.
        
        Complexity: O(1)
        """
        return current_time > self.expiration_time

class TenantCache:
    """
    A dedicated cache for a single tenant, ensuring absolute isolation.
    Uses an OrderedDict to provide O(1) exact match lookups and ordered
    sequence for LRU eviction.
    """
    def __init__(self, capacity: int, tau: float) -> None:
        """
        Initializes the TenantCache.
        
        Complexity: O(1)
        """
        self.capacity = capacity
        self.tau = tau
        # Exact match cache: hash(query) -> CacheEntry
        self.exact_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
    def _evict_if_needed(self) -> None:
        """
        Evicts the oldest entry if capacity is exceeded.
        
        Complexity: O(1) amortized.
        """
        while len(self.exact_cache) > self.capacity:
            self.exact_cache.popitem(last=False)

    def _cleanup_expired(self, current_time: float) -> None:
        """
        Removes all expired entries from the cache.
        
        Complexity: O(N) where N is the number of cache entries.
        """
        expired_keys = [key for key, entry in self.exact_cache.items() if entry.is_expired(current_time)]
        for key in expired_keys:
            del self.exact_cache[key]
            
    def put(self, query: str, embedding: List[float], response: Any, ttl_seconds: float, current_time: float) -> None:
        """
        Inserts a new cache entry or updates an existing exact match.
        
        Complexity: O(K) where K is the length of the string to compute hash.
        Eviction is O(1) amortized.
        """
        self._cleanup_expired(current_time)
        q_hash = compute_hash(query)
        exp_time = current_time + ttl_seconds
        
        if q_hash in self.exact_cache:
            del self.exact_cache[q_hash]
        
        new_entry = CacheEntry(query, embedding, response, exp_time)
        self.exact_cache[q_hash] = new_entry
        self._evict_if_needed()

    def get(self, query: str, embedding: List[float], current_time: float) -> Optional[Any]:
        """
        Retrieves a cached response if an exact or semantic match is found.
        
        Complexity: 
        - O(1) for exact match lookup.
        - O(N * D) for semantic match, where N is the number of valid entries 
          and D is the dimensionality of embeddings.
        """
        self._cleanup_expired(current_time)
        
        q_hash = compute_hash(query)
        if q_hash in self.exact_cache:
            entry = self.exact_cache[q_hash]
            if not entry.is_expired(current_time):
                self.exact_cache.move_to_end(q_hash)
                return entry.response
                
        best_key: Optional[str] = None
        best_sim = -1.0
        
        for key, entry in self.exact_cache.items():
            if not entry.is_expired(current_time):
                sim = cosine_similarity(embedding, entry.embedding)
                if sim >= self.tau and sim > best_sim:
                    best_sim = sim
                    best_key = key
                
        if best_key is not None:
            self.exact_cache.move_to_end(best_key)
            return self.exact_cache[best_key].response
            
        return None

class SemanticCache:
    """
    Orchestrator for the Semantic Cache.
    Routes queries to the appropriate TenantCache ensuring namespace isolation.
    
    Architecture is scoped as a single microcomponent with model/provider-independent interfaces.
    Unsupported guarantees regarding production safety, tokenization, and embeddings.
    """
    def __init__(self, capacity: int = 1000, tau: float = 0.90) -> None:
        """
        Initializes the SemanticCache orchestrator.
        
        Complexity: O(1)
        """
        self.capacity = capacity
        self.tau = tau
        self.namespaces: Dict[str, TenantCache] = {}

    def _get_tenant_cache(self, tenant_id: str) -> TenantCache:
        """
        Retrieves or creates a TenantCache for the given tenant ID.
        
        Complexity: O(1) amortized.
        """
        if tenant_id not in self.namespaces:
            self.namespaces[tenant_id] = TenantCache(self.capacity, self.tau)
        return self.namespaces[tenant_id]

    def put(self, tenant_id: str, query: str, embedding: List[float], response: Any, ttl_seconds: float = 3600.0, current_time: Optional[float] = None) -> None:
        """
        Routes the put request to the specific tenant's cache.
        
        Complexity: O(K) where K is the length of the string to compute hash.
        Eviction is O(1) amortized.
        
        Raises:
            ValueError: If the query string or embedding vector is empty.
        """
        if not query:
            raise ValueError("Query string cannot be empty")
        if not embedding:
            raise ValueError("Embedding vector cannot be empty")
            
        if current_time is None:
            active_time = time.time()
        else:
            active_time = current_time
        target_cache = self._get_tenant_cache(tenant_id)
        target_cache.put(query, embedding, response, ttl_seconds, active_time)

    def get(self, tenant_id: str, query: str, embedding: List[float], current_time: Optional[float] = None) -> Optional[Any]:
        """
        Routes the get request to the specific tenant's cache.
        
        Complexity: O(N * D) for semantic match, O(1) for exact match lookup.
        
        Raises:
            ValueError: If the query string or embedding vector is empty.
        """
        if not query:
            raise ValueError("Query string cannot be empty")
        if not embedding:
            raise ValueError("Embedding vector cannot be empty")
            
        if current_time is None:
            active_time = time.time()
        else:
            active_time = current_time
            
        if tenant_id not in self.namespaces:
            return None
            
        target_cache = self._get_tenant_cache(tenant_id)
        return target_cache.get(query, embedding, active_time)
