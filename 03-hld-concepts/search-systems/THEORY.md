# Search Systems (Elasticsearch)

**Code and tests**: See [Elasticsearch](../elasticsearch/THEORY.md) for canonical code and tests.

## What is it?

Elasticsearch is a distributed, RESTful search and analytics engine built on Apache Lucene. It provides real-time full-text search, structured search, and analytics capabilities with horizontal scalability and high availability.

## Why do we need it?

**Problem it solves**: Traditional relational databases are inefficient for full-text search, especially across large datasets with complex querying requirements like relevance scoring, typo tolerance, and faceted search.

**Without Elasticsearch**:
- Slow LIKE queries in SQL databases (`WHERE text LIKE '%keyword%'`)
- No relevance ranking or scoring
- Limited typo tolerance and fuzzy matching
- Poor performance for unstructured text search
- Complex aggregations are slow

**With Elasticsearch**:
- Sub-second full-text search across billions of documents
- Relevance scoring (TF-IDF, BM25)
- Fuzzy matching, synonyms, and autocomplete
- Real-time analytics and aggregations
- Horizontal scaling across nodes

## Core Concepts

### 1. Inverted Index

The fundamental data structure powering Elasticsearch:

```
Documents:
Doc 1: "The quick brown fox"
Doc 2: "The lazy dog"
Doc 3: "Quick brown dogs"

Inverted Index:
Term      → Document IDs
----------------------------
the       → [1, 2]
quick     → [1, 3]
brown     → [1, 3]
fox       → [1]
lazy      → [2]
dog       → [2]
dogs      → [3]

Search "quick brown":
- quick → [1, 3]
- brown → [1, 3]
- Result: Documents 1, 3 (intersection)
```

**Text analysis pipeline**:
```
Input: "The Quick BROWN fox!"
    ↓ Tokenization
["The", "Quick", "BROWN", "fox", "!"]
    ↓ Lowercase Filter
["the", "quick", "brown", "fox", "!"]
    ↓ Stop Words Removal
["quick", "brown", "fox"]
    ↓ Stemming
["quick", "brown", "fox"]
    ↓ Stored in Inverted Index
```

### 2. Architecture

```
Elasticsearch Cluster
├── Node 1 (Master-eligible, Data)
│   ├── Index: products
│   │   ├── Shard 0 (Primary)
│   │   └── Shard 2 (Replica)
│   └── Index: users
│       └── Shard 1 (Primary)
├── Node 2 (Data)
│   ├── Index: products
│   │   ├── Shard 1 (Primary)
│   │   └── Shard 0 (Replica)
│   └── Index: users
│       └── Shard 0 (Replica)
└── Node 3 (Coordinating only)
    └── Routes queries to data nodes
```

**Node types**:
- **Master**: Cluster management, index creation/deletion
- **Data**: Store shards, execute queries
- **Coordinating**: Route requests, merge results
- **Ingest**: Pre-process documents before indexing

### 3. Sharding and Replication

```
Index: products (3 primary shards, 1 replica)

Node 1          Node 2          Node 3
P0 (docs 0-333) P1 (docs 334-666) P2 (docs 667-999)
R2 (replica)    R0 (replica)     R1 (replica)

Write to doc 500:
→ Routes to Node 2 (P1 owns doc 500)
→ Writes to P1
→ Replicates to R1 on Node 3
→ Acknowledges client
```

**Shard sizing best practices**:
- 10-50 GB per shard (optimal)
- Fewer large shards > many small shards
- Shard count = number of nodes × 1-3 (for scaling)

## How it works

### Indexing (Write Path)

```
Client → POST /products/_doc/123
    ↓
Coordinating Node
    ↓ (hash doc ID to determine shard)
Primary Shard (Node 2)
    ├── 1. Add to in-memory buffer
    ├── 2. Append to translog (durability)
    ├── 3. Periodic refresh → make searchable
    └── 4. Replicate to replica shards
    ↓
Acknowledge to client (after quorum)
```

**Refresh interval**: Default 1 second (near real-time, not real-time)

### Search (Read Path)

```
Client → GET /products/_search?q=laptop
    ↓
Coordinating Node
    ↓ (broadcasts to all shards)
┌───┴───┬─────────┐
P0      P1        P2 (or replicas R0, R1, R2)
    ↓ (each shard searches locally)
Top 10 results from each shard
    ↓ (returned to coordinator)
Coordinating Node
    ├── Merges results
    ├── Sorts by relevance score
    └── Returns top 10 overall
```

**Two-phase search**:
1. **Query phase**: Fetch document IDs and scores
2. **Fetch phase**: Retrieve full documents for top results

### Relevance Scoring (BM25)

```
Score = IDF(term) × TF(term, doc) × Field-Length-Norm

IDF (Inverse Document Frequency):
- Rare terms score higher
- log((N - df + 0.5) / (df + 0.5))
- N = total docs, df = docs containing term

TF (Term Frequency):
- More occurrences score higher
- But with diminishing returns

Field-Length-Norm:
- Penalizes long documents
```

