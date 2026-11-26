# Search Autocomplete - Common Pitfalls

## 1. Synchronous Trie Updates
- **Failure Signal:** Designing the system to update the Trie synchronously on every keystroke or search submission.
- **Root Cause:** Misunderstanding read-vs-write ratios and lock contention in high-concurrency environments.
- **Mitigation:** Use an append-only log for analytics and rebuild/update the Trie offline in batch.
- **Validation Signal:** Throughput tests show severe degradation under concurrent writes.

## 2. Inefficient Trie Traversal
- **Failure Signal:** Computing top-5 suggestions dynamically during read requests by traversing the entire subtree.
- **Root Cause:** Not recognizing that O(p + m log k) is too slow for <100ms latency at high QPS.
- **Mitigation:** Pre-compute and cache the top-5 queries at every Trie node (O(1) lookup since prefix length is capped).
- **Validation Signal:** Load tests reveal P99 read latency exceeding 100ms.

## 3. Ignoring Client-Side Optimizations
- **Failure Signal:** Sending a request for every single keystroke without debouncing.
- **Root Cause:** Treating the system only as a backend problem.
- **Mitigation:** Discuss debouncing, browser caching, and cancelling stale AJAX requests.
- **Validation Signal:** Network logs show an excessive number of duplicate or overlapping API calls.

## 4. Overcomplicating Real-Time Updates
- **Failure Signal:** Building a complex streaming pipeline (Flink/Storm) to update autocomplete instantly.
- **Root Cause:** Ignoring the business requirement that stale data is acceptable (most popular searches don't change by the second).
- **Mitigation:** Acknowledge that a small delay (hours/days) in trending searches is a valid trade-off for simplicity and performance.
- **Validation Signal:** Architectural complexity significantly increases without noticeable user benefit.
