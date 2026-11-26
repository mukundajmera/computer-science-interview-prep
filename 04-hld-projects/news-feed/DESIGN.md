# News Feed System Design

Complete high-level design for a scalable social media news feed system.

---


## Requirements

### Functional Requirements
- Core user flow for News Feed System.

### Non-Functional Requirements
- High availability, low latency, fault tolerance.

## Back-of-envelope Estimation

### Traffic
| Metric | Calculation | Result |
|---|---|---|
| DAU | Given | 300M |
| Avg QPS | 300M DAU x 20 reads / 86,400 s | 69K avg QPS |
| Peak QPS | 69K avg QPS x 3 peak | 207K peak QPS |

### Storage
| Metric | Calculation | Result |
|---|---|---|
| Daily Storage | 300M DAU x 2 posts x 1 KB = 600 GB/day |

## API Contracts

### Endpoints
```http
POST /api/v1/posts
GET /api/v1/feed
```

## Data Model

### Schema
- Primary Key: `post_id`
- Partition Key: `user_id`


## System Architecture

```mermaid
flowchart TB
    subgraph Clients
        Web[Web App]
        Mobile[Mobile App]
        direction TB
    end
    
    subgraph Edge["Edge Layer"]
        CDN[CDN - CloudFront]
        DNS[DNS + GeoDNS]
    end
    
    subgraph Gateway["API Gateway Layer"]
        LB[Load Balancer]
        RL[Rate Limiter]
        Auth[Auth Service]
    end
    
    subgraph Services["Core Services"]
        PostService[Post Service]
        FeedService[Feed Service]
        FollowService[Follow Service]
        FanoutService[Fanout Service]
        RankingService[Ranking Service]
        NotificationService[Notification Service]
    end
    
    subgraph Queue["Message Queue"]
        Kafka[Kafka Cluster]
        FanoutTopic[Fanout Topic]
        NotifTopic[Notification Topic]
    end
    
    subgraph Cache["Caching Layer"]
        FeedCache[(Feed Cache<br/>Redis Sorted Sets)]
        PostCache[(Post Cache<br/>Redis)]
        UserCache[(User Cache<br/>Redis)]
        CountCache[(Count Cache<br/>Redis)]
    end
    
    subgraph Storage["Storage Layer"]
        PostDB[(Posts DB<br/>Cassandra)]
        GraphDB[(Social Graph<br/>Cassandra)]
        UserDB[(User DB<br/>PostgreSQL)]
        MediaStore[(Media Store<br/>S3)]
    end
    
    subgraph ML["ML Pipeline"]
        FeatureStore[(Feature Store)]
        RankingModel[Ranking Model]
    end
    
    Web --> CDN
    Mobile --> CDN
    CDN --> DNS
    DNS --> LB
    LB --> RL
    RL --> Auth
    Auth --> PostService
    Auth --> FeedService
    Auth --> FollowService
    
    PostService --> Kafka
    Kafka --> FanoutService
    Kafka --> NotificationService
    FanoutService --> FeedCache
    
    FeedService --> FeedCache
    FeedService --> PostCache
    FeedService --> PostDB
    FeedService --> RankingService
    
    RankingService --> FeatureStore
    RankingService --> RankingModel
    
    PostService --> PostDB
    PostService --> PostCache
    PostService --> MediaStore
    FollowService --> GraphDB
    FollowService --> UserCache
    
    style FeedCache fill:#69db7c
    style PostCache fill:#69db7c
    style Kafka fill:#ffa94d
```

**Architecture Notes:**
- **Fan-out on Write**: Normal users' posts pushed to followers' feed caches
- **Fan-out on Read**: Celebrity posts (>10K followers) pulled at read time
- **Hybrid Approach**: Combines write-heavy for most, read-heavy for celebrities
- **Feed Cache**: Redis Sorted Sets with post IDs sorted by timestamp/rank
- **Social Graph**: Cassandra for high-throughput follower lookups

---

## Sequence Diagrams

### Write Path: Post Creation with Fan-out

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant API as API Gateway
    participant PostService
    participant MediaStore as S3
    participant PostDB as Cassandra
    participant Kafka
    participant FanoutWorker
    participant GraphDB as Social Graph
    participant FeedCache as Redis
    
    User->>API: POST /posts {content, media}
    API->>PostService: Create post request
    
    alt Has Media
        PostService->>MediaStore: Upload media
        MediaStore-->>PostService: Media URLs
    end
    
    PostService->>PostDB: Save post
    PostDB-->>PostService: Post ID
    
    PostService->>Kafka: Publish PostCreated event
    PostService-->>User: 201 Created {postId}
    
    Note over Kafka,FeedCache: Async Fan-out Processing
    
    Kafka->>FanoutWorker: PostCreated event
    FanoutWorker->>GraphDB: Get followers(userId)
    GraphDB-->>FanoutWorker: Follower IDs (paginated)
    
    alt User has < 10K followers (Normal User)
        loop For each follower batch (1000)
            FanoutWorker->>FeedCache: ZADD feed:{followerId} timestamp postId
        end
    else User has >= 10K followers (Celebrity)
        FanoutWorker->>FeedCache: Add to celebrity_posts:{userId}
        Note over FanoutWorker: Skip fan-out, merge at read time
    end
    
    FanoutWorker->>Kafka: Publish NotifyFollowers event
