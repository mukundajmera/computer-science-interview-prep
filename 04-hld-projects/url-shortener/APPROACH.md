# Design Approach for URL Shortener

A step-by-step thought process for designing the URL shortening system.

---

## 1. Requirements Clarification

### Functional vs Non-Functional

**Functional (What the system does):**
- Shorten long URLs to short, unique codes
- Redirect short URLs to original long URLs
- Support custom aliases
- Track basic analytics (click count)
- Support optional link expiration

**Non-Functional (How the system behaves):**
- High availability (99.99%)
- Low latency (< 100ms for redirects)
- High throughput (100K+ redirects/second)
- Durable storage (no data loss)
- Eventually consistent

### Assumptions with Numbers

| Metric | Value | Reasoning |
|--------|-------|-----------|
| DAU | 100 million | Large-scale service |
| New URLs/month | 100 million | ~40 URL creations/second |
| Redirects/month | 10 billion | 100:1 read/write ratio |
| URL retention | 5 years | Long-term storage |
| Short URL length | 7 chars | 62^7 = 3.5 trillion combinations |

---

## 2. Back-of-the-Envelope Estimation

### Traffic Calculations

```
Write Operations (URL Creation):
- 100M URLs/month
- = 100M / (30 * 24 * 3600) = ~40 URLs/second
- Peak: 40 * 3 = ~120 URLs/second

Read Operations (Redirects):
- 10B redirects/month
- = 10B / (30 * 24 * 3600) = ~4,000 redirects/second
- Peak: 4,000 * 3 = ~12,000 redirects/second

Read/Write Ratio: 100:1 (read-heavy)
```

### Storage Calculations

```
Per URL Entry:
- Short URL (7 chars): 7 bytes
- Long URL (avg 100 chars): 100 bytes
- Created timestamp: 8 bytes
- Expiration timestamp: 8 bytes
- User ID (optional): 8 bytes
- Click count: 8 bytes
- Metadata: ~20 bytes
- Total: ~160 bytes per URL

5-Year Storage:
- URLs: 100M/month * 12 * 5 = 6 billion URLs
- Storage: 6B * 160 bytes = 960 GB ≈ 1 TB

With indexes and overhead: ~3-5 TB total
```

### Bandwidth Calculations

```
Incoming (Writes):
- 40 URLs/sec * 200 bytes (request) = 8 KB/s

Outgoing (Redirects):
- 4,000 req/sec * 500 bytes (response with redirect) = 2 MB/s

Cache bandwidth (reads from cache):
- Assuming 80% cache hit rate
- 3,200 req/sec from cache * 200 bytes = 640 KB/s
```

### Memory for Caching

```
Hot URLs (20% of URLs, 80% of traffic - Pareto):
- 20% of 6B URLs = 1.2 billion URLs
- Too many! Cache only recent/hot ones

Realistic cache:
- Top 1 million URLs in memory
- 1M * 160 bytes = 160 MB (fits easily)
- Could cache 10M URLs = 1.6 GB
```

---

## 3. API Design

### Endpoint 1: Create Short URL

```
POST /api/v1/urls

Request:
{
    "longUrl": "https://example.com/very/long/path/to/resource",
    "customAlias": "my-custom-name",    // optional
    "expiresAt": "2025-12-31T23:59:59Z" // optional
}

Response (201 Created):
{
    "shortUrl": "https://short.ly/abc1234",
    "shortCode": "abc1234",
    "longUrl": "https://example.com/very/long/path/to/resource",
    "expiresAt": "2025-12-31T23:59:59Z",
    "createdAt": "2024-01-15T10:30:00Z"
}

Errors:
- 400: Invalid URL format
- 409: Custom alias already exists
- 429: Rate limit exceeded
```

### Endpoint 2: Redirect to Original URL

```
GET /{shortCode}

Response (301 Moved Permanently):
Location: https://example.com/very/long/path/to/resource

Errors:
- 404: Short URL not found
- 410: Short URL has expired
```

### Endpoint 3: Get URL Analytics

```
GET /api/v1/urls/{shortCode}/stats

Response:
{
    "shortCode": "abc1234",
    "longUrl": "https://example.com/very/long/path/to/resource",
    "clicks": 15420,
    "createdAt": "2024-01-15T10:30:00Z",
    "expiresAt": null
}

Errors:
- 404: Short URL not found
- 401: Unauthorized (if authentication required)
```

### Endpoint 4: Delete URL

