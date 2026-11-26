# Interview Questions: Search Systems (Elasticsearch)

## Basic Questions

### 1. What is Elasticsearch and when would you use it?

**A**: Elasticsearch is a distributed search and analytics engine built on Lucene, providing full-text search with relevance ranking, typo tolerance, and real-time analytics.

**Use cases:**
- E-commerce product search with faceted filtering
- Log analytics (ELK stack: Elasticsearch + Logstash + Kibana)
- Application search (GitHub code search, Stack Overflow)
- Autocomplete and suggestions
- Real-time analytics dashboards

**Key features:**
- Full-text search with BM25 relevance scoring
- Horizontal scalability (sharding)
- Near real-time indexing (1-second refresh)
- Rich aggregations for analytics

**vs Alternatives:**
- Faster than SQL `LIKE` queries for text search
- More flexible than Solr (easier clustering)
- Cheaper than Algolia (self-hosted option)

---

### 2. Explain inverted indexes

**A**: Inverted index maps terms to documents (opposite of document → terms):

```
Documents:
1: "quick brown fox"
2: "lazy brown dog"

Inverted Index:
quick → [1]
brown → [1, 2]
fox   → [1]
lazy  → [2]
dog   → [2]

Query "brown dog" → [2] (intersection of brown ∩ dog)
```

**Why inverted indexes are fast:**
- O(1) term lookup (hash table)
- O(K) to merge K posting lists
- No need to scan all documents

---

### 3. What are shards and replicas?

**A**:
- **Shards**: Horizontal partitions of an index
- **Replicas**: Copies of shards for high availability

```
Index with 3 primary shards, 1 replica:

Node 1: P0, R1
Node 2: P1, R2
Node 3: P2, R0

Write to doc → hashed to shard → written to primary → replicated
Read → load balanced across primary/replica
```

**Best practices:**
- 10-50 GB per shard
- Number of primaries = nodes × 1-3 (for future scaling)
- Replicas ≥ 1 for production (HA)

---

### 4. How does Elasticsearch achieve near real-time search?

**A**:
1. Document indexed → written to in-memory buffer
2. Every 1 second (refresh interval), buffer → new segment
3. Segment immediately searchable (near real-time)
4. Periodically, segments merged and flushed to disk

**Trade-off**: 1-second delay vs truly real-time, but much faster indexing

---

### 5. What is the difference between `match` and `term` queries?

**A**:
- **Match**: Analyzed, full-text search, relevance scoring
- **Term**: Exact match, not analyzed, filter use case

```json
// Match: "Quick BROWN fox" → analyzed → ["quick", "brown", "fox"]
{"match": {"text": "Quick fox"}}  // Matches

// Term: Exact match on keyword field
{"term": {"status.keyword": "active"}}  // "Active" won't match
```

---

## Intermediate Questions

### 1. How would you design search for an e-commerce site?

**A**:
```json
Index: products
Mapping:
{
  "properties": {
    "title": {"type": "text", "analyzer": "standard"},
    "category": {"type": "keyword"},
    "brand": {"type": "keyword"},
    "price": {"type": "float"},
    "description": {"type": "text"},
    "in_stock": {"type": "boolean"},
    "rating": {"type": "float"},
    "tags": {"type": "keyword"}
  }
}

Search query with facets:
{
  "query": {
    "bool": {
      "must": [
        {"multi_match": {
          "query": "wireless headphones",
          "fields": ["title^3", "description"]
        }}
      ],
      "filter": [
        {"term": {"in_stock": true}},
        {"range": {"price": {"lte": 200}}}
      ],
      "should": [
        {"term": {"brand": "Sony"}},
        {"range": {"rating": {"gte": 4.0}}}
      ]
    }
  },
  "aggs": {
    "brands": {"terms": {"field": "brand"}},
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          {"to": 50},
          {"from": 50, "to": 100},
          {"from": 100, "to": 200},
          {"from": 200}
        ]
      }
    }
  }
}
```

---

### 2. How do you implement autocomplete?

**A**: Three common approaches:

**1. Prefix queries** (simple):
```json
{"prefix": {"title": "wire"}}  // Matches "wireless"
```

**2. Edge n-grams** (faster):
```json
Analyzer: "quick" → ["q", "qu", "qui", "quic", "quick"]
Query: "qui" → instant match
```

**3. Completion suggester** (optimized):
```json
{
  "suggest": {
    "product-suggest": {
      "prefix": "wire",
      "completion": {"field": "suggest"}
    }
  }
}
```

**Recommendation**: Completion suggester for production (in-memory FST, very fast)

---

### 3. How would you handle multi-language search?

**A**:
**Approach 1: Separate fields per language**
```json
{
  "title_en": "laptop",
  "title_es": "portátil",
  "title_fr": "ordinateur portable"
}
```

**Approach 2: Language-specific analyzers**
```json
{
  "properties": {
    "title": {
      "type": "text",
      "fields": {
        "english": {"analyzer": "english"},
        "spanish": {"analyzer": "spanish"},
        "french": {"analyzer": "french"}
      }
    }
  }
}
```

**Approach 3: ICU analysis plugin** (Unicode normalization)

---

## Advanced Questions

### 1. How do you tune Elasticsearch for performance?

**A**:
**Indexing performance:**
- Increase refresh interval: `"refresh_interval": "30s"`
- Bulk indexing: 5-15 MB per request
- Disable replicas during bulk load
- Use SSD storage
- Increase `index.translog.flush_threshold_size`

**Search performance:**
- Use filters instead of queries (cacheable)
- Limit `from + size` (max 10,000 by default)
- Use search_after for deep pagination
- Warm up filesystem cache
- Use doc values for sorting/aggregations

**Cluster tuning:**
- Heap size: 50% of RAM, max 31 GB
- Monitor GC pauses
- Use dedicated master nodes (3+)
- Appropriate shard sizing (10-50 GB)

---

### 2. How would you migrate from SQL database to Elasticsearch?

**A**:
**Strategy:**
1. **Denormalize data** (ES has no joins):
```sql
-- SQL: Normalized
SELECT p.name, c.name FROM products p
JOIN categories c ON p.category_id = c.id

-- ES: Denormalized
{
  "product_name": "Laptop",
  "category_name": "Electronics"  // Duplicated
}
```

2. **Dual-write during migration**:
```
App → SQL (primary)
   → ES (secondary)

Validate ES results
Switch reads to ES
Eventually deprecate SQL for search
```

3. **Use Logstash or custom ETL**:
```
Logstash JDBC input → Elasticsearch output
```

---

## Common Follow-ups

- "How do you handle Elasticsearch cluster failures?"
- "What's the difference between Elasticsearch and Solr?"
- "How do you secure Elasticsearch?"
- "What is the ELK stack?"

---

## Red Flags to Avoid

❌ **Don't say:**
- "Use Elasticsearch as primary database" - It's a secondary index
- "Real-time search" - It's near real-time (1s refresh)
- "ES handles joins" - No joins; denormalize data

---

## How to Explain in 30 Seconds

> "Elasticsearch is a distributed search engine using inverted indexes for fast full-text search with relevance scoring. Key design: choose shard count for scaling (10-50 GB per shard), denormalize data (no joins), use filters for facets (cacheable), and tune refresh interval for indexing speed. Use for product search, log analytics, and autocomplete. Avoid as primary data store. Monitor cluster health and shard distribution."