```

### Read Path: Get Feed with Ranking

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant API as API Gateway
    participant FeedService
    participant FeedCache as Redis Feed
    participant PostCache as Redis Post
    participant PostDB as Cassandra
    participant GraphDB as Social Graph
    participant RankingService
    
    User->>API: GET /feed?cursor=...&limit=20
    API->>FeedService: Get feed request
    
    FeedService->>FeedCache: ZREVRANGE feed:{userId} cursor limit
    FeedCache-->>FeedService: Post IDs from pre-computed feed
    
    FeedService->>GraphDB: Get followed celebrities
    GraphDB-->>FeedService: Celebrity user IDs
    
    loop For each celebrity
        FeedService->>FeedCache: ZREVRANGE celebrity_posts:{celebId}
        FeedCache-->>FeedService: Recent celebrity post IDs
    end
    
    FeedService->>FeedService: Merge and deduplicate post IDs
    
    FeedService->>PostCache: MGET post:{id1}, post:{id2}...
    PostCache-->>FeedService: Cached posts
    
    alt Cache miss for some posts
        FeedService->>PostDB: Fetch missing posts
        PostDB-->>FeedService: Post data
        FeedService->>PostCache: Cache fetched posts
    end
    
    FeedService->>RankingService: Rank posts for user
    RankingService-->>FeedService: Ranked post IDs
    
    FeedService->>FeedService: Build response with pagination cursor
    FeedService-->>User: {posts[], nextCursor}
```

### Follow/Unfollow Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant API
    participant FollowService
    participant GraphDB
    participant FeedCache as Redis
    participant Kafka
    
    User->>API: POST /users/{targetId}/follow
    API->>FollowService: Follow request
    
    FollowService->>GraphDB: Check existing relationship
    GraphDB-->>FollowService: Not following
    
    FollowService->>GraphDB: Create follow edge
    GraphDB-->>FollowService: Success
    
    FollowService->>FollowService: Update follower/following counts
    
    alt Target is normal user
        FollowService->>Kafka: Publish FollowCreated event
        Note over Kafka: Backfill worker adds recent posts to follower's feed
    else Target is celebrity
        Note over FollowService: No backfill needed - merged at read time
    end
    
    FollowService-->>User: 200 OK
    
    Note over Kafka,FeedCache: Async Backfill (for normal users)
    Kafka->>FeedCache: ZADD feed:{userId} with target's recent posts
```

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ FOLLOW : follows
    USER ||--o{ FOLLOW : followed_by
    POST ||--o{ LIKE : receives
    POST ||--o{ COMMENT : has
    POST ||--o{ MEDIA : contains
    USER ||--o{ LIKE : gives
    USER ||--o{ COMMENT : writes

    USER {
        uuid user_id PK
        string username UK
        string email UK
        string display_name
        string profile_image_url
        string bio
        int follower_count "Denormalized"
        int following_count "Denormalized"
        int post_count "Denormalized"
        boolean is_celebrity "10K+ followers"
        timestamp created_at
    }

    POST {
        uuid post_id PK
        uuid user_id FK
        text content
        int like_count "Denormalized"
        int comment_count "Denormalized"
        int share_count "Denormalized"
        string visibility "public/followers/private"
        timestamp created_at
        timestamp updated_at
    }

    MEDIA {
        uuid media_id PK
        uuid post_id FK
        string media_type "image/video/gif"
        string storage_url
        string thumbnail_url
        int width
        int height
        int duration_ms "For video"
    }

    FOLLOW {
        uuid follower_id PK "FK to USER"
        uuid following_id PK "FK to USER"
        timestamp created_at
    }

    LIKE {
        uuid user_id PK "FK to USER"
        uuid post_id PK "FK to POST"
        timestamp created_at
    }

    COMMENT {
        uuid comment_id PK
        uuid post_id FK
        uuid user_id FK
        uuid parent_comment_id FK "For replies"
        text content
        int like_count
        timestamp created_at
    }

    FEED_CACHE {
        uuid user_id PK "Feed owner"
        uuid post_id "Sorted by score"
        float score "Timestamp or rank"
        timestamp cached_at
    }

    CELEBRITY_POSTS {
        uuid celebrity_user_id PK
        uuid post_id
        timestamp created_at
    }
```

