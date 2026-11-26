# 🏗️ HLD Interview Checklist

A step-by-step framework for acing System Design interviews.

---

## 📊 Overview

| Phase | Time (45-60 min) | Focus |
|-------|------------------|-------|
| 1. Requirements | 5-10 min | Clarify functional & non-functional |
| 2. Estimation | 5 min | Back-of-envelope calculations |
| 3. API Design | 5-10 min | Core endpoints |
| 4. Data Model | 5-10 min | Schema and database choice |
| 5. High-Level Architecture | 10-15 min | Components and data flow |
| 6. Deep Dives | 10-15 min | Specific components, scaling |
| 7. Bottlenecks & Trade-offs | 5 min | Discuss alternatives |

---

## 1️⃣ Requirements Clarification (5-10 min)

### What to Do
- **Understand the system's purpose**
- **Identify core features** (must-have vs nice-to-have)
- **Clarify scale and constraints**
- **Define non-functional requirements**

### Questions to Ask

#### Functional Requirements
- "What are the core features we need to support?"
- "Who are the users? What actions can they take?"
- "Should we support [specific feature]?"
- "What's the expected user flow?"

#### Scale & Traffic
- "How many users are we designing for?"
- "What's the expected daily active users (DAU)?"
- "What's the read to write ratio?"
- "Any geographic considerations?"

#### Non-Functional Requirements
- "What's the target latency?"
- "What availability do we need? (99.9%? 99.99%?)"
- "Is consistency or availability more important?"
- "Any compliance or security requirements?"

### Example Dialogue

**Problem:** Design Twitter

> **You:** "Before I start, let me clarify a few things. What features should we focus on? Tweeting, following, timeline?"
>
> **Interviewer:** "Yes, focus on posting tweets and viewing home timeline."
>
> **You:** "What's the scale? How many users?"
>
> **Interviewer:** "Let's say 500 million users, 200 million DAU."
>
> **You:** "For the timeline, should we prioritize low latency reads or strong consistency?"
>
> **Interviewer:** "Low latency is more important. Eventual consistency is acceptable."

### Document Your Requirements

**Functional:**
- Post tweets (140 chars, optional media)
- Follow/unfollow users
- View home timeline (tweets from followed users)
- View user timeline

**Non-Functional:**
- 500M users, 200M DAU
- Low latency (< 200ms for timeline)
- High availability (99.9%)
- Eventual consistency acceptable

### ✅ Checklist
- [ ] Identified core features
- [ ] Clarified scale (users, DAU, QPS)
- [ ] Defined latency/availability requirements
- [ ] Confirmed consistency requirements
- [ ] Noted out-of-scope features

### ⚠️ Red Flags to Avoid
- ❌ Starting design without understanding requirements
- ❌ Not asking about scale
- ❌ Spending too long on this phase (>10 min)

---

## 2️⃣ Back-of-Envelope Estimation (5 min)

### What to Do
- Calculate QPS (queries per second)
- Estimate storage needs
- Estimate bandwidth
- Show your math

### Key Formulas

```
Daily requests = DAU × actions per user per day
QPS = Daily requests / 86,400 (seconds in a day)
Peak QPS = QPS × 2 or 3 (for spikes)
Storage = Size per item × Items per day × Days to store
Bandwidth = QPS × Average request/response size
```

### Example: Twitter Estimation

**Traffic:**
```
- 200M DAU
- Average user views 100 tweets/day, posts 0.5 tweets/day
- Read QPS = 200M × 100 / 86,400 ≈ 230K QPS
- Write QPS = 200M × 0.5 / 86,400 ≈ 1.2K QPS
- Peak Read QPS ≈ 500K QPS
```

**Storage:**
```
- Tweet size: 140 chars + metadata ≈ 300 bytes
- 200M × 0.5 tweets/day = 100M tweets/day
- Daily storage = 100M × 300 bytes = 30 GB/day
- 5-year storage = 30 GB × 365 × 5 ≈ 55 TB
```

**Bandwidth:**
```
- Read: 230K QPS × 10 tweets × 300 bytes = 690 MB/s
- Write: 1.2K QPS × 300 bytes = 360 KB/s
```

### Quick Reference Numbers

| Metric | Value |
|--------|-------|
| Seconds in a day | 86,400 (~100K for easy math) |
| 1 million req/day | ~12 QPS |
| 1 billion req/day | ~12K QPS |

### What to Say

