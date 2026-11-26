# System Design Interview Delivery Framework

A practical execution model for 45-60 minute product and infrastructure system design interviews.

---

## 📖 What This Interview Actually Tests

System design rounds primarily evaluate:
- Your ability to reduce ambiguity into a clear plan
- Your ability to pick trade-offs intentionally
- Your ability to communicate and adapt under constraints
- Your ability to go deep in one or two high-risk areas

A strong answer is not the most complex answer. It is a coherent and defensible answer that matches requirements and scale.

---

## Requirements and Constraints

### Functional Requirements
Capture the smallest feature set that makes the system useful:
- Core user actions
- Key read/write flows
- Required outputs and behaviors

### Non-Functional Requirements
Quantify before designing:
- Latency targets (read/write)
- Availability target
- Throughput and traffic envelope
- Consistency and durability expectations
- Security and compliance constraints (if relevant)

### Interview Time Constraint
Most rounds are 45-60 minutes:
- Spend early time reducing ambiguity
- Avoid deep detail on low-impact components
- Reserve time for one deep dive and trade-off discussion

---

## Suggested Time Box

| Phase | Time | Deliverable |
|---|---:|---|
| Requirements + scope | 5-8 min | Prioritized requirements and explicit out-of-scope |
| Capacity estimates | 3-6 min | Only estimates that change design decisions |
| APIs / interfaces | 4-6 min | 3-5 key endpoints or service interfaces |
| Data model + entities | 5-8 min | Core entities + index/partition hints |
| High-level design | 10-15 min | End-to-end read and write paths |
| Deep dive(s) | 10-12 min | One bottleneck area with trade-offs |
| Risks + evolution | 3-5 min | Failure handling + v1 to v2 growth plan |

---

## Scoring Rubric (Self-Calibration)

| Dimension | Weak Signal | Strong Signal |
|---|---|---|
| Problem Navigation | Starts architecture before clarifying problem | Prioritizes requirements, constraints, and scope clearly |
| Solution Design | Box diagram with no data-flow reasoning | Clear read/write paths and data ownership |
| Technical Judgment | Tool-name dropping without rationale | Pattern and technology choices tied to constraints |
| Communication | Jumps around with no summary | Structured flow and concise decisions |

---

## Common Pitfalls

- Spending 15+ minutes on API details and never reaching scaling decisions
- Doing generic capacity math that does not influence architecture
- Choosing advanced patterns before proving simpler options fail
- Ignoring failure modes (cache down, replica lag, queue backlog, regional outage)
- Avoiding explicit trade-offs
- No wrap-up summary that ties decisions to requirements

---

## Follow-up Questions

1. Which requirement drives your first architecture decision?
2. What will break first at 10x traffic?
3. Which component is intentionally eventually consistent, and why?
4. Where would you apply backpressure?
5. What metric would trigger your first major redesign?
6. What would you simplify in v1 to ship faster?

---

## Variants and Extensions

- **Staff-level variant:** Add migration plan, ownership boundaries, and operational risk controls
- **Global variant:** Add multi-region latency and data sovereignty constraints
- **Cost-constrained variant:** Optimize for fewer managed components in v1
- **Infra-heavy variant:** Focus on durability, failure isolation, and replay/idempotency
- **Realtime variant:** Compare polling vs SSE vs WebSocket with connection-scaling implications

---

## 🔗 Cross-References

- [Back-of-Envelope Estimation](./back-of-envelope.md)
- [CAP Theorem & Consistency Models](./cap-theorem.md)
- [Networking Essentials](../networking-basics/networking-essentials.md)
- [HLD Concepts](../../03-hld-concepts/README.md)
- [HLD Design Template](../../04-hld-projects/DESIGN-TEMPLATE.md)
- [HLD Interview Checklist](../../resources/interview-tips/hld-checklist.md)
