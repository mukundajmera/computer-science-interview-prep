# Strong Answer: Social Post Search

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Social Post Search, I will focus on modeling a robust keyword indexing pipeline with a query planning and ranking abstraction. The core deliverables are handling document ingestion (posts), building an inverted index, executing boolean queries (AND/OR), and finally ranking results using BM25. I'll outline the core data models, architect the ingestion and search paths, and address scale, concurrency, and relevance tuning. Our primary goal is to ensure standard-library-only execution with deterministic testing."

By establishing these constraints early, we frame the discussion around concrete algorithmic and structural choices rather than black-box external frameworks. We will use in-memory standard library structures (Java 11+ and Python 3.8+).

## 2. Inverted Index and Ingestion (5-15 minutes)

**Say:** "At the core, we need an `InvertedIndex` and a `Tokenizer`. The tokenizer splits text on word boundaries and removes stopwords. The index maps tokens to sets of document IDs and maintains term frequencies and document lengths."

We use a simple regex-based tokenizer and stopword filtering. Document ingestion is thread-safe using `ConcurrentHashMap` in Java and standard dictionaries (with locks if threaded, though simplified here) in Python. 

When a post is updated or deleted, we remove existing term postings, decrement the total document count, and drop its length metric. Empty documents or text containing only stopwords produce empty tokens and are gracefully ignored.

## 3. Query Grammar and Planning (15-25 minutes)

**Say:** "For search, a `QueryPlanner` parses boolean grammar. We support `AND` and `OR` operations. The planner breaks the query into a List of `OR` groups, each containing one or more terms combined with `AND`. This transforms flat text into a manageable execution plan."

If a query contains an unindexed term (missing term), it correctly results in an empty set for that specific `AND` group. Empty queries or whitespace-only strings return empty lists.

## 4. Relevance Ranking (BM25) and Tie-breaking (25-35 minutes)

**Say:** "Instead of arbitrary relevance scores, we use hand-calculated BM25 ranking. BM25 requires document frequency (`df`), term frequency (`tf`), total documents (`N`), average document length (`avgdl`), and constants `k1=1.5` and `b=0.75`. To ensure deterministic tie-breaking, we sort by score descending, then by `postId` ascending if scores are identical."

This is the most critical algorithmic portion.

### Java Implementation

```java
public List<String> rank(String rawQuery, List<String> candidatePostIds) {
    List<String> queryTerms = Tokenizer.tokenize(rawQuery);
    if (queryTerms.isEmpty() || candidatePostIds.isEmpty()) return candidatePostIds;

    double avgdl = 0;
    if (index.getTotalDocs() > 0) {
        int totalLen = index.getDocLengths().values().stream().mapToInt(Integer::intValue).sum();
        avgdl = (double) totalLen / index.getTotalDocs();
    }

    List<Map.Entry<String, Double>> scores = new ArrayList<>();
    for (String postId : candidatePostIds) {
        double score = 0.0;
        int docLen = index.getDocLengths().getOrDefault(postId, 0);
        
        Map<String, Integer> tfs = index.getTermFreqs().getOrDefault(postId, Collections.emptyMap());
        for (String term : queryTerms) {
            int tf = tfs.getOrDefault(term, 0);
            if (tf == 0) continue;
            
            int df = index.getIndex().getOrDefault(term, Collections.emptySet()).size();
            int N = index.getTotalDocs();
            
            double idf = Math.log(1 + (N - df + 0.5) / (df + 0.5));
            double termScore = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * docLen / (avgdl == 0 ? 1 : avgdl))));
            score += termScore;
        }
        scores.add(new AbstractMap.SimpleEntry<>(postId, score));
    }

    scores.sort((e1, e2) -> {
        int cmp = Double.compare(e2.getValue(), e1.getValue());
        if (cmp == 0) return e1.getKey().compareTo(e2.getKey());
        return cmp;
    });

    List<String> ranked = new ArrayList<>();
    for (Map.Entry<String, Double> entry : scores) {
        ranked.add(entry.getKey());
    }
    return ranked;
}
```

### Python Implementation

```python
def rank(self, raw_query: str, candidate_post_ids: List[str]) -> List[str]:
    query_terms = Tokenizer.tokenize(raw_query)
    if not query_terms or not candidate_post_ids:
        return candidate_post_ids
    
    avgdl = 0
    if self.index.total_docs > 0:
        avgdl = sum(self.index.doc_lengths.values()) / self.index.total_docs

    scores: List[Tuple[str, float]] = []
    for post_id in candidate_post_ids:
        score = 0.0
        doc_len = self.index.doc_lengths.get(post_id, 0)
        for term in query_terms:
            tf = self.index.term_freqs.get(post_id, {}).get(term, 0)
            if tf == 0:
                continue
            df = len(self.index.index.get(term, set()))
            N = self.index.total_docs
            idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
            term_score = idf * ((tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * doc_len / (avgdl or 1))))
            score += term_score
        scores.append((post_id, score))

    scores.sort(key=lambda x: (-x[1], x[0]))
    return [pid for pid, _ in scores]
```

## 5. Idempotency and Updates (35-40 minutes)

**Say:** "To guarantee robustness against retries, the `PostIngestionService` implements idempotency hooks by checking if a recent request (identified by an idempotency key) was processed. Additionally, indexing operations gracefully handle document updates by completely cleaning up the old term postings before writing the new ones, preventing phantom search results."

## 6. Architecture & Trade-offs (40-45 minutes)

**Say:** "Architecturally, splitting query planning, inverted index, and ranking into separate classes ensures loose coupling. While this basic version operates entirely in-memory using concurrent data structures, a distributed environment would require document-based or term-based partitioning, alongside external coordinators like ZooKeeper, to handle large-scale indices."