**Example**:
```
Query: "machine learning"

Doc 1: "Machine learning is a subset of AI. Machine learning..."
       → High TF for "machine", high relevance

Doc 2: "Introduction to computing, databases, networks, ML..."
       → Low TF for "machine", lower relevance

Result: Doc 1 scores higher
```

## Query Types

### 1. Full-Text Queries

**Match Query** (analyzed, fuzzy):
```json
GET /products/_search
{
  "query": {
    "match": {
      "title": {
        "query": "wireles headphon",
        "fuzziness": "AUTO"
      }
    }
  }
}
```
Matches: "wireless headphones" (typo tolerance)

**Multi-Match** (search across fields):
```json
{
  "query": {
    "multi_match": {
      "query": "laptop",
      "fields": ["title^3", "description", "brand^2"]
    }
  }
}
```
Field boosting: `title^3` = 3x weight

### 2. Term-Level Queries

**Term Query** (exact match, not analyzed):
```json
{
  "query": {
    "term": {
      "status.keyword": "active"
    }
  }
}
```

**Range Query**:
```json
{
  "query": {
    "range": {
      "price": {
        "gte": 100,
        "lte": 500
      }
    }
  }
}
```

### 3. Compound Queries

**Bool Query** (combine multiple queries):
```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"category": "electronics"}}
      ],
      "filter": [
        {"range": {"price": {"lte": 1000}}},
        {"term": {"in_stock": true}}
      ],
      "should": [
        {"match": {"brand": "Apple"}},
        {"match": {"brand": "Samsung"}}
      ],
      "must_not": [
        {"term": {"refurbished": true}}
      ]
    }
  }
}
```

- **must**: Required, affects score
- **filter**: Required, no scoring (cacheable, faster)
- **should**: Optional, boosts score
- **must_not**: Excluded

## Aggregations

Aggregations enable analytics on search results:

**Metric aggregations** (statistics):
```json
{
  "aggs": {
    "avg_price": {"avg": {"field": "price"}},
    "max_price": {"max": {"field": "price"}},
    "total_sales": {"sum": {"field": "quantity_sold"}}
  }
}
```

**Bucket aggregations** (grouping):
```json
{
  "aggs": {
    "by_category": {
      "terms": {"field": "category.keyword", "size": 10},
      "aggs": {
        "avg_price_per_category": {
          "avg": {"field": "price"}
        }
      }
    }
  }
}
```

Result:
```
Electronics: avg_price $450 (1200 items)
Clothing: avg_price $35 (800 items)
Books: avg_price $15 (2000 items)
```

## When to use

✅ **Use Elasticsearch when:**
- Full-text search across documents
- Typo tolerance and fuzzy matching needed
- Relevance ranking important
- Real-time search and analytics
- Log analysis and monitoring (ELK stack)
- Faceted search and filtering
- Autocomplete and suggestions

**Specific scenarios:**
- E-commerce product search
- Document management systems
- Log aggregation (Elasticsearch + Logstash + Kibana)
- Application search (GitHub, Stack Overflow)
- Metrics and time-series analytics

## When NOT to use

❌ **Avoid or reconsider when:**
- Primary data store (use as secondary index)
- ACID transactions required
- Strong consistency needed (eventual consistency)
- Binary data storage (use object storage)
- Frequent updates to same documents (write-heavy)
- Joins across indices (not supported)

**Consider alternatives:**
- **PostgreSQL**: Full-text search for relational data
- **Solr**: Similar to Elasticsearch, more mature
- **Algolia**: Managed search-as-a-service
- **Typesense**: Open-source typo-tolerant search

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Inverted index** | Fast full-text search | High storage overhead (1.5-3x) |
| **Near real-time** | Fresh data (1s refresh) | Not truly real-time |
| **Schemaless** | Flexible indexing | Type mismatches can cause errors |
| **Horizontal scaling** | Add nodes for capacity | Complex cluster management |
| **Relevance scoring** | Smart ranking | Can be opaque, requires tuning |
| **Eventual consistency** | High availability | Read-your-writes not guaranteed |

## Real-world examples

### GitHub
- **Usage**: Code search across repositories
- **Scale**: Billions of lines of code indexed
- **Pattern**: Multi-field search with syntax highlighting

### Uber
- **Usage**: Restaurant and dish search in Uber Eats
- **Pattern**: Geospatial search + full-text + filters

### Netflix
- **Usage**: Content search and recommendations
- **Pattern**: Fuzzy search, autocomplete, personalized ranking

### StackOverflow
- **Usage**: Question and answer search
- **Pattern**: Full-text + tag filtering + relevance boosting

