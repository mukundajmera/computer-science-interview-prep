# Bot Detection — Common Interview Pitfalls

## 1. Designing for static attackers
Ignoring adversarial evolution leads to rapid model obsolescence.

## 2. No graduated enforcement
Binary ban/no-ban policy creates excessive collateral damage.

## 3. Over-reliance on one model
Single-model stacks are brittle to concept drift.

## 4. No investigator label strategy
Scarce high-quality labels must be allocated deliberately.

## 5. No appeal workflow
False positives without clear recovery path erode trust.

## 6. Missing feature-pipeline fallback
Detection gaps appear during stream lag or feature outages.

## 7. Running heavy ML inference inline on the critical path
Evaluating deep behavioral models synchronously at 50,000 peak req/sec blows past the 5 ms inline risk-assessment budget and degrades login and checkout latency. Keep inline checks limited to Redis profile lookups, sliding-window rate limits, and lightweight heuristics, and offload behavioral feature aggregation to Kafka and Flink asynchronously.

## 8. Failing closed when Redis or the risk engine times out
Blocking requests whenever Redis misses its 2 ms fetch budget or the inline risk engine hits 5 ms turns a cache hiccup into a platform outage that violates the 99.99% availability target. Enforce an explicit fail-open timeout boundary that allows legitimate traffic through while logging the missed evaluation asynchronously.

## 9. Treating noisy fingerprints as deterministic block rules
JA3/JA4 TLS hashes, HTTP/2 SETTINGS frames, and Canvas/WebGL fingerprints collide across corporate NATs, shared devices, and routine browser upgrades, causing waves of false positives. Decay fingerprint weights over time, combine them with velocity and behavioral signals, and route uncertain traffic to low-friction challenges instead of hard `403` blocks.

## 10. Collecting sensitive telemetry without consent, minimization, or TTLs
Silently capturing raw keystrokes, canvas/WebGL hashes, or mobile sensor streams violates GDPR/CCPA constraints and risks exposing passwords or PII. Require explicit notice and consent, map keystrokes to generic character categories before transmission, and enforce Cassandra TTLs (24h for network hashes, 30 days for behavioral signals).

## 11. Omitting hot-key salting and accessibility fallbacks
Large corporate NAT IPs or botnet exit nodes concentrate writes on single Cassandra partitions and Redis keys, while screen-reader users trigger false behavioral velocity alerts. Salt hot partition keys or buffer locally, and provide accessible verification alternatives (such as audio challenges or email MFA) alongside the self-service appeal API.

---

## Quick Self-Check

- Did I model adversarial drift and adaptation cadence?
- Did I include multi-stage enforcement actions?
- Did I include investigator + appeal feedback loops?
- Did I define fallback behavior when features are stale?
- Did I keep inline risk evaluation under 5 ms with a fail-open timeout boundary?
- Did I offload heavy behavioral feature aggregation to an async stream pipeline (Kafka/Flink)?
- Did I treat TLS and Canvas/WebGL fingerprints as noisy signals rather than deterministic blocks?
- Did I enforce consent, keystroke anonymization, and TTL retention on sensitive telemetry?
- Did I address NAT hot partitions and accessible verification paths for flagged users?
