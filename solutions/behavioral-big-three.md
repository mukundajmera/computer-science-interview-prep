# 🎯 Behavioral Big Three

Coach answer outline for the three most common behavioral prompts:
1. Tell me about yourself
2. Tell me about your favorite project
3. Tell me about a conflict you resolved

---

## 1) Tell Me About Yourself (TMAY)

### What interviewers are scoring
- Career trajectory and role fit
- Scope and ownership progression
- Communication clarity and prioritization

### Strong structure (60-90 seconds)
1. Present role + core scope
2. 1-2 past highlights tied to target role
3. Why this role/company now

### Sample answer scaffold
- "I'm a staff-level backend engineer currently leading reliability and platform work for a high-throughput payments surface."
- "Over the last few years, I've moved from shipping services to owning cross-team architecture decisions, including a migration that reduced checkout failures by 30%."
- "I'm now looking for a role where I can combine hands-on architecture with mentoring and cross-functional execution at larger scale."

### Common weak patterns
- Full chronological biography
- Team-only language with no personal actions
- Generic close with no role-specific intent

---

## 2) Favorite Project

### What interviewers are scoring
- Problem selection judgment
- Technical depth and trade-off quality
- Measurable impact and personal contribution

### Strong structure (2-3 minutes + follow-ups)
1. Problem context and stakes
2. Constraints and decision points
3. Your actions and why
4. Outcome and what changed
5. Reflection and next iteration

### Sample answer scaffold
- **Context:** "Search latency spikes during peak events were hurting conversion."
- **Constraint:** "We had six weeks, no downtime window, and strict relevance guardrails."
- **Actions:** "I proposed staged indexing, introduced query-classification caching, and led cross-team rollout sequencing."
- **Result:** "P95 latency dropped from 780ms to 290ms, and conversion improved 8.4%."
- **Reflection:** "I'd add earlier failure-injection tests; we found one degradation path late."

### Common weak patterns
- Vague "we built X" narrative
- No hard trade-off discussion
- Outcome without metrics

---

## 3) Conflict Story

### What interviewers are scoring
- Conflict maturity and professionalism
- Influence without authority
- Resolution quality and relationship durability

### Strong structure (2-3 minutes)
1. Nature of disagreement (technical/process/prioritization)
2. Why it mattered
3. How you handled conversation and alignment
4. Decision and outcome
5. Relationship and process improvement after

### Sample answer scaffold
- **Situation:** "Product wanted to launch quickly; engineering flagged integrity risks."
- **Action:** "I documented failure scenarios, proposed a phased launch, and facilitated a decision review with shared success criteria."
- **Resolution:** "We shipped phase 1 safely in two weeks and unlocked full rollout after validation."
- **Aftermath:** "Trust improved because we converted disagreement into explicit risk ownership."

### Common weak patterns
- Story framed as "I was right, they were wrong"
- Emotional detail without business/technical resolution
- No evidence of collaboration repair

---

## Follow-up Handling Cheat Sheet
- Clarification: "Happy to go deeper on design trade-offs or stakeholder dynamics."
- Depth: "At that point, I chose X over Y because failure cost was higher than latency cost."
- Ownership: "The team executed it, and I personally owned architecture, rollout gates, and incident readiness."
- Reflection: "If repeated, I'd front-load dependency risk earlier to cut one week of churn."

---

## Final Self-Check
Before ending each answer, confirm:
- Clear personal ownership
- Explicit constraints and trade-offs
- Quantified outcome
- Learning that generalizes

---

## Related Resources
- `resources/interview-tips/behavioral-big-three.md`
- `resources/interview-tips/behavioral-practice-roadmap.md`
- `resources/interview-tips/behavioral-pitfalls.md`
