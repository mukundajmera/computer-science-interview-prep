# Real-Time Gaming Leaderboard - Follow-Up Questions

## Follow-up questions

1. **How do you handle a scenario where 500 million users participate?**
   - *Probe:* A single Redis node can only hold so much memory and handle ~100k QPS.
   - *Expected:* Shift from a single Redis node to a cluster utilizing Score-Range sharding.

2. **How does your design change if the leaderboard is historical (all-time) instead of monthly?**
   - *Probe:* A monthly tournament allows us to drop the Redis key at the end of the month. An all-time leaderboard grows indefinitely.
   - *Expected:* Active users remain in a fast Redis cache, while inactive users are flushed to a slower storage tier (e.g., Cassandra or heavily sharded MySQL) to save RAM. The read path must query both.

3. **How do you handle bots or cheaters injecting fake scores?**
   - *Probe:* If a user submits a score of 9,999,999 directly to the API, how is it validated?
   - *Expected:* The `Score Service` should not accept raw scores from clients. It should accept verified match telemetry (e.g., signed payloads, server-side validation of match outcomes) and update the score internally. Introduce anomaly detection on the Kafka event stream.

4. **What happens if the primary Redis node crashes and the replica hasn't synced yet?**
   - *Probe:* Redis asynchronous replication can lead to data loss during failover.
   - *Expected:* Since we have an asynchronous durable path to MySQL via Kafka, we can write a reconciliation script. The script compares the new Redis primary's state against the MySQL source of truth and replays any missing updates.

5. **How do you handle the "Hot Shard" problem in Score-Range sharding?**
   - *Probe:* If we shard by score (e.g., 0-100, 101-500), the lowest bucket will have massive write contention because every new player starts at 0.
   - *Expected:* For highly dense score buckets (like 0-100), we further subdivide the shard using Hash Sharding (e.g., `bucket_0_100_shard_1`, `bucket_0_100_shard_2`). Since rank within the lowest bucket rarely matters for top-tier competitive play, the slight latency penalty of a scatter-gather query on the lowest bucket is an acceptable trade-off.

## Variants and extensions

- **Historical Tournaments:** Provide an API to query a user's rank in a tournament from 3 years ago. (Requires querying MySQL/Cold storage, not Redis).
- **Geo-localized Leaderboards:** "Top in North America" vs "Top in Asia". (Requires maintaining parallel Sorted Sets per region).
- **Friends-only Leaderboards:** Show the user's rank compared strictly to their social graph. (Often handled by querying the user's friends list, doing an $O(1)$ score lookup for each friend, and sorting in memory on the application server).

## Interviewer probes to prepare

- "Walk me through the exact math of how you will store the timestamp inside a double-precision float without losing the integer score data."
- "Draw the sequence diagram for a Redis node failure and the subsequent recovery process."

## 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Design](DESIGN.md)