> "Let me do some quick calculations. With 200M DAU and each user viewing ~100 tweets, we're looking at about 230K read QPS. For writes, if users post 0.5 tweets per day on average, that's about 1.2K write QPS. So this is heavily read-dominated."

### ✅ Checklist
- [ ] Calculated read QPS
- [ ] Calculated write QPS
- [ ] Estimated storage requirements
- [ ] Identified read/write ratio
- [ ] Showed calculations clearly

---

## 3️⃣ API Design (5-10 min)

### What to Do
- Define core endpoints
- Specify request/response format
- Consider pagination
- Think about rate limiting

### API Template

```
[METHOD] /api/v1/resource

Request:
{
    "field1": "value",
    "field2": "value"
}

Response: 200 OK
{
    "data": { ... },
    "metadata": { ... }
}

Errors: 400, 401, 404, 500
```

### Example: Twitter APIs

**Post Tweet:**
```
POST /api/v1/tweets
Authorization: Bearer <token>

Request:
{
    "content": "Hello world!",
    "media_ids": ["abc123"]  // optional
}

Response: 201 Created
{
    "tweet_id": "123456",
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Get Home Timeline:**
```
GET /api/v1/timeline?cursor=<cursor>&limit=20
Authorization: Bearer <token>

Response: 200 OK
{
    "tweets": [
        {
            "tweet_id": "123",
            "user_id": "456",
            "content": "...",
            "created_at": "..."
        }
    ],
    "next_cursor": "abc123",
    "has_more": true
}
```

**Follow User:**
```
POST /api/v1/users/{user_id}/follow
Authorization: Bearer <token>

Response: 200 OK
{
    "following": true
}
```

### API Design Tips
- Use RESTful conventions
- Include API versioning (`/v1/`)
- Use cursor-based pagination for feeds
- Include appropriate HTTP status codes
- Consider rate limiting headers

### What to Say

> "For the API, I'll define three main endpoints. First, POST /tweets for creating tweets. GET /timeline for the home feed with cursor-based pagination - this is important for infinite scroll. And POST /users/{id}/follow for following."

### ✅ Checklist
- [ ] Defined CRUD operations needed
- [ ] Included authentication
- [ ] Added pagination for lists
- [ ] Used appropriate HTTP methods
- [ ] Considered error cases

---

## 4️⃣ Data Model (5-10 min)

### What to Do
- Choose database type (SQL vs NoSQL)
- Design schema
- Identify indexes
- Consider partitioning strategy

### Database Selection

| Need | Choose |
|------|--------|
| Relationships, transactions | SQL (PostgreSQL, MySQL) |
| Flexible schema, scale | Document (MongoDB) |
| Simple key-value, speed | Key-Value (Redis, DynamoDB) |
| Time-series, write-heavy | Wide-Column (Cassandra) |

### Example: Twitter Schema

**Users (SQL - PostgreSQL):**
```sql
CREATE TABLE users (
    user_id     UUID PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);
-- Index: username, email
```

**Tweets (NoSQL - Cassandra for write scaling):**
```
Table: tweets
{
    tweet_id:    UUID (partition key)
    user_id:     UUID
    content:     TEXT
    created_at:  TIMESTAMP (clustering key, DESC)
    media_urls:  LIST<TEXT>
}
-- Partition by user_id for user timelines
```

**Follows (SQL or Graph DB):**
```sql
CREATE TABLE follows (
    follower_id  UUID,
    followee_id  UUID,
    created_at   TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id)
);
-- Indexes: follower_id, followee_id
```

**Timeline (Redis for caching):**
```
Key: timeline:{user_id}
Value: List of tweet_ids (sorted by time)
TTL: 24 hours
```

### What to Say

> "For the data model, I'll use SQL for users and follows since we need relationships and consistency. For tweets, Cassandra makes sense given the high write volume and time-series nature. We'll cache timelines in Redis for fast reads."

### ✅ Checklist
- [ ] Chose appropriate database types
- [ ] Designed core tables/collections
- [ ] Identified necessary indexes
- [ ] Considered sharding strategy
- [ ] Explained database choices

---

## 5️⃣ High-Level Architecture (10-15 min)

### What to Do
- Draw the architecture diagram
- Identify all components
- Show data flow
- Explain each component's purpose

### Core Components to Consider

| Component | When to Include |
|-----------|-----------------|
| Load Balancer | Always (multiple servers) |
| API Gateway | Microservices, need auth/rate limiting |
| Application Servers | Always |
| Cache | Read-heavy, need low latency |
| Database | Always |
| Message Queue | Async processing needed |
| CDN | Static content, global users |
| Search | Search functionality |

### Example: Twitter Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Clients                              │
│                  (Web, Mobile, API)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │      Load Balancer      │
              │        (Nginx)          │
              └───────────┬────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │   API   │      │   API   │      │   API   │
    │ Server  │      │ Server  │      │ Server  │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐     ┌─────────────┐    ┌───────────┐
   │  Redis  │     │   Kafka     │    │ Timeline  │
   │ (Cache) │     │  (Queue)    │    │  Service  │
   └────┬────┘     └──────┬──────┘    └─────┬─────┘
        │                 │                 │
        │                 ▼                 │
        │         ┌──────────────┐          │
        │         │   Fan-out    │          │
        │         │   Workers    │          │
        │         └──────┬───────┘          │
        │                │                  │
        ▼                ▼                  ▼
   ┌──────────────────────────────────────────┐
   │              Data Layer                   │
   ├────────────────┬────────────────────────┤
   │  PostgreSQL    │     Cassandra          │
   │  (Users, Follows)  (Tweets)             │
   └────────────────┴────────────────────────┘
```

