# 🧭 System Design Interview Delivery Framework

A practical 7-step flow you can use in almost any HLD interview to stay structured, communicate clearly, and cover depth without losing time.

---

## ⏱️ 45-Minute Timebox

| Step | Time | Goal |
|------|------|------|
| 1. Clarify Requirements | 5-7 min | Scope the problem correctly |
| 2. Back-of-Envelope Estimation | 4-6 min | Size traffic/storage and shape architecture |
| 3. API Design | 4-5 min | Define external contract |
| 4. Data Modeling | 4-5 min | Identify key entities and access patterns |
| 5. High-Level Architecture | 10-12 min | Design components + data flow |
| 6. Deep Dives & Trade-offs | 8-10 min | Show judgment and scaling depth |
| 7. Wrap-up & Follow-ups | 2-4 min | Summarize and extend thoughtfully |

Note: These time ranges are approximate; adjust them to fit your interview’s 45-minute timebox (or whatever time you’re given).

---

## 1) Clarify Requirements

Start with functional + non-functional requirements before proposing components.

**Ask:**
- Core user flows?
- Expected scale (DAU, QPS, storage)?
- Latency/availability targets?
- Consistency expectations?
- In/out of scope?

**Good phrasing:**
> "Before designing, I want to align on requirements, scale, and success criteria."

---

## 2) Back-of-Envelope Estimation

Do quick, rounded math to avoid designing blindly.

**Estimate:**
- Read/write QPS
- Daily storage growth
- Peak traffic multiplier
- Bandwidth hotspots

Use estimates to justify:
- Cache strategy
- Database choice
- Partitioning needs
- Async pipeline needs

Related: [Back-of-Envelope Estimation](../../00-theory/system-design-fundamentals/back-of-envelope.md)

---

## 3) API Design

Define 2-4 core APIs early so downstream model and architecture are concrete.

**Cover:**
- endpoint shape
- request/response
- idempotency where needed
- pagination/filtering for list APIs
- error handling basics

---

## 4) Data Modeling

Model entities around access patterns, not just nouns.

**Discuss:**
- primary keys and lookup keys
- hot queries
- indexing strategy
- SQL vs NoSQL trade-off
- retention/archive if relevant

---

## 5) High-Level Architecture

Sketch the full request path and major components first.

Typical blocks:
- API Gateway / LB
- stateless services
- primary datastore + cache
- async queue/stream
- object store / CDN (if media heavy)

State the flow explicitly:
1. request enters
2. write/read path
3. cache hit/miss behavior
4. async side effects

---

## 6) Deep Dives & Trade-offs

Pick 1-2 critical areas and go deep:
- partitioning and hot keys
- consistency model
- failure handling/retries
- rate limiting
- observability

Always compare alternatives:
- "Option A is simpler but caps scale..."
- "Option B improves availability but relaxes consistency..."

Related: [CAP Theorem](../../00-theory/system-design-fundamentals/cap-theorem.md)

---

## 7) Wrap-up & Follow-ups

Close with a concise summary:
- requirements satisfied
- known bottlenecks
- next scaling steps

Then proactively offer extensions:
- multi-region
- analytics/reporting
- abuse prevention
- cost optimization

---

## 8) Applied ML Variant (When Prompt Includes Modeling)

Use this fork when interview prompt centers on recommendation, moderation, fraud, or bot detection.

### Timebox adaptation

| Step | Time | Goal |
|------|------|------|
| 1. Clarify Problem | 5-7 min | Lock business objective, failure costs, and guardrails |
| 2. Data & Label Strategy | 6-8 min | Define data sources, label quality, and scarcity plan |
| 3. Modeling Approach | 8-10 min | Candidate model stack and policy/threshold strategy |
| 4. Inference + System Architecture | 10-12 min | Online path, async enrichment, fallback modes |
| 5. Evaluation Stack | 6-8 min | Business -> product -> ML metrics, offline + online gates |
| 6. Deep Dives & Trade-offs | 6-8 min | Drift, feedback loops, calibration, rollout safety |
| 7. Wrap-up | 2-4 min | Operating point + next validation step |

### Mandatory signal

- Separate business objective from ML metric.
- State precision/recall or quality guardrails before proposing enforcement actions.
- Include feedback loop and drift response path.

Related:
- [ML Generalization](../../06-genai-systems/00-concepts/ml-generalization/README.md)
- [LLM Evaluation](../../06-genai-systems/00-concepts/llm-evaluation/)

---

## 9) Behavioral Adaptation Callout

For mixed loops where system design and behavioral calibration both matter:
- Start with one concise signal statement ("I'll optimize for reliability under ambiguity").
- Use one story that proves ownership, conflict handling, and reflection quality.
- Keep a manager variant and an IC variant for the same story anchor.

Related:
- [Behavioral Big Three](./behavioral-big-three.md)
- [Behavioral Big Tech Calibration](./behavioral-big-tech-calibration.md)
- [Behavioral Special Interview Types](./behavioral-special-interview-types.md)

---

## ✅ Quick Self-Check

Before ending, verify you covered:
- [ ] Functional + non-functional requirements
- [ ] Core capacity estimates
- [ ] API and data model
- [ ] Scalable architecture
- [ ] Trade-offs and failure scenarios
