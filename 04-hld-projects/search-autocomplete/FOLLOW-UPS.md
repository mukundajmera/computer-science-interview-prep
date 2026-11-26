# Search Autocomplete - Follow-Up Questions

## Follow-up questions

1. **How do you handle trending searches that need to appear in minutes, not days?**
   - Combine a fast-path streaming aggregator (e.g., Flink) with the slow-path batch system. The fast-path maintains a smaller Trie of recent heavy hitters that is merged with the main Trie results at query time.

2. **The Trie grows beyond single machine memory capacity. How do you scale?**
   - **Sharding by Prefix:** Shard the Trie based on the first character(s) (e.g., 'a'-'c' on Server 1, 'd'-'f' on Server 2). Handle uneven distribution by sharding on deeper prefixes or hashing.
   - **Sharding by Hash:** Hash the prefix to determine the shard, requiring a scatter-gather approach if we need to find all prefixes starting with a string, but since we cache at the node level, we just hash the exact prefix being queried to hit the correct shard.

3. **How do you reduce the bandwidth cost of 48,000 QPS hitting your servers?**
   - Browser caching: Cache previous responses locally.
   - Debouncing: Only send request after user stops typing for ~50-100ms.
   - Edge Caching (CDN): Cache popular prefixes at the edge.

## Variants and extensions
- **Personalized Autocomplete:** Merging global popularity with user's historical searches. Requires a fast lookup of user history (e.g., Redis) and runtime merging with global Trie results.

## Interviewer probes to prepare
- "What happens if a celebrity does something controversial and a specific query spikes 1000x in 5 minutes?"
- "Walk me through how you replace the old Trie with the newly built one without dropping traffic."
