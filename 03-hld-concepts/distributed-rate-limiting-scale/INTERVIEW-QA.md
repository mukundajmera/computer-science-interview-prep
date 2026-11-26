# Distributed Rate Limiting at Scale - Interview Q&A

These staff-level questions test the depth of understanding regarding distributed systems, concurrency, clock synchronization, and high-availability design patterns in the context of rate limiting.

### 1. How does the Sliding Window Counter handle bursts at the edge of window boundaries better than a Fixed Window, without the memory cost of a Sliding Window Log?
**Candidate should explain:**
- The Fixed Window algorithm allows double the traffic if a burst occurs right at the boundary (e.g., 100 requests at 1:59.99 and 100 at 2:00.01).
- The Sliding Window Log solves this but requires O(N) memory, tracking every timestamp, which fails at high QPS.
- The Sliding Window Counter uses O(1) memory, keeping only two counters (current and previous window). It interpolates the rate by calculating `(Previous Count * overlap percentage) + Current Count`.
**Say:** "The Sliding Window Counter uses a weighted interpolation between the previous and current minute's counters based on how far we are into the current minute, giving O(1) memory usage while drastically smoothing out boundary bursts compared to fixed windows."

### 2. When implementing rate limiting using Redis, why is a GET-then-SET approach dangerous, and how do you fix it?
**Candidate should explain:**
- GET-then-SET is vulnerable to race conditions (read-modify-write hazard). Two concurrent requests might read the same remaining token count and both decrement it, allowing more traffic than the limit permits.
- Using Redis transactions (`MULTI/EXEC`) or `INCR` commands can help, but complex logic (like checking limits before decrementing) requires atomicity.
**Say:** "To ensure atomicity, we encapsulate the check-and-decrement logic within a Redis Lua script. Since Redis executes Lua scripts atomically on its single thread, it guarantees no other operation can interleave, preventing race conditions."

### 3. At 1 Million QPS, making a network call to Redis for every request introduces too much latency. How do you design around this?
**Candidate should explain:**
- The critical path must be decoupled from remote network calls.
- Introducing a Local Memory Token Batching architecture. Gateways reserve a batch of tokens (e.g., 100) from Redis and serve requests locally.
**Say:** "We use a hybrid local-global architecture. Gateways fetch a batch of tokens asynchronously and store them in local memory. Requests consume tokens locally in sub-microseconds, and we replenish the batch in the background when it runs low, completely removing Redis from the critical path."

### 4. In a local token batching architecture, what happens if a single user's traffic is perfectly distributed across 1,000 gateway instances, but their global limit is only 500 QPS?
**Candidate should explain:**
- This is the "Thundering Herd" or fragmentation problem of batching. If 1,000 gateways all try to reserve a batch of 10 tokens for a 500 QPS limit, they will over-allocate or exhaust the limit instantly.
- Solutions include dynamic batch sizing (smaller batches for lower limits or distributed traffic) or sticky routing (routing the same user to the same gateway/subset of gateways).
**Say:** "If traffic is highly distributed, static batch sizes lead to over-allocation. We can mitigate this by implementing sticky sessions at the load balancer based on the user ID, or by dynamically shrinking the batch size when we detect high contention or low global limits."

### 5. How does Clock Drift across different gateway nodes affect a distributed rate limiter, and how can we mitigate it?
**Candidate should explain:**
- If Node A's clock is 2 seconds ahead of Node B, they might disagree on which time window a request belongs to, potentially allowing bursts or dropping valid requests.
- Mitigation involves relying on a single source of truth for time, or using NTP.
**Say:** "In a distributed system, relying on local gateway clocks is risky due to drift. We should use the central Redis server's clock as the source of truth for window boundaries by utilizing Redis's `TIME` command or TTL expirations, rather than the gateway's system time."

### 6. What is your strategy for handling a Redis network partition or complete failure? Do you fail open or fail closed?
**Candidate should explain:**
- Failing closed means denying all traffic, which destroys availability.
- Failing open means allowing all traffic, which might overwhelm downstream databases and cause a cascading failure.
- A better approach is graceful degradation.
**Say:** "I would degrade gracefully by falling back to local, in-memory rate limiting on the gateways. We divide the global limit by the number of active gateway nodes to enforce a 'fair share' limit locally until Redis recovers, protecting downstream services while maintaining partial availability."

### 7. How do you handle multi-region active-active rate limiting where users might switch regions?
**Candidate should explain:**
- Synchronizing every request across regions is too slow (high cross-region latency).
- Eventual consistency is usually required. Regions can have local Redis clusters that asynchronously sync with a global cluster (e.g., CRDTs or Redis Enterprise active-active).
**Say:** "For multi-region, we can't do synchronous global checks. We use local Redis clusters in each region and synchronize them asynchronously. If a user switches regions rapidly, we accept a brief period of potential over-limit usage as a tradeoff for low latency."

### 8. What is the difference between throttling and rate limiting, and how might you implement backpressure?
**Candidate should explain:**
- Rate limiting drops requests (HTTP 429). Throttling might delay or queue them.
- Backpressure involves signaling to the upstream client to slow down.
**Say:** "Rate limiting typically rejects requests outright with a 429 status and a 'Retry-After' header. Throttling might queue requests using a Leaky Bucket or Message Queue to smooth out the burst. Returning 429s with retry headers is a standard way to apply backpressure to well-behaved clients."

### 9. If you are using a Sliding Window Counter, how do you handle a malicious user who sends a massive burst precisely at the millisecond the window rolls over?
**Candidate should explain:**
- The weighted formula smooths out standard traffic, but a massive burst at the start of a window combined with a burst at the end of the previous window can still exceed the limit momentarily.
- To prevent this, multiple limits are often layered.
**Say:** "While the sliding window approximation smooths most traffic, to completely prevent malicious micro-bursts, we should layer rate limits. For example, applying a limit of 10,000 per minute globally, but pairing it with a strict limit of 200 per second to clamp instantaneous spikes."

### 10. In your local batching design, how do you ensure the background async replenishment thread doesn't create a stampede on Redis if many gateways run low simultaneously?
**Candidate should explain:**
- If many gateways hit their low-water mark at the exact same time, they will all hammer Redis.
- Mitigation involves introducing jitter (randomness) to the threshold or the replenishment interval.
**Say:** "To prevent synchronized thundering herds on Redis, we introduce 'jitter' to the batch replenishment threshold. Instead of every gateway fetching when tokens hit exactly 20%, we randomize the threshold between 15% and 25%, spreading out the Redis calls over time."
