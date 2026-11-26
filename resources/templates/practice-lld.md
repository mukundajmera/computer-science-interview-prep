# 🎯 LLD Interview Practice Template

> **Type:** Low-Level Design  
> **Total Time:** 45 minutes  
> **Flagship Example:** Parking Lot System

---

## ⏱️ Time-Boxed Structure

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Requirements Clarification | 5 min | Ask questions, scope the problem, identify FRs & NFRs |
| 2. Core Entities & Relationships | 5 min | Nouns → classes, map associations (has-a, is-a) |
| 3. Design Patterns Selection | 5 min | Pick 2-3 patterns, justify each choice |
| 4. Class Design | 15 min | Attributes, methods, interfaces, enums — write code |
| 5. Edge Cases & Optimizations | 10 min | Thread safety, error handling, complexity analysis |
| 6. Wrap-Up & Follow-Ups | 5 min | Summarize, discuss extensibility, answer follow-ups |

### Requirements and constraints

- Keep v1 scope constrained to core flows only.
- State assumptions explicitly before class design.
- Reserve at least 10 minutes for edge cases and follow-up handling.

---

## 📊 Scoring Rubric

| Dimension | 1 — Weak | 2 — Below Avg | 3 — Meets Bar | 4 — Strong | 5 — Exceptional |
|-----------|----------|---------------|---------------|------------|-----------------|
| **Requirements Gathering** | Dives straight into code | Asks 1-2 surface questions | Identifies core FRs and basic NFRs | Clearly scopes FRs, NFRs, and out-of-scope | Proactively uncovers edge cases and hidden constraints |
| **Entity Identification** | Missing key entities | Identifies obvious entities only | Covers all major entities with reasonable attributes | Clean entity model with correct relationships | Elegant model with clear separation of concerns |
| **Pattern Usage** | No patterns or wrong patterns | Applies 1 pattern incorrectly | Uses 1-2 appropriate patterns | Applies 2-3 patterns with clear justification | Patterns compose naturally; discusses trade-offs |
| **Class Design Quality** | Incomplete or non-compiling | Basic classes, missing key methods | Working design, follows SRP mostly | Clean OOP, SOLID principles, extensible | Production-quality, thread-safe, well-documented |
| **Edge Cases & Error Handling** | Not discussed | Mentions 1-2 obvious cases | Handles common edge cases | Comprehensive coverage, graceful degradation | Anticipates interviewer follow-ups, discusses monitoring |
| **Communication** | Hard to follow | Explains only when asked | Clear explanation of design choices | Structured walkthrough, good pacing | Drives the conversation, teaches while designing |

**Scoring:** 18+ = Strong Hire · 14-17 = Hire · 10-13 = Lean Hire · <10 = No Hire

---

## ✅ Self-Review Checklist

After completing your practice session, verify:

### Requirements
- [ ] Identified at least 4-5 functional requirements
- [ ] Discussed non-functional requirements (concurrency, scale, extensibility)
- [ ] Asked at least 2-3 clarifying questions
- [ ] Defined what is out of scope

### Design
- [ ] All key entities identified (no missing nouns)
- [ ] Relationships are explicit (composition vs aggregation vs inheritance)
- [ ] Applied at least 2 design patterns with justification
- [ ] Interfaces used for abstraction where appropriate
- [ ] Enums used for fixed sets of values

### Code Quality
- [ ] Classes follow Single Responsibility Principle
- [ ] Open/Closed Principle considered for extensibility
- [ ] No God classes (no class doing everything)
- [ ] Meaningful method and variable names
- [ ] Appropriate access modifiers (private fields, public API)

### Edge Cases
- [ ] Null/empty input handling
- [ ] Concurrent access scenarios discussed
- [ ] Invalid state transitions handled
- [ ] Resource limits considered (capacity, bounds)

### Communication
- [ ] Stayed within time budget per phase
- [ ] Explained "why" behind each design decision
- [ ] Drew or described class diagram
- [ ] Discussed 2-3 potential follow-up extensions

---

## 🔗 Related Resources

- [LLD Practice Template](lld-template.md) — Blank fill-in template
- [HOW-TO-APPROACH.md](../../02-lld-projects/HOW-TO-APPROACH.md) — Methodology guide
- [LLD Interview QA](../../02-lld-projects/INTERVIEW-QA.md) — Follow-up question bank
- [LLD Interview Checklist](../interview-tips/lld-checklist.md) — Quick reference
- [LLD Projects](../../02-lld-projects/) — 20 practice problems

---

*Use this rubric to grade yourself honestly after each practice session. Focus on dimensions where you score below 3.*
