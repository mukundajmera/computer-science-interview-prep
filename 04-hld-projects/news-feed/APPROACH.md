# Design Approach for News Feed System

---

## 1. Requirements Clarification

### Assumptions with Numbers

| Metric | Value |
|--------|-------|
| DAU | 200 million |
| Posts/day | 400 million (2 per user) |
| Feed requests/day | 2 billion |
| Average followers | 200 |
| Celebrity threshold | 1M+ followers (1% of users) |

---

## 2. Back-of-the-Envelope Estimation

### Traffic Calculations

```
Posts per second: 400M / 86400 = ~4,600 posts/sec
Feed reads per second: 2B / 86400 = ~23,000 reads/sec
Peak (3x): ~70,000 feed reads/sec
```

### Storage Calculations

```
Per Post: ~1 KB
Daily posts: 400M * 1 KB = 400 GB/day
Yearly: ~146 TB
Feed cache per user: 1000 posts * 8 bytes (post IDs) = 8 KB
Total feed cache: 200M users * 8 KB = 1.6 TB
```

---

## 3. API Design

### Create Post
```
POST /api/v1/posts
Request: { "content": "Hello world!", "mediaIds": [] }
Response: { "postId": "post123", "createdAt": "..." }
```

### Get Home Feed
```
GET /api/v1/feed?cursor={cursor}&limit=20
Response: { 
  "posts": [...], 
  "nextCursor": "...",
  "hasMore": true 
}
```

### Follow/Unfollow
```
POST /api/v1/follow
Request: { "targetUserId": "user456" }
```

---

## 4. Data Model

### Posts Table
```
posts {
  post_id:     uuid (PK)
  user_id:     uuid (FK)
  content:     text
  created_at:  timestamp
  media_ids:   list<uuid>
  like_count:  int
  share_count: int
}
```

### User Follows Table
```
user_follows {
  follower_id:  uuid (PK)
  followee_id:  uuid (PK)
  created_at:   timestamp
}
```

### User Feed Cache (Redis)
```
feed:{user_id} -> Sorted Set of post_ids (score = timestamp)
```

---

## 5. High-Level Architecture

### Fan-out Strategies

**Fan-out on Write:**
- When user posts, push to all followers' feeds
- Pros: Fast feed reads (pre-computed)
- Cons: Slow writes for celebrities, storage intensive

**Fan-out on Read:**
- When user reads feed, fetch from all followees
- Pros: Fast writes, less storage
- Cons: Slow reads, high latency

**Hybrid Approach (Recommended):**
- Fan-out on write for regular users (< 10K followers)
- Fan-out on read for celebrities (> 10K followers)
- Merge at read time

---

## 6. Deep Dives

### 6.1 Feed Ranking

```
Score = base_time_score + engagement_boost + relationship_boost

Where:
- base_time_score = post_timestamp (recency)
- engagement_boost = log(likes + shares + comments)
- relationship_boost = interaction_history_with_author
```

### 6.2 Cache Strategy

```
Feed Cache (Redis Sorted Set):
- Key: feed:{user_id}
- Value: post_ids with timestamp scores
- Size: Top 1000 posts per user
- TTL: 24 hours

Post Cache (Redis Hash):
- Key: post:{post_id}
- Value: Post content and metadata
- TTL: 1 hour
```

### 6.3 Handling Celebrities

```
Celebrity Detection:
- Users with > 10K followers
- Skip fan-out on write
- Fetch their posts at read time

Read Path for Feed:
1. Get pre-computed feed from cache
2. Fetch recent posts from followed celebrities
3. Merge and rank
4. Return top N posts
```

---

## 7. Bottlenecks and Mitigations

| Bottleneck | Mitigation |
|------------|------------|
| Celebrity writes | Hybrid fan-out approach |
| Feed cache size | LRU eviction, cold storage |
| Hot user feeds | Cache replication |
| Real-time updates | WebSocket for active users |

---

## 8. Evolution Plan

**v1-basic:** Pull-based, query database on each request
**v2-scaled:** Fan-out on write, Redis caching, pagination
**v3-distributed:** Hybrid fan-out, ML ranking, multi-region