```
DELETE /api/v1/urls/{shortCode}

Response (204 No Content)

Errors:
- 404: Short URL not found
- 401: Unauthorized
```

### Idempotency Considerations

- URL creation can be made idempotent by returning existing short URL for same long URL
- Delete operations are naturally idempotent
- Use request IDs for retry safety

---

## 4. Data Model

### Database Choice: NoSQL (Key-Value Store)

**Why NoSQL over SQL:**

| Factor | NoSQL | SQL |
|--------|-------|-----|
| Read Pattern | Simple key lookup (shortCode → URL) | Same |
| Write Pattern | Simple inserts | Same |
| Joins | None needed | Not needed |
| Scale | Horizontal scaling easier | Vertical + sharding complex |
| Flexibility | Schema flexibility for metadata | Fixed schema |
| Consistency | Eventual (acceptable) | ACID (overkill) |

**Recommendation**: Use NoSQL (DynamoDB, Cassandra, or Redis for cache + persistent store)

### Primary Table: urls

```
{
    short_code:     string (PK)     -- "abc1234"
    long_url:       string          -- "https://example.com/..."
    created_at:     timestamp       -- creation time
    expires_at:     timestamp       -- null if never expires
    user_id:        string          -- null if anonymous
    click_count:    number          -- analytics counter
    is_custom:      boolean         -- custom alias flag
    metadata:       map             -- extensible metadata
}

Indexes:
- Primary Key: short_code (hash key)
- GSI: user_id (for listing user's URLs)
- GSI: long_url (for deduplication, optional)
```

### Caching Layer

```
Redis Cache Structure:
- Key: short_code
- Value: long_url
- TTL: 24 hours (configurable)

Example:
  SET "abc1234" "https://example.com/..." EX 86400
```

### Sharding Strategy

**Sharding Key**: `short_code`
- Natural distribution (random IDs spread evenly)
- No hot partition issues with hash-based sharding
- Alternative: Range-based on creation time (but causes hot partitions)

---

## 5. High-Level Architecture

### Logical Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
│              (Web Browsers, Mobile Apps, APIs)              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   DNS + CDN      │ ← Cache redirects at edge
                    │  (CloudFlare)    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Load Balancer   │ ← L7, health checks
                    │     (ALB/NLB)    │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │   API    │  │   API    │  │   API    │
        │ Server 1 │  │ Server 2 │  │ Server N │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │             │             │
             └──────────┬──┴─────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │  Cache   │  │ ID Gen   │  │Analytics │
    │ (Redis)  │  │ Service  │  │ (Kafka)  │
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    Database      │
              │ (DynamoDB/Cass)  │
              │   [Sharded]      │
              └──────────────────┘
```

### HLD Concepts Used

| Concept | How It's Used |
|---------|---------------|
| **Load Balancer** | Distribute traffic across API servers |
| **Cache (Redis)** | Store hot URLs for fast redirects |
| **CDN** | Cache redirects at edge locations |
| **NoSQL Database** | Store URL mappings, scale horizontally |
| **Message Queue** | Async analytics processing |
| **API Gateway** | Rate limiting, authentication |
| **Sharding** | Partition data across DB nodes |

### Read Path (Redirect)

```
1. Client requests GET /abc1234
2. CDN checks if redirect is cached → if yes, return 301
3. Request hits Load Balancer → routes to API server
4. API server checks Redis cache
   - Cache HIT: Return 301 redirect immediately
   - Cache MISS: Query database
5. Query database for short_code
6. If found: Cache result, return 301 redirect
7. If not found: Return 404
8. Async: Increment click count (via queue)
```

### Write Path (Create URL)

```
1. Client sends POST /api/v1/urls with long URL
2. API server validates URL format
3. (Optional) Check if long URL already shortened
4. Generate unique short code via ID service
5. Write to database (short_code → long_url)
6. Optionally cache the new mapping
7. Return short URL to client
```

---

## 6. Deep Dives

### 6.1 ID Generation Strategies

**Option A: Counter-Based (Centralized)**
```
- Use auto-increment counter
- Convert counter to base62
- Pros: Guaranteed unique, compact
- Cons: Single point of failure, bottleneck
```

**Option B: Hash-Based (MD5/SHA)**
```
- Hash(longUrl + timestamp + random)
- Take first 7 characters
- Pros: Distributed, no coordination
- Cons: Collision possible, need collision handling
```

**Option C: Pre-Generated Keys (Recommended)**
```
- Key Generation Service (KGS)
- Pre-generate millions of unique 7-char codes
- Store in database (used/unused tables)
- Workers fetch batches of unused keys
- Pros: Fast, distributed, no collisions
- Cons: Need to maintain key pool
```

**Chosen Approach**: Pre-generated keys with base62 encoding
- 62^7 = 3.5 trillion combinations
- Far exceeds 6 billion URLs needed in 5 years

### 6.2 Caching Strategy

**Cache-Aside Pattern (Lazy Loading)**
```
Read:
1. Check cache for key
2. If miss, read from DB
3. Populate cache
4. Return value