### Component Descriptions

| Component | Purpose | Technology |
|-----------|---------|------------|
| Load Balancer | Distribute traffic, health checks | Nginx, AWS ALB |
| API Servers | Handle requests, business logic | Java/Node.js |
| Redis Cache | Cache timelines, reduce DB load | Redis Cluster |
| Kafka | Queue for fan-out operations | Apache Kafka |
| Fan-out Workers | Distribute tweets to follower timelines | Background workers |
| Timeline Service | Build and serve user timelines | Microservice |
| PostgreSQL | Users, relationships | PostgreSQL |
| Cassandra | Tweets storage | Cassandra |

### Data Flow

**Write Path (Post Tweet):**
1. Client → Load Balancer → API Server
2. API Server → Store tweet in Cassandra
3. API Server → Publish to Kafka
4. Fan-out Workers → Update follower timelines in Redis

**Read Path (View Timeline):**
1. Client → Load Balancer → API Server
2. API Server → Check Redis cache
3. If miss → Timeline Service builds from Cassandra
4. Return tweets to client

### What to Say

> "Let me draw the high-level architecture. Starting from the top, clients connect through a load balancer for distribution and high availability. API servers handle requests and are stateless so we can scale horizontally..."

### ✅ Checklist
- [ ] Drew clear architecture diagram
- [ ] Included all necessary components
- [ ] Explained data flow (read and write paths)
- [ ] Components are appropriately scaled
- [ ] Justified technology choices

---

## 6️⃣ Deep Dives (10-15 min)

### What to Do
- Pick 2-3 important components
- Explain in detail
- Discuss challenges and solutions
- Show depth of understanding

### Common Deep Dive Topics

| Topic | What to Discuss |
|-------|-----------------|
| **Scaling** | How to handle 10x traffic? |
| **Caching** | What to cache, invalidation strategy |
| **Database** | Sharding, replication, consistency |
| **Key Algorithm** | Ranking, matching, recommendation |
| **Reliability** | Failures, retries, monitoring |

### Example Deep Dives

#### Fan-out Strategy (Twitter Timeline)

**Problem:** When a user tweets, how do we update followers' timelines?

**Fan-out on Write (Push):**
```
When user tweets:
1. Store tweet in Tweets DB
2. Get all followers from Follows DB
3. Push tweet_id to each follower's timeline cache

Pros: Fast reads (O(1) to get timeline)
Cons: Slow writes for users with millions of followers
```

**Fan-out on Read (Pull):**
```
When user requests timeline:
1. Get all users they follow
2. Fetch recent tweets from each
3. Merge and sort

Pros: Fast writes
Cons: Slow reads, more DB queries
```

**Hybrid Approach:**
```
- Normal users (< 10K followers): Fan-out on Write
- Celebrities (> 10K followers): Fan-out on Read
- Merge at read time
```

> "For fan-out, I'd use a hybrid approach. For most users, we push tweets to followers' timelines in the cache. But for celebrities with millions of followers, we fetch their tweets at read time to avoid the write amplification."

#### Caching Strategy

