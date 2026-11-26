# 🎯 HLD Interview Practice Template

> **Type:** High-Level Design (Classic System Design)  
> **Total Time:** 45 minutes  
> **Flagship Example:** URL Shortener

---

## ⏱️ Time-Boxed Structure

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Requirements Clarification | 5 min | Functional & non-functional requirements, scope, assumptions |
| 2. Capacity Estimation | 5 min | QPS, storage, bandwidth — back-of-envelope math |
| 3. API Design | 5 min | Core endpoints, request/response schemas |
| 4. Data Model | 5 min | Schema, database choice, indexing strategy |
| 5. High-Level Architecture | 10 min | Component diagram, data flow (read + write paths) |
| 6. Deep Dives | 10 min | Scaling, caching, key algorithms, failure handling |
| 7. Trade-Offs & Wrap-Up | 5 min | Design decisions, alternatives, follow-ups |

---

## 📊 Scoring Rubric

| Dimension | 1 — Weak | 2 — Below Avg | 3 — Meets Bar | 4 — Strong | 5 — Exceptional |
|-----------|----------|---------------|---------------|------------|-----------------|
| **Requirements & Scoping** | No scoping, jumps to design | Mentions a few FRs | Clear FRs + NFRs, reasonable scope | Proactively defines scale, latency targets, and out-of-scope | Uncovers hidden requirements, identifies key trade-offs early |
| **Estimation** | Skipped entirely | Rough guess with no math | Reasonable estimates with basic calculations | Accurate estimates with clear methodology | Estimation drives design decisions (e.g., sharding threshold) |
| **API Design** | No APIs defined | Incomplete or inconsistent APIs | Core CRUD endpoints with reasonable schemas | RESTful design with pagination, auth, rate limiting | Versioned APIs with idempotency, error codes, and webhooks |
| **Data Model** | No schema | Basic schema, wrong DB choice | Reasonable schema with justified DB choice | Normalized/denormalized as appropriate, indexes identified | Schema handles evolution, discusses migration and partitioning |
| **Architecture** | No diagram | Missing key components | Core components present, basic data flow | Clean architecture with caching, queues, CDN as needed | Elegant design with clear failure domains and scaling paths |
| **Deep Dives** | Cannot go deeper | Surface-level answers | Solid understanding of 1-2 deep topics | Detailed analysis of scaling, caching, consistency | Novel insights, quantitative reasoning, multiple alternatives |
| **Trade-Offs** | No trade-offs discussed | Acknowledges trade-offs exist | Discusses 1-2 concrete trade-offs | Structured trade-off analysis with pros/cons | Connects trade-offs to business requirements and SLAs |

**Scoring:** 24+ = Strong Hire · 19-23 = Hire · 14-18 = Lean Hire · <14 = No Hire

---

## ✅ Self-Review Checklist

After completing your practice session, verify:

### Requirements
- [ ] Defined at least 4-5 functional requirements
- [ ] Specified non-functional requirements (latency, availability, consistency)
- [ ] Stated assumptions and out-of-scope items
- [ ] Asked 2-3 clarifying questions

### Estimation
- [ ] Estimated DAU / QPS (read and write)
- [ ] Calculated storage needs (per-record × volume × retention)
- [ ] Estimated bandwidth (incoming + outgoing)
- [ ] Numbers are realistic (not off by orders of magnitude)

### API & Data Model
- [ ] Core APIs cover all functional requirements
- [ ] Database type justified (SQL vs NoSQL)
- [ ] Schema has primary keys and necessary indexes
- [ ] Considered read vs write optimization

### Architecture
- [ ] Drew a clear component diagram
- [ ] Explained both read and write data flows
- [ ] Included load balancer, app servers, cache, database
- [ ] Added message queue or async processing where appropriate

### Deep Dives
- [ ] Discussed at least 2 deep-dive topics
- [ ] Covered scaling strategy (horizontal, sharding, replication)
- [ ] Addressed caching strategy (what, where, TTL, invalidation)
- [ ] Considered failure scenarios and recovery

### Communication
- [ ] Stayed within time budget per phase
- [ ] Drew diagrams to support explanations
- [ ] Justified every technology and design choice
- [ ] Proactively discussed trade-offs

---

## 🔗 Related Resources

- [HLD Practice Template](hld-template.md) — Blank fill-in template
- [DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md) — HLD methodology
- [HLD Interview Checklist](../interview-tips/hld-checklist.md) — Quick reference
- [Interview Framework](../interview-tips/interview-framework.md) — Includes Applied ML variant flow
- [HLD Projects](../../04-hld-projects/) — 26 complete system designs

---

*Use this rubric to grade yourself honestly after each practice session. Focus on dimensions where you score below 3.*
