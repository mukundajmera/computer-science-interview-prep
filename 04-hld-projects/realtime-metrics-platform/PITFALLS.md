# Real-Time Metrics Platform — Common Pitfalls

## 1. Treating all time windows the same
Using one store/query strategy for both last 5 minutes and last 90 days causes either cost blowups or poor latency.

## 2. Ignoring cardinality limits
Unbounded tags (request_id, user_id, trace_id) can collapse the system.

## 3. No event-time policy
Without watermark/late-data handling, alert correctness is unreliable.

## 4. Weak ingestion contracts
Missing batch/idempotency constraints causes duplicate or inconsistent points.

## 5. Alert flapping
No debounce/cooldown policy leads to noisy, low-trust alerting.

## 6. Missing backpressure plan
Assuming sinks always keep up ignores real spike behavior.

## 7. Cost-blind retention
Keeping full-resolution raw data indefinitely usually fails budget constraints.

---

## Top-K Variant Pitfalls

- Executing global top-K scans at query time.
- No late-event policy, causing unstable ranking windows.
- Ignoring partition skew from viral IDs.