```
What to cache:
- User timelines (Redis sorted set)
- User profile data
- Tweet content

Cache invalidation:
- Timeline: Append new tweets, truncate old
- Profile: Invalidate on update
- Tweets: TTL-based, rarely change

Eviction: LRU with TTL
```

### What to Say

> "Let me deep dive into the caching strategy. We'll cache three things: timelines, profiles, and tweet content. For timelines, we use Redis sorted sets..."

### ✅ Checklist
- [ ] Selected appropriate topics to deep dive
- [ ] Explained mechanisms in detail
- [ ] Discussed trade-offs
- [ ] Showed practical solutions

---

## 7️⃣ Bottlenecks & Trade-offs (5 min)

### What to Do
- Identify potential bottlenecks
- Discuss how to address them
- Present trade-offs made
- Be ready for follow-up questions

### Common Bottlenecks

| Bottleneck | Solution |
|------------|----------|
| Database overload | Caching, read replicas, sharding |
| Single point of failure | Redundancy, failover |
| Hot spots | Consistent hashing, rate limiting |
| Network latency | CDN, regional deployment |
| Write amplification | Batch writes, async processing |

### Trade-offs to Discuss

| Decision | Trade-off |
|----------|-----------|
| Push vs Pull | Write latency vs Read latency |
| Cache-aside vs Write-through | Consistency vs Performance |
| SQL vs NoSQL | Consistency vs Scalability |
| Sync vs Async | Latency vs Reliability |

### Example Discussion

> "A key trade-off in this design is consistency vs latency for timelines. By using eventual consistency and caching, we can serve timelines in < 100ms, but users might see tweets with a slight delay. Given our requirements, this is acceptable."

### Follow-up Questions to Prepare

| Question | Example Answer |
|----------|----------------|
| "What if traffic 10x?" | "Add more API servers, increase cache size, add read replicas" |
| "What if cache fails?" | "Fall back to DB, use cache-aside pattern, gradual cache warming" |
| "What if celebrity tweets?" | "Hybrid fan-out, rate limiting, priority queues" |
| "How to handle spam?" | "Rate limiting, content filtering, user reporting" |

### ✅ Checklist
- [ ] Identified main bottlenecks
- [ ] Proposed solutions
- [ ] Discussed key trade-offs
- [ ] Ready for follow-up questions

---

## 📊 Summary Template

Before wrapping up, summarize:

> "To summarize, I've designed [System] with these key components:
> - [Component 1] for [purpose]
> - [Component 2] for [purpose]
> - [Component 3] for [purpose]
>
> Key trade-offs include [Trade-off 1] and [Trade-off 2].
>
> The design can handle [X QPS] with [Y latency], meeting our requirements for [availability/consistency]."

---

## ✅ Final Checklist

Before ending, verify you've covered:

- [ ] Requirements clearly defined and prioritized
- [ ] Back-of-envelope numbers make sense
- [ ] API covers all core functionality
- [ ] Database schema supports all operations
- [ ] Architecture diagram is clear
- [ ] Scaling approach is concrete
- [ ] Trade-offs discussed with justification
- [ ] Can answer follow-up questions

---

## 🧮 Quick Scoring Rubric

Use this for mock interview calibration.

| Dimension | Weak | Strong |
|---|---|---|
| Problem navigation | Jumps to architecture | Clarifies and prioritizes requirements first |
| Design quality | Components listed without flow | Clear read/write paths and ownership |
| Technical judgment | Tool names without rationale | Choices tied to constraints and bottlenecks |
| Communication | Unstructured explanation | Structured flow and concise summary |

---

## ⚠️ Common Pitfalls

- Spending too long on API details and missing deep dives
- Doing generic estimations that do not impact decisions
- Introducing advanced patterns too early
- Ignoring failure handling and degraded mode
- Skipping final architecture summary

---

## 🔁 Practice Variants

- **Global scale:** multi-region deployments and data locality concerns
- **Strict consistency:** inventory/payment correctness over latency
- **Cost-optimized:** reduce managed services while preserving core SLOs
- **Realtime-heavy:** polling vs SSE vs WebSocket trade-offs

---

## 🔗 Related Resources

- [DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md) - Full HLD template
- [hld-template.md](../templates/hld-template.md) - Practice template
- [hld-components-map.md](../cheatsheets/hld-components-map.md) - Component selection
- [trade-offs-matrix.md](../cheatsheets/trade-offs-matrix.md) - Trade-offs guide

---

*Follow this checklist to systematically cover all aspects of system design! 🏗️*
