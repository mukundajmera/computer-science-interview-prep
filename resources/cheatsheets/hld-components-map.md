# 🗺️ HLD Components Map

A guide to selecting the right components for your system design.

---

## 🎯 Quick Selection Guide

```
What problem are you solving?
│
├── Need to reduce LATENCY? ────────────────→ Caching, CDN
├── Need to handle TRAFFIC SPIKES? ─────────→ Load Balancer, Auto-scaling
├── Need ASYNC processing? ─────────────────→ Message Queues
├── Need to SCALE database? ────────────────→ Sharding, Replication
├── Need API management? ───────────────────→ API Gateway
├── Need to PREVENT abuse? ─────────────────→ Rate Limiting
├── Need REAL-TIME updates? ────────────────→ WebSockets, Push notifications
├── Need SEARCH functionality? ─────────────→ Search engine (Elasticsearch)
├── Need to store LARGE FILES? ─────────────→ Blob storage, CDN
└── Need to MONITOR system? ────────────────→ Metrics, Logging, Alerting
```

---

## 📦 Component Deep Dive

### 1. Load Balancer

**When to Use:**
- Multiple server instances
- Need high availability
- Traffic exceeds single server capacity

**Types:**

| Type | Layer | Use Case |
|------|-------|----------|
| Layer 4 (L4) | Transport | Simple, fast, TCP/UDP based |
| Layer 7 (L7) | Application | HTTP routing, SSL termination |

**Algorithms:**

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| Round Robin | Rotate through servers | Equal capacity servers |
| Weighted Round Robin | Proportional distribution | Different capacity servers |
| Least Connections | Route to least busy | Varying request duration |
| IP Hash | Same client → same server | Stateful sessions |
| Least Response Time | Fastest server | Performance optimization |

**Technologies:** Nginx, HAProxy, AWS ELB/ALB, Google Cloud LB

**Trade-offs:**
- ✅ Increases availability and throughput
- ❌ Adds complexity, potential single point of failure
- ❌ Session affinity challenges

**Example Systems:** All high-traffic systems

---

### 2. Caching

**When to Use:**
- Read-heavy workloads (read:write > 10:1)
- Frequently accessed data
- Expensive computations
- Reduce database load

**Caching Strategies:**

| Strategy | Description | Use When |
|----------|-------------|----------|
| **Cache-Aside** | App manages cache | General purpose, read-heavy |
| **Write-Through** | Write to cache + DB | Need strong consistency |
| **Write-Behind** | Write to cache, async to DB | Write-heavy, can lose data |
| **Read-Through** | Cache fetches from DB | Simplify application logic |

**Cache Layers:**

| Layer | What to Cache | Technology |
|-------|---------------|------------|
| CDN | Static files, images | CloudFront, Akamai |
| Application | Session, computed data | Redis, Memcached |
| Database | Query results | DB query cache |
| Browser | Static assets | HTTP headers |

**Eviction Policies:**
- **LRU** (Least Recently Used) - Most common
- **LFU** (Least Frequently Used) - For stable access patterns
- **TTL** (Time To Live) - For time-sensitive data

**Technologies:** Redis, Memcached, CloudFront, Varnish

**Trade-offs:**
- ✅ Dramatically reduces latency
- ✅ Reduces database load
- ❌ Cache invalidation is hard
- ❌ Data can become stale

**Example Systems:** Twitter (timeline cache), Facebook (social graph cache)

---

### 3. Message Queue

**When to Use:**
- Decouple services
- Handle traffic spikes
- Async processing
- Reliable delivery needed

**Types:**

| Type | Use Case | Example |
|------|----------|---------|
| Point-to-Point | Single consumer | Order processing |
| Pub/Sub | Multiple consumers | Notifications, fan-out |
| Stream | Ordered events, replay | Event sourcing |

**Technologies:**

| Technology | Best For | Ordering | Persistence |
|------------|----------|----------|-------------|
| Kafka | High throughput, streaming | Partition-ordered | Yes |
| RabbitMQ | Complex routing, low latency | Queue-ordered | Yes |
| SQS | Simple, managed | No guarantee | Yes |
| Redis Pub/Sub | Real-time, ephemeral | No guarantee | No |

**Trade-offs:**
- ✅ Decouples services
- ✅ Handles spikes (buffer)
- ✅ Reliable delivery
- ❌ Added latency (async)
- ❌ Complexity in ordering
- ❌ Message duplication possible

**Example Systems:** Email/notification systems, Order processing, Video transcoding

---

### 4. CDN (Content Delivery Network)

**When to Use:**
- Serving static content globally
- Large media files (images, videos)
- Reduce origin server load
- Improve global latency

**What to Cache:**
- Static assets (CSS, JS, images)
- Video content
- API responses (carefully)

**Technologies:** CloudFront, Akamai, Cloudflare, Fastly

**Trade-offs:**
- ✅ Dramatically reduces latency globally
- ✅ Reduces origin load
- ❌ Cost can be high
- ❌ Cache invalidation latency

**Example Systems:** Netflix (video), YouTube (video), Any global website

---

### 5. Database (SQL)

**When to Use:**
- Structured data with relationships
- Need ACID transactions
- Complex queries with JOINs
- Data integrity is critical

**Technologies:** PostgreSQL, MySQL, Oracle, SQL Server

**Scaling Options:**
- **Read Replicas** - Scale reads
- **Sharding** - Scale writes
- **Partitioning** - Manage large tables

**Trade-offs:**
- ✅ Strong consistency
- ✅ Complex queries
- ❌ Harder to scale horizontally
- ❌ Schema changes can be painful

---

### 6. Database (NoSQL)

**Types:**

