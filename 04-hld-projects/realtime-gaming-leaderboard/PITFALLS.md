# Real-Time Gaming Leaderboard - Common Pitfalls

## 1. Relying Exclusively on RDBMS
- **Signal:** Candidate proposes MySQL/PostgreSQL with `INDEX(score)` and uses `SELECT COUNT(*) FROM leaderboard WHERE score > my_score` to find user rank.
- **Root Cause:** Misunderstanding of database index scanning. While finding the top 10 is fast (`ORDER BY score DESC LIMIT 10`), finding a specific rank requires traversing the index to count all elements greater than the target.
- **Mitigation:** Guide the candidate to calculate the Big-O complexity of their read query. At 25 million records, an $O(N)$ index scan for every user requesting their rank will immediately crash the database.
- **Validation:** Look for the candidate proactively switching to an $O(\log N)$ data structure like a SkipList (Redis Sorted Set).

## 2. Ignoring Durability in In-Memory Stores
- **Signal:** Candidate uses Redis Sorted Sets for everything but does not persist the data elsewhere.
- **Root Cause:** Treating Redis as a primary, durable database without understanding the risks of catastrophic memory loss or snapshot (RDB) / AOF corruption.
- **Mitigation:** Ask, "What happens if the Redis cluster loses power in the middle of a tournament?"
- **Validation:** The candidate should introduce a durable, asynchronous write path (e.g., via Kafka to MySQL) to allow leaderboard rebuilding.

## 3. Naive Hash Sharding
- **Signal:** When asked to scale to 500M users, the candidate proposes sharding Redis by `hash(user_id) % N`.
- **Root Cause:** Treating a leaderboard like a standard key-value store. 
- **Mitigation:** Ask, "If you have 10 shards, how do you find the global Top 10? How do you find User A's absolute global rank?"
- **Validation:** The candidate realizes hash sharding breaks global ordering and pivots to score-range sharding.

## 4. Failing to Handle Tie-Breakers Properly
- **Signal:** Candidate uses standard `ZINCRBY` without modifying the score structure.
- **Root Cause:** Forgetting that Redis sorts identical scores lexicographically by the member name (`user_id`), not chronologically.
- **Mitigation:** Ask, "If Alice and Bob both score 100 points, but Alice scored it yesterday and Bob scored it today, who is ranked higher in your system?"
- **Validation:** The candidate introduces a composite score combining the integer score with an inverted timestamp fractional component.

## 5. ZINCRBY with Fractional Timestamps
- **Signal:** Candidate proposes using `ZINCRBY` to add points while using a fractional timestamp.
- **Root Cause:** If the score is `points + inverted_timestamp`, simply adding `new_points` via `ZINCRBY` will result in `(old_points + inverted_timestamp_old) + new_points`. The timestamp portion is now stale (it reflects the time of the *first* points earned, not the most recent).
- **Mitigation:** Ask, "If a user scores again, should their tie-breaker timestamp be the time they scored their *first* point, or their *most recent* point?"
- **Validation:** The candidate realizes they must execute a read-modify-write loop (often via a Lua script in Redis) to extract the old integer score, add the new points, generate a new fractional timestamp, and execute a `ZADD`.

## 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
- [Rubric](RUBRIC.md)
