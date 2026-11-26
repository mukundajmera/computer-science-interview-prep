# Real-Time Gaming Leaderboard - Strong Answer

## Narrative Example

*Here is an example of how a strong candidate narrates their system design during an interview.*

---

**1. Requirements & Scoping**

> **Say:** "To design this real-time gaming leaderboard, I'll focus on three core operations: updating a player's score, fetching the global top 10, and fetching a player's exact rank along with a few players above and below them. Because it's a competitive game, I'm assuming we need strict tie-breakers where the first player to achieve a score ranks higher. For scale, you mentioned 25 million monthly active players peaking at 2,500 write queries per second, with a P99 latency target of under 50 milliseconds. We also need to ensure data isn't lost if a server crashes."

**2. Sizing & The Core Trade-off**

> **Say:** "Let's look at the storage and read-path requirements. If we use a traditional relational database like MySQL, updating scores and getting the Top 10 is easy. However, finding a specific user's absolute rank requires an index scan to count all players with a higher score. At 25 million users, that $O(N)$ query will easily exceed our 50ms latency budget and crush the database CPU."

> **Say:** "Because of this, I propose using an in-memory data store. Specifically, Redis Sorted Sets. Redis uses a combination of a Hash Table and a SkipList, which allows $O(\log N)$ updates and, crucially, $O(\log N)$ absolute rank queries via `ZREVRANK`."

> **Say:** "To size this: 25 million users, storing a 24-byte user ID and an 8-byte score, is around 800MB. Factoring in Redis's SkipList pointer overhead (about 2.5x), we are looking at roughly 2GB of RAM. This easily fits on a single, modestly sized Redis node. Furthermore, a single node can handle up to 100,000 QPS, which gives us massive headroom over our 2,500 peak write requirement."

**3. The Tie-Breaker Problem**

> **Say:** "Redis Sorted Sets sort by the floating-point score, and if there's a tie, they sort lexicographically by the member string. To fix this and meet the 'first-to-score wins' requirement, I will use a composite score. I will take the integer points and add a fractional component representing the inverted timestamp. For example, if we use the formula `score + (1.0 - (timestamp / max_time))`, the player who scores first gets a slightly higher fractional value, guaranteeing monotonic ordering."

**4. Architecture & Durability**

> **Say:** "While Redis gives us the speed, it's volatile. If the node restarts, we could lose tournament data. To solve this, I'll design a hybrid architecture."

> **Say:** "When the Gaming Client hits the API Gateway with a win, the request routes to the Score Service. The Score Service calculates the composite score and synchronously updates the Redis Primary using a `ZADD` command. Immediately after, it drops an event payload onto a Kafka topic and returns a 200 OK to the client. We use Kafka because it's durable and handles high write throughput flawlessly. In the background, a DB Persist Worker consumes from Kafka, batches the updates, and writes them to a MySQL database."

> **Say:** "If our Redis cluster completely fails, we can spin up a new one and run a recovery script that reads the canonical state from MySQL and replays it into the new Redis cluster."

**5. Scaling to 500 Million Users (Follow-up)**

> **Say:** "If the game explodes in popularity and we hit 500 million players, we now need about 65GB of RAM and might exceed a single node's compute limits. At this point, we must shard the Redis cluster."

> **Say:** "I would explicitly avoid Hash Sharding (by `user_id`) because finding the global top 10 would require a scatter-gather query across all shards, and finding an absolute rank becomes incredibly slow. Instead, I would use Score-Range sharding. We would bucket the shards by score (e.g., Shard A: 100k+ points, Shard B: 50k-99k points). To find the Top 10, we just query Shard A. To find a user's rank, we look up their score to find their shard, calculate their local rank in that shard, and then add the total element count of all higher shards, which we can cache in $O(1)$ time."

---

## 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
- [Rubric](RUBRIC.md)
