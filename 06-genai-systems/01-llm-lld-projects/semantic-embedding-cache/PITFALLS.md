# Common Pitfalls: Semantic Embedding Cache

### 1. Failing to Refresh LRU on Semantic Hits
Many candidates correctly update the LRU list when an exact match string hash hits, but forget to update the LRU list when an item is retrieved via a vector semantic match.

**Counterexample (Incorrect implementation):**
```python
        if best_match_key:
            # Missing: self.exact_cache.move_to_end(best_match_key)
            return self.exact_cache[best_match_key].response
```

### 2. Returning the First Match instead of the Best Match
When iterating over the cache looking for semantic matches `> tau`, candidates might return immediately upon finding the first match that exceeds the threshold. They should instead scan the entire namespace cache to find the *highest* similarity score that exceeds the threshold.

**Counterexample (Incorrect implementation):**
```python
        for key, entry in self.exact_cache.items():
            if entry.is_expired(current_time):
                continue
                
            sim = cosine_similarity(embedding, entry.embedding)
            if sim >= self.tau:
                return entry.response # Incorrect: returns the first match > tau
```

### 3. Hardcoding `time.time()` inside the class
If the class internalizes `time.time()`, testing the TTL eviction becomes slow and flaky because tests actually have to `sleep()` to verify expiration. Passing `current_time` as a parameter to `get` and `put` is a critical testability pattern.

**Counterexample (Incorrect implementation):**
```python
    def get(self, query: str, embedding: List[float]) -> Optional[Any]:
        current_time = time.time() # Incorrect: hardcodes time instead of accepting it as an argument
        self._cleanup_expired(current_time)
```

### 4. Overly Complex Vector Indexing
Candidates sometimes try to implement complex KD-Trees, HNSW, or clustering algorithms for an in-memory test. This violates the simplicity constraint and usually leads to buggy implementations. A linear scan $O(N)$ with cosine similarity is the expected pattern for this LLD exercise.

### 5. Missing Input and Dimension Validation
Candidates must explicitly validate inputs and raise a `ValueError` for empty queries, empty embeddings, or mismatched embedding dimensions.

**Counterexample (Incorrect implementation):**
```python
    def get(self, query: str, embedding: List[float], current_time: float) -> Optional[Any]:
        # Missing validation for empty query or embedding
        # Missing validation for mismatched embedding dimension during semantic match
```
