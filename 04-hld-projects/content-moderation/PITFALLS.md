# Content Moderation — Common Interview Pitfalls

## 1. No explicit operating threshold
Ignoring precision guardrails leads to unworkable enforcement policy.

## 2. Treating class imbalance as minor
Rare harmful events require targeted sampling and calibration strategy.

## 3. Missing policy/action layer
A score alone is not a production decision.

## 4. No human review capacity model
Review queues can become the bottleneck.

## 5. No feedback loop
Without reports/appeals/moderator labels, performance decays quickly.

## 6. Conflating this with full LLM governance platform
Interview scope drifts away from applied moderation architecture.

## 7. Treating perceptual hash matches as automatic policy violations
Auto-blocking on approximate perceptual hashes (such as PDQ) causes false takedowns on benign memes or cropped images that share visual structure with harmful media. Restrict immediate auto-blocks to exact cryptographic matches (such as SHA-256) and route perceptual near-matches to the Tier 3 human review queue.

## 8. Ignoring adversarial text obfuscation before model inference
Feeding raw user text straight into toxicity classifiers lets bad actors bypass detection using homoglyphs, l33t speak, or injected whitespace. Run a deterministic normalization stage to strip unusual whitespace and map homoglyphs prior to model scoring.

## 9. Storing full multi-modal payloads for benign traffic or mutating policies in place
Persisting raw image and video payloads for all 1B daily posts (99% benign) explodes storage to petabytes per day, while overwriting global policy rules breaks appeal auditability. Filter at ingestion so only flagged metadata is persisted long-term, and attach an immutable `policy_version` to every decision so appeals evaluate against the original rules.

## 10. Running heavy video frame extraction synchronously on the ingestion path
Decoding and sampling frames inline from tens of millions of daily videos saturates ingestion servers and violates the <200 ms P95 automated decision SLA. Return `202 Accepted` after writing to Kafka, split videos into chunks across distributed worker pools, and process extracted keyframes asynchronously.

## 11. Skipping cache stampede protection and reviewer safety controls
Viral posts that trigger thousands of simultaneous reports can expire cached decisions and hammer PostgreSQL, while FIFO review queues leave high-exposure content sitting past the <2-hour SLA and expose moderators to fatigue or doxxing. Combine probabilistic early expiration with request coalescing on decision lookups, and enforce severity/virality priority queues, double-blind reviews, fatigue rotation, and scrubbed reviewer identities.

---

## Quick Self-Check

- Did I define business objective + precision guardrail?
- Did I include policy actions beyond binary score?
- Did I model review queue saturation and fallback behavior?
- Did I cover drift/evasion and recalibration cadence?
- Did I distinguish exact cryptographic hash auto-blocks from perceptual-hash human review?
- Did I include text normalization for homoglyphs and obfuscation before scoring?
- Did I filter benign media at ingestion and attach immutable policy versions for appeal audits?
- Did I offload video chunking and frame extraction to async distributed workers via Kafka?
- Did I protect viral decision lookups from cache stampedes and enforce reviewer safety/fatigue controls?
