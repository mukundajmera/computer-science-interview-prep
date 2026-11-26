# HLD Core Concepts Practice Template

Type: Concept-focused HLD drill
Total Time: 45 minutes

---

## Time-boxed structure

| Phase | Duration | Focus |
|---|---:|---|
| 1. Scope and assumptions | 5 min | Define critical flows and constraints |
| 2. Capacity and growth cues | 5 min | Only estimates that change decisions |
| 3. CAP policy by endpoint | 8 min | Consistency vs availability per operation |
| 4. Data scaling path | 10 min | Replicas/index/cache first, sharding triggers next |
| 5. Hashing/hotspot/failure plan | 8 min | Ownership churn vs traffic skew controls |
| 6. Trade-offs and close | 9 min | Crisp decisions, risks, and next-step evolution |

---

## Fill-in worksheet

### 1) Scope and assumptions
- Product/problem:
- Critical write paths:
- Non-critical read paths:
- Latency and availability expectations:

### 2) Capacity and growth cues
- Current read/write volume:
- 12-month growth assumption:
- Bottleneck hypothesis to validate:

### 3) CAP policy per endpoint
| Endpoint/operation | Consistency need | Availability posture | Degraded mode |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

### 4) Data scaling path
- Stage 1 (no sharding):
- Sharding triggers:
- Candidate shard key(s):
- Cross-shard query mitigation:
- Migration safety plan:

### 5) Hashing, hotspots, and failures
- Consistent hashing plan:
- Hotspot mitigation stack:
- Failure handling sequence:
- Rebalance guardrails:

### 6) Trade-offs and close
- Major decision 1 and why:
- Major decision 2 and why:
- Risks and mitigations:
- 60-second final summary:

---

## Scoring rubric

| Dimension | 1 - Weak | 3 - Meets bar | 5 - Strong |
|---|---|---|---|
| Scope quality | Vague requirements | Clear critical/non-critical split | Constraints drive all decisions |
| Estimation quality | Random numbers | Reasonable directional estimates | Estimates directly drive architecture |
| CAP reasoning | Global CP/AP label only | Per-endpoint choices | Endpoint policy + degraded mode + recovery |
| Scaling judgment | Premature sharding | Trigger-aware progression | Measured trigger thresholds + safe migration |
| Hotspot/failure strategy | Generic "add cache" | Basic mitigations | Layered controls + operational runbook |
| Communication | Disconnected ideas | Mostly coherent | Clear, defensible, interview-ready narrative |

Suggested thresholds:
- 24+ strong
- 18-23 good
- <18 needs more repetition

---

## Pitfall checklist

- [ ] I justified sharding with measured triggers, not fear.
- [ ] I separated CAP behavior by endpoint.
- [ ] I called out ownership churn vs traffic skew.
- [ ] I included migration rollback criteria.
- [ ] I stated a freshness contract where staleness is allowed.

---

## Follow-up prompt bank

1. What breaks first at 10x traffic and why?
2. How do you migrate shard key with near-zero downtime?
3. Which endpoint can tolerate stale data, and for how long?
4. How do you prevent cache stampede during rebalancing?
5. What metrics gate your cutover progression?

---

## Cross-links

- [HLD Practice Template](./practice-hld.md)
- [HLD Checklist](../interview-tips/hld-checklist.md)
- [CAP Theory](../../00-theory/system-design-fundamentals/cap-theorem.md)
- [Sharding Theory](../../00-theory/database-concepts/sharding.md)
- [Consistent Hashing Concept](../../03-hld-concepts/consistent-hashing/)