**Schema Notes:**
- **USER Table**: PostgreSQL for ACID, denormalized counts for performance
- **POST Table**: Cassandra, partitioned by `user_id` for user timeline queries
- **FOLLOW Table**: Cassandra, two tables for bidirectional queries:
  - `followers_by_user(user_id, follower_id)` - who follows me
  - `following_by_user(user_id, following_id)` - who I follow
- **FEED_CACHE**: Redis Sorted Set, not persisted to disk
- **Indexes**:
  - `POST(user_id, created_at DESC)` for user timeline
  - `FOLLOW(following_id)` for fan-out
  - `COMMENT(post_id, created_at)` for comment threads

---

## Trade-offs

### Fan-out on Write vs Read

| Aspect | Fan-out on Write | Fan-out on Read |
|--------|-----------------|-----------------|
| Write latency | Higher | Lower |
| Read latency | Lower | Higher |
| Storage | Higher | Lower |
| Celebrity handling | Poor | Good |
| **Recommendation** | Use for normal users | Use for celebrities |

### Consistency vs Availability

- **Choice**: Eventual consistency
- **Trade-off**: New posts may take seconds to appear in all feeds
- **Benefit**: Higher availability and throughput

---

## Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Feed Cache | Redis Sorted Sets | Pre-computed feeds |
| Post Storage | Cassandra | Scalable post storage |
| Social Graph | Neo4j/Cassandra | Follow relationships |
| Message Queue | Kafka | Async fan-out |
| Ranking | ML Service | Feed personalization |

---

## 🤖 GenAI Extension

> How could this system be augmented with LLMs? Below are interview-ready ideas that connect this classical HLD to GenAI patterns. For full GenAI system designs, see [06-genai-systems/](../../06-genai-systems/).

### Potential LLM-Powered Features

| Feature | Description | GenAI Components |
|---------|-------------|-----------------|
| **Post Summarization** | Summarize long threads or trending topics (e.g., "Trending: AI debate — key viewpoints are…") | Chunker, prompt builder, LLM service |
| **AI-Powered Content Moderation** | Detect harmful, misleading, or policy-violating posts using LLM classifiers | Safety filter, LLM classifier |
| **Smart Feed Explanations** | Explain why a post appears in a user's feed (e.g., "Shown because 5 people you follow engaged with this") | Prompt builder, LLM service |
| **Content Creation Assistant** | Help users draft posts with AI suggestions, hashtag recommendations, and tone adjustments | Prompt builder, conversation memory, LLM service |

### Integration Points

```
Existing News Feed Pipeline:
  Create Post → Fan-out → Feed Cache → Render Feed

With GenAI Extension:
  Create Post → Fan-out → Feed Cache → Render Feed
       │                                    │
       └→ Content moderation (LLM, async)   └→ Feed explanations (LLM, on demand)
       └→ Topic extraction (LLM) → Trending summarization
```

### Trade-offs

- **Moderation latency**: Posts should appear quickly — run moderation async, remove violating posts retroactively
- **Summarization freshness**: Trending summaries become stale quickly — regenerate every few minutes, cache aggressively
- **Cost**: Per-post moderation at billions of posts/day is expensive — use lightweight classifier first, LLM for borderline cases

### Learn More

- [GenAI HLD Projects: Content Moderation Pipeline](../../06-genai-systems/02-llm-hld-projects/) — Full moderation system design
- [GenAI LLD: Safety Filter & Policy Engine](../../06-genai-systems/01-llm-lld-projects/safety-filter-policy-engine/) — Content filtering component
- [GenAI Concepts: Safety & Governance](../../06-genai-systems/00-concepts/safety-governance/) — Safety strategies for user-generated content


## Bottlenecks and Failure Modes

| Component | Failure Mode | Mitigation | Impact | Detection | Recovery |
|---|---|---|---|---|---|
| Feed Cache | Memory Full | Eviction policies (LRU) | Increased latency | Cache hit rate drop | Add cache nodes |
| Fan-out Worker | Queue Backlog | Priority queues (active users) | Delayed feed updates | Queue depth alarm | Scale workers |
| Graph DB | Slow Queries | Read replicas, caching | Slower feed generation | Query latency metrics | Add read replicas |
| Post DB | Node Down | Quorum reads/writes | Minimal, handled transparently | Node heartbeat failure | Gossip protocol sync |
| CDN | Cache Miss Spike | Cache warming strategies | Increased origin load | Origin traffic metrics | Tune cache headers |
| API Gateway | Instance Crash | Auto-scaling group | Brief latency spike | 5xx rate spikes | Auto-replace |

## Scaling Stages

- **10K Users**: Single monolith, simple DB, basic caching.
- **1M Users**: Microservices, robust cache, read replicas.
- **100M+ Users**: Sharded databases, globally distributed edge nodes, event streaming.


---
**Real-world reference**: See how Twitter solved this in the [Twitter case study](../../case-studies/twitter-timeline/)