## Complexity Analysis

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| **Index document** | O(log N) per shard | N = docs in shard |
| **Term lookup** | O(1) | Inverted index lookup |
| **Full-text query** | O(T + K log K) | T = matching docs, K = top K results |
| **Aggregation** | O(N) | N = matching documents |
| **Scroll** | O(N) | For exporting all results |

## Common Problems and Solutions

### 1. Mapping Explosion
**Problem**: Too many fields cause memory issues

**Solution**:
```json
{
  "mappings": {
    "_source": {"enabled": false},  // Don't store original doc
    "dynamic": "strict",  // Reject unmapped fields
    "properties": {
      "metadata": {
        "type": "flattened"  // Single field for many keys
      }
    }
  }
}
```

### 2. Deep Pagination
**Problem**: `from/size` inefficient for deep pages

**Solution**: Use search_after or scroll API
```json
{
  "size": 100,
  "query": {...},
  "search_after": [last_doc_sort_value]
}
```

### 3. Slow Aggregations
**Problem**: Aggregations on high-cardinality fields

**Solution**: Use sampling or doc_count_error_upper_bound

## Key Takeaways

1. **Inverted index powers search**: Optimized for read-heavy full-text queries
2. **Near real-time, not real-time**: 1-second refresh interval
3. **Shard sizing matters**: 10-50 GB per shard for optimal performance
4. **Use as secondary index**: Not a primary data store
5. **Relevance tuning is iterative**: BM25 scoring requires testing
6. **Denormalize data**: No joins; duplicate data across documents
7. **Monitor cluster health**: Yellow/red status indicates issues

---

## Related Concepts
- [NoSQL Databases](../nosql-databases/) - Document store patterns
- [Caching](../caching/) - Search result caching strategies
- [Database Sharding](../database-sharding/) - Horizontal partitioning patterns

## Elasticsearch Overview

## Why do we need it?
- Provide relevance-ranked search beyond exact database indexing.
- Support typo tolerance, tokenization, and language-aware search behavior.
- Run faceting/aggregation workloads without overloading transactional databases.
- Scale search and indexing independently from OLTP systems.

## Requirements and constraints
- Keep a transactional database as source of truth for critical writes.
- Define mappings intentionally (field types, analyzers, keyword vs text usage).
- Size shards and replicas to match data growth and query shape.
- Plan reindex strategy for incompatible schema changes.
- Track indexing lag and freshness SLOs explicitly.

## How it works

### Core model
- Documents are stored in indices.
- Each index is split into primary shards.
- Replicas improve availability and read throughput.
- Coordinating nodes fan out query work and merge results.

### Query model
- **Full-text queries** for relevance scoring.
- **Filter clauses** for deterministic constraints.
- **Aggregation clauses** for analytics and reporting.

## When to use
- Product/content/document search with ranking needs.
- Observability and log analytics pipelines.
- High-cardinality faceted filtering experiences.

## When NOT to use
- Strongly consistent transactional write ownership.
- Tiny datasets where relational full-text is sufficient.
- Complex relational joins as primary requirement.

## Trade-offs
| Pros | Cons |
|------|------|
| Powerful search relevance model | Operational complexity (mapping, shard tuning) |
| Horizontal query scaling | Reindexing can be expensive |
| Flexible document model | Eventual consistency in indexed views |

## Scoring rubric
| Score | Interview signal |
|---|---|
| 1 | Proposes Elasticsearch without source-of-truth separation |
| 3 | Correct high-level usage with shards/replicas awareness |
| 5 | Includes mapping strategy, reindex rollout, and freshness/error SLO trade-offs |

## Common pitfalls
- Making Elasticsearch the only write source.
- Over-sharding small datasets.
- Using wildcard-heavy queries in hot paths.
- Ignoring mapping drift and long-term reindex costs.

## Follow-up questions
1. How would you handle a breaking mapping change?
2. What metrics indicate cluster pressure (query and indexing sides)?
3. How would you isolate noisy tenants in shared search clusters?
4. How do you set freshness expectations for end users?

## Variants and extensions
- **Log analytics variant:** time-partitioned indices + retention lifecycle.
- **E-commerce variant:** text relevance + filters + boosting by business signals.
- **Multilingual variant:** per-field analyzer strategy and locale-specific ranking.

## Related concepts and projects
- [Database Sharding](../database-sharding/)
- [Message Queues](../message-queues/)
- [Monitoring & Observability](../monitoring-observability/)
- [E-commerce Backend](../../04-hld-projects/ecommerce-backend/)
- [News Feed](../../04-hld-projects/news-feed/)
- [LinkedIn Feed Case Study](../../case-studies/linkedin-feed/)
- [HLD Concepts Quiz](../../quizzes/hld-concepts-quiz.md)
- [HLD Concepts Flashcards](../../flashcards/hld-concepts.md)

---

## Source 15 Integration: Social Post Search

For social post search, keep source-of-truth writes in OLTP, project to search index asynchronously, and define bounded freshness instead of pretending fully synchronous search visibility.
