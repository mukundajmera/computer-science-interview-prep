# Read Scaling Interview Q&A

1. **How do you guarantee read-your-writes for profile edits?**
   By issuing a read-your-writes (RYW) token upon saving the profile edit. The token represents the transaction ID or timestamp. When the client subsequently reads the profile, it includes this token, and the router ensures the request goes to the primary or a replica that has caught up to that token.

2. **What metric tells you your cache strategy is failing?**
   A low cache hit ratio coupled with high database CPU/IO utilization, or a high cache eviction rate (thrashing) indicating the cache size is too small for the working set.

3. **How do you prevent stampede when a hot key expires?**
   Use request collapsing (singleflight) to ensure only one thread queries the database while others wait. Alternatively, use probabilistic early expiration or a background thread to refresh the cache before the hard TTL expires.

4. **When do read replicas stop being enough?**
   When the dataset size exceeds a single machine's storage capacity, or when the write volume is so high that the primary cannot replicate to the read replicas fast enough without unacceptable lag, or when the primary itself is bottlenecked on writes. At this point, sharding is required.

5. **Which data should never be edge-cached?**
   Highly sensitive personal data (e.g., banking details, private messages) or data that is extremely real-time and specific to a single user without broad appeal, as caching it at the edge wastes resources and poses security risks if misconfigured.

6. **Explain the difference between fan-out-on-read and fan-out-on-write.**
   Fan-out-on-write pre-computes data (like a news feed) and pushes it to followers' inboxes when a new item is created. Fan-out-on-read pulls data from all the people a user follows only when the user requests their feed.

7. **How does a CDN improve read performance?**
   It caches static assets (images, JS, CSS) at edge locations geographically closer to users, reducing network latency and offloading traffic from the origin servers.

8. **What is replica lag and what causes it?**
   The time difference between a write occurring on the primary and that same write being visible on a read replica. It's caused by network latency, high write volume on the primary, or slow replay of the replication log on the replica.

9. **How do you handle a scenario where all read replicas fail?**
   The system must either route all read traffic to the primary (which risks overwhelming it) or implement load shedding and circuit breakers to serve degraded responses or errors until replicas recover.

10. **What is the write break-even point in social feeds?**
    It's the threshold of followers at which pushing a post to every follower's timeline (fan-out-on-write) becomes too expensive computationally and storage-wise, necessitating a switch to fan-out-on-read for that user.

11. **How can local caching (e.g., inside the app server) improve upon remote caching (e.g., Redis)?**
    Local caching avoids network hops entirely, offering sub-millisecond latency. It is extremely effective for defending against hot keys, though it suffers from cache incoherence across servers and lower memory limits.

12. **Describe how a Bloom filter can assist read operations.**
    Before checking an on-disk database or a slow storage engine for a key's existence, a Bloom filter can be queried in memory. If it says 'no', we skip the expensive read. If it says 'yes', we perform the read (with a small chance of a false positive).

13. **Why might we use different TTLs for different types of cached data?**
    Static data like a company logo might have a TTL of months, while stock prices might have a TTL of seconds. Tailoring TTLs balances freshness requirements with cache hit rates.

14. **How do we test for race conditions in a request collapsing implementation?**
    By using concurrent load testing tools to hammer a specific key simultaneously and asserting that only a single database query is executed, usually by mocking the DB and counting invocations.

15. **What role does database indexing play in read scaling before caching is considered?**
    Proper indexing reduces the time complexity of database reads from O(N) to O(log N) or O(1). This is the cheapest and most effective first step for read scaling, as an unindexed query can bring down a DB regardless of caches.