| Type | Use Case | Examples |
|------|----------|----------|
| **Document** | Flexible schema, JSON-like | MongoDB, CouchDB |
| **Key-Value** | Simple lookups, caching | Redis, DynamoDB |
| **Wide-Column** | Time-series, analytics | Cassandra, HBase |
| **Graph** | Relationships, social networks | Neo4j, Neptune |

**When to Use:**
- Flexible/evolving schema
- Horizontal scaling needed
- Simple access patterns
- High write throughput

**Trade-offs:**
- ✅ Easy horizontal scaling
- ✅ Flexible schema
- ❌ Limited query capabilities
- ❌ Eventual consistency (usually)

---

### 7. Sharding

**When to Use:**
- Database too large for single node
- Write throughput exceeds capacity
- Geographic distribution needed

**Strategies:**

| Strategy | How It Works | Pros/Cons |
|----------|--------------|-----------|
| **Range-based** | Shard by data ranges | Easy, but hot spots possible |
| **Hash-based** | Hash key to shard | Even distribution, but range queries hard |
| **Directory-based** | Lookup service | Flexible, but extra lookup |
| **Geo-based** | By geographic region | Low latency, but uneven data |

**Challenges:**
- Cross-shard queries
- Transactions across shards
- Rebalancing when adding shards
- Hotspots

**Trade-offs:**
- ✅ Horizontal scaling
- ❌ Complexity
- ❌ Cross-shard joins expensive

---

### 8. Replication

**When to Use:**
- High availability needed
- Read scaling
- Disaster recovery

**Types:**

| Type | Consistency | Use Case |
|------|-------------|----------|
| **Synchronous** | Strong | Financial, critical data |
| **Asynchronous** | Eventual | Read scaling, acceptable lag |

**Patterns:**
- **Primary-Replica**: One write node, multiple read nodes
- **Multi-Primary**: Multiple write nodes (conflict resolution needed)

**Trade-offs:**
- ✅ High availability
- ✅ Read scaling
- ❌ Replication lag (async)
- ❌ Complexity in conflict resolution

---

### 9. API Gateway

**When to Use:**
- Microservices architecture
- Need single entry point
- Cross-cutting concerns (auth, rate limiting)

**Features:**
- Request routing
- Authentication/Authorization
- Rate limiting
- Request/Response transformation
- SSL termination
- Caching

**Technologies:** Kong, AWS API Gateway, Nginx, Zuul

**Trade-offs:**
- ✅ Centralized management
- ❌ Potential bottleneck
- ❌ Single point of failure

---

### 10. Rate Limiter

**When to Use:**
- Prevent abuse/DDoS
- Fair usage enforcement
- Cost control
- Protect downstream services

**Algorithms:**

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| **Token Bucket** | Tokens replenish over time | Burst allowed, then limit |
| **Leaky Bucket** | Fixed rate output | Smooth traffic |
| **Fixed Window** | Count per time window | Simple implementation |
| **Sliding Window** | Rolling time window | More accurate |

**Technologies:** Redis (distributed), Custom implementation

**Trade-offs:**
- ✅ Protects system
- ❌ Can reject legitimate traffic
- ❌ Distributed implementation complex

---

## 🏗️ System → Components Mapping

| System | Key Components |
|--------|----------------|
| **URL Shortener** | NoSQL DB, Cache, Counter service, Analytics (optional) |
| **Twitter/Feed** | Message queue, Cache, Timeline service, Fan-out service |
| **Chat Application** | WebSockets, Message queue, Presence service, NoSQL |
| **Video Streaming** | CDN, Blob storage, Transcoding service, Adaptive streaming |
| **E-commerce** | SQL DB, Cache, Search engine, Payment gateway, Queue |
| **Uber/Ride-sharing** | Location service (geospatial), Matching service, Maps API |
| **Rate Limiter** | Redis (distributed counter), Token bucket |
| **Notification System** | Message queue, Push service, SMS/Email providers |

---

## 📊 Component Comparison

### Database Selection

| Need | Choose |
|------|--------|
| Strong consistency, complex queries | SQL (PostgreSQL, MySQL) |
| Flexible schema, scale horizontally | Document (MongoDB) |
| Simple key-value, high speed | Key-Value (Redis, DynamoDB) |
| Time-series, write-heavy | Wide-Column (Cassandra) |
| Complex relationships | Graph (Neo4j) |

### Communication Pattern

| Need | Choose |
|------|--------|
| Request-Response, simple | REST API |
| High performance, typed | gRPC |
| Real-time bidirectional | WebSockets |
| Fire and forget | Message Queue |
| One-to-many broadcast | Pub/Sub |

---

## 📋 Interview Quick Reference

**Interviewer mentions...** → **Consider adding...**

| Keyword | Component |
|---------|-----------|
| "millions of users" | Load Balancer, Cache, Sharding |
| "low latency" | Cache, CDN |
| "global users" | CDN, Multi-region |
| "read-heavy" | Cache, Read replicas |
| "write-heavy" | Sharding, NoSQL |
| "real-time" | WebSockets, Pub/Sub |
| "send emails/notifications" | Message Queue |
| "prevent abuse" | Rate Limiter |
| "search" | Elasticsearch |
| "large files" | Blob storage (S3), CDN |
| "reliability" | Replication, Retries, Dead letter queue |

---

## 🔗 Related Resources

- [CONCEPTS.md](../../CONCEPTS.md#️-system-design-components-map) - Components overview
- [04-hld-projects/](../../04-hld-projects/) - See components in action
- [trade-offs-matrix.md](trade-offs-matrix.md) - Compare options

---

*Use this map to quickly identify components for any system design! 🗺️*