Write:
1. Write to DB
2. Invalidate cache (or update)
```

**Cache Configuration**
```
- Cache: Redis Cluster
- Eviction: LRU (Least Recently Used)
- TTL: 24 hours for general URLs
- No TTL: For top 1000 most accessed URLs
- Size: 10 million entries (~1.6 GB)
```

**Handling Hot Keys**
```
Problem: Viral URLs get millions of requests
Solutions:
1. Replicate hot keys across cache nodes
2. Use CDN to cache redirects at edge
3. Local in-memory cache on API servers (short TTL)
```

### 6.3 Database Sharding

**Sharding by short_code (Hash-based)**
```
shard_id = hash(short_code) % num_shards

Benefits:
- Even distribution (random codes)
- No need to know creation time
- Single shard lookup for reads

Drawbacks:
- Range queries difficult (acceptable)
- Adding shards requires rebalancing
```

**Replication**
```
- Each shard has 3 replicas
- 1 primary + 2 secondaries
- Read from secondaries (eventual consistency OK)
- Write to primary only
```

---

## 7. Bottlenecks and Mitigations

### Identified Bottlenecks

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| **ID Generation** | Single point of failure | Use KGS with key pools per server |
| **Database Writes** | 40 writes/sec easy, but spikes | Write-behind caching, batching |
| **Database Reads** | 4,000 reads/sec | Cache layer, read replicas |
| **Hot URLs** | Single key overload | CDN caching, key replication |
| **Cache Failures** | Database overwhelmed | Circuit breaker, cache redundancy |

### Scaling Strategy

```
Level 1 (100 QPS):
- Single server, single DB, Redis cache
- Handles basic load

Level 2 (10K QPS):
- Multiple API servers behind LB
- Redis cluster (3 nodes)
- Database with read replicas

Level 3 (100K+ QPS):
- Global CDN for edge caching
- Multiple Redis clusters per region
- Sharded database (10+ shards)
- Multi-region deployment
```

---

## 8. Evolution Plan

### v1 → v2 → v3 Narrative

**v1-basic: MVP (Week 1)**
```
- Single API server
- Single database
- Simple counter-based ID generation
- No caching (acceptable for low traffic)
- Focus: Correctness, basic functionality

Handles: ~100 redirects/second
```

**v2-scaled: Production Ready (Month 1)**
```
- Multiple API servers + Load Balancer
- Redis cache layer
- Key Generation Service (KGS)
- Database read replicas
- Basic analytics (async via queue)
- Rate limiting

Handles: ~10,000 redirects/second
```

**v3-distributed: Planet Scale (Month 6)**
```
- Multi-region deployment
- Global CDN (CloudFlare, CloudFront)
- Sharded database across regions
- Active-active with conflict resolution
- Advanced analytics pipeline
- Custom domains support

Handles: ~1,000,000 redirects/second globally
```

---

## Interview Discussion Points

1. **Why base62 encoding?**
   - Case-sensitive alphanumeric (a-z, A-Z, 0-9)
   - 62^7 = 3.5 trillion combinations
   - URL-safe characters only

2. **Why not hash the long URL directly?**
   - Same long URL might need different short URLs
   - Different users might want different aliases
   - Hash collisions need handling anyway

3. **How to handle expired URLs?**
   - Lazy deletion: Check expiry on read
   - Background cleanup job for storage
   - Don't reuse expired codes immediately

4. **301 vs 302 redirect?**
   - 301 (Permanent): Browser caches, better for SEO
   - 302 (Temporary): Fresh lookup each time, better for analytics
   - Recommendation: 301 for most cases, 302 for analytics-heavy

5. **How to prevent abuse?**
   - Rate limiting per IP/user
   - CAPTCHA for anonymous users
   - Block known malicious URLs (external service)
