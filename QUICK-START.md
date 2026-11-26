# 🚀 Quick Start Guide

Welcome to the System Design Interview Prep repository! This guide will help you navigate the content effectively based on your timeline and goals.

---

## 📑 Table of Contents

- [🎯 Study Modes](#-study-modes)
- [📂 Directory Guide](#-directory-guide)
- [📝 How to Practice](#-how-to-practice)
- [🧭 Navigation Tips](#-navigation-tips)
- [⏱️ Time Estimates](#️-time-estimates)
- [❓ FAQ](#-faq)

---

## 🎯 Study Modes

Choose the study mode that fits your timeline:

### 🚨 Interview in 1 Week

A focused crash course for last-minute preparation. [**Full 1-Week Plan →**](./resources/study-plans/1-week-plan.md)

| Day | Focus Area | Time | What to Cover |
|-----|------------|------|---------------|
| **Day 1** | Core Design Patterns | 5-6 hrs | Singleton, Factory, Strategy, Observer, Builder, Decorator |
| **Day 2** | LLD Projects | 5-6 hrs | Parking Lot, LRU Cache, Elevator |
| **Day 3** | HLD Concepts | 5-6 hrs | Caching, Load Balancing, Sharding, Queues, Idempotency |
| **Day 4** | HLD Projects #1 | 5-6 hrs | URL Shortener, Twitter Feed |
| **Day 5** | HLD Projects #2 | 5-6 hrs | Chat App, Video Streaming |
| **Day 6** | Mock Practice | 4-5 hrs | Practice interviews, self-assessment |
| **Day 7** | Review & Rest | 3-4 hrs | Cheatsheets, weak areas |

**Key Resources:**
- 📋 [CONCEPTS.md](./CONCEPTS.md) - Quick reference cheatsheet
- 📊 [Cheatsheets](./resources/cheatsheets/) - Pattern decision tree, trade-offs
- 💡 [Interview Tips](./resources/interview-tips/) - LLD/HLD/behavioral checklists
- 💬 [Salary Negotiation Playbook](./resources/interview-tips/salary-negotiation-playbook.md) - Offer-stage negotiation strategy (Global + India)

---

### 📚 Deep Dive (1-3 Months)

Comprehensive preparation for thorough understanding. [**Full 1-Month Plan →**](./resources/study-plans/1-month-plan.md)

#### Month 1: Foundations
| Week | Focus | Content | Time/Day |
|------|-------|---------|----------|
| Week 1 | Theory | OOP, SOLID, Complexity | 2-3 hrs |
| Week 2 | Patterns | Creational + Structural | 2-3 hrs |
| Week 3 | Patterns | Behavioral patterns | 2-3 hrs |
| Week 4 | Review | Pattern practice + first LLD | 3-4 hrs |

#### Month 2: Low-Level Design
| Week | Focus | Content | Time/Day |
|------|-------|---------|----------|
| Week 1 | LLD Basics | Approach, 3 beginner projects | 3-4 hrs |
| Week 2 | LLD Practice | 4 intermediate projects | 3-4 hrs |
| Week 3 | LLD Advanced | 3 complex projects | 3-4 hrs |
| Week 4 | LLD Review | Revisit, optimize solutions | 2-3 hrs |

#### Month 3: High-Level Design
| Week | Focus | Content | Time/Day |
|------|-------|---------|----------|
| Week 1 | HLD Concepts | Core concept families, including read/write/blob/async scaling patterns | 2-3 hrs |
| Week 2 | HLD Projects | 3 system designs | 3-4 hrs |
| Week 3 | HLD Projects | 3 more systems | 3-4 hrs |
| Week 4 | Integration | Mock interviews, full review | 3-4 hrs |

---

### 🤖 GenAI System Design Prep

For engineers preparing for GenAI/LLM-focused system design interviews.

| Plan | Duration | Best For | Link |
|------|----------|----------|------|
| 🚨 **GenAI Crash Track** | 1–2 weeks | Fast GenAI SD prep | [genai-crash-track.md](./resources/study-plans/genai-crash-track.md) |
| 🧠 **GenAI Deep Dive** | 4 weeks | Comprehensive GenAI mastery | [genai-deep-dive.md](./resources/study-plans/genai-deep-dive.md) |

**Key Resources:**
- 📋 [GenAI SD Framework](./06-genai-systems/GENAI-SD-FRAMEWORK.md) — 6-step interview framework
- ⚖️ [Classic vs GenAI SD](./06-genai-systems/CLASSIC-VS-GENAI.md) — What's different
- 🚨 [GenAI Pitfalls](./06-genai-systems/PITFALLS.md) — Top 10 interview mistakes
- 📈 [Model Generalization](./06-genai-systems/00-concepts/ml-generalization/) — drift, calibration, and production quality diagnostics

---

### 🔍 Topic-Based Preparation

For targeting specific areas or filling knowledge gaps. [**Full Topic Paths →**](./resources/study-plans/topic-based-plan.md)

**If you need to work on:**

| Topic | Start Here | Then Move To | Est. Time |
|-------|------------|--------------|-----------|
| OOP Basics | [00-theory/oop-principles](./00-theory/oop-principles/) | Design Patterns | 1-2 days |
| Design Patterns | [01-design-patterns](./01-design-patterns/) | LLD Projects | 1-2 weeks |
| LLD Skills | [02-lld-projects](./02-lld-projects/) + [HOW-TO-APPROACH](./02-lld-projects/HOW-TO-APPROACH.md) | More projects | 1-2 weeks |
| Distributed Systems | [03-hld-concepts](./03-hld-concepts/) | HLD Projects | 1 week |
| System Design | [04-hld-projects](./04-hld-projects/) + [DESIGN-TEMPLATE](./04-hld-projects/DESIGN-TEMPLATE.md) | Related concepts | 1-2 weeks |
| Caching | [resources/cheatsheets/hld-components-map.md](./resources/cheatsheets/hld-components-map.md) | HLD projects with caching | 2-3 days |
| GenAI SD | [06-genai-systems/GENAI-SD-FRAMEWORK.md](./06-genai-systems/GENAI-SD-FRAMEWORK.md) | [GenAI concepts](./06-genai-systems/00-concepts/) → HLD projects | 1-4 weeks |

---

## 📂 Directory Guide

### 00-theory/ - Fundamentals
**Estimated Time:** 5-7 hours total

| Folder | Topics | Time | Priority |
|--------|--------|------|----------|
| `oop-principles/` | SOLID, DRY, KISS, Composition vs Inheritance | 2-3 hrs | High |
| `database-concepts/` | SQL, NoSQL, Indexing, Transactions | 1-2 hrs | Medium |
| `networking-basics/` | HTTP, TCP/IP, REST, gRPC | 1 hr | Low |
| `complexity-analysis/` | Big-O, Space/Time analysis | 1-2 hrs | High |
| `system-design-fundamentals/` | Core principles | 1 hr | Medium |

---

### 01-design-patterns/ - 23 GoF Patterns
**Estimated Time:** 15-20 hours total

| Category | Patterns | Priority | Time |
|----------|----------|----------|------|
| **Creational** | Singleton, Factory, Abstract Factory, Builder, Prototype | High | 4-5 hrs |
| **Structural** | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy | Medium | 5-6 hrs |
| **Behavioral** | Strategy, Observer, Command, State, Template, Chain, Iterator, Mediator, Memento, Visitor, Interpreter | High (core 5) | 6-8 hrs |

**Must-Know Patterns:** Singleton, Factory, Strategy, Observer, Decorator, State

---

### 02-lld-projects/ - 56 Projects
**Estimated Time:** 30-40 hours total

| Difficulty | Projects | Est. Time Each | Start Here |
|------------|----------|----------------|------------|
| ⭐⭐ Beginner | Parking Lot, Tic-Tac-Toe, Vending Machine | 45-60 min | ✅ Yes |
| ⭐⭐⭐ Intermediate | Library, Elevator, Hotel Booking, Movie Ticket, Inventory Management | 60-90 min | After 2 beginner |
| ⭐⭐⭐⭐ Advanced | Chess, Splitwise, Ride Sharing | 90+ min | After 3 intermediate |

**Key File:** [HOW-TO-APPROACH.md](./02-lld-projects/HOW-TO-APPROACH.md) - Master the 7-step framework

---

### 03-hld-concepts/ - 59 Core System Design Concepts
**Estimated Time:** 10-15 hours total

| Category | Concepts | Priority | Time |
|----------|----------|----------|------|
| **Infrastructure** | Load Balancing, Caching, CDN, API Gateway | High | 4-5 hrs |
| **Data + Scaling** | Sharding, Replication, CAP Theorem, Read Scaling, Write Scaling, Large Blob Handling | High | 3-4 hrs |
| **Communication + Reliability** | Message Queues, Microservices, Service Discovery, Idempotency, Distributed Transactions, Long-Running Tasks | Medium | 3-4 hrs |

---

### 04-hld-projects/ - 48 System Design Case Studies
**Estimated Time:** 20-30 hours total

| System | Key Concepts | Difficulty | Time |
|--------|--------------|------------|------|
| URL Shortener | Hashing, NoSQL, Cache | ⭐⭐ | 2-3 hrs |
| News Feed | Fan-out, Timelines, Cache | ⭐⭐⭐ | 3-4 hrs |
| Chat (WhatsApp-like) | WebSockets, Queues, Presence | ⭐⭐⭐ | 3-4 hrs |
| Video (YouTube-like) | CDN, Transcoding, Streaming | ⭐⭐⭐⭐ | 3-4 hrs |
| Content Moderation Platform | Calibration, reviewer queues, policy rollout safety | ⭐⭐⭐⭐ | 3-4 hrs |
| Bot Detection Platform | Adversarial signals, staged remediation, adaptation loops | ⭐⭐⭐⭐ | 3-4 hrs |
| Payment System | Idempotency, Distributed Transactions, Ledger, Reconciliation | ⭐⭐⭐⭐ | 3-4 hrs |
| Web Crawler | Frontier, Politeness, Deduplication | ⭐⭐⭐⭐ | 3-4 hrs |
| Ad Click Aggregator | Stream aggregation, Idempotency, Replay, Late events | ⭐⭐⭐⭐ | 3-4 hrs |
| Metrics Monitoring | TSDB, Alerts, Cardinality controls | ⭐⭐⭐⭐ | 3-4 hrs |

**Key File:** [DESIGN-TEMPLATE.md](./04-hld-projects/DESIGN-TEMPLATE.md) - Interview framework

Recommendation ranking practice: [Video Recommendations](./04-hld-projects/video-recommendations/) covers candidate generation -> light ranker -> heavy ranker -> reranker with latency and fairness follow-ups.

---

### resources/ - Study Materials

| Folder | Contents | When to Use |
|--------|----------|-------------|
| `study-plans/` | 1-week, 1-month, topic-based plans | Start of preparation |
| `cheatsheets/` | Complexity, patterns, components, trade-offs | Review & interviews |
| `interview-tips/` | LLD/HLD/behavioral/salary-negotiation guides, communication, pitfalls | Before interviews |
| `templates/` | LLD/HLD/behavioral/salary-negotiation practice templates | During practice |

---

## 📝 How to Practice

### For LLD Projects

Follow this structured approach using [HOW-TO-APPROACH.md](./02-lld-projects/HOW-TO-APPROACH.md):

```
1. Read the Problem (5 min)
   ├── Understand requirements
   ├── Note key entities
   └── Identify constraints

2. Attempt Solution (30-45 min)
   ├── Clarify requirements
   ├── Identify core entities
   ├── Map relationships
   ├── Choose design patterns
   ├── Design classes
   └── Handle edge cases

3. Compare with Solution (15 min)
   ├── Note differences
   ├── Understand trade-offs
   └── Learn new patterns

4. Refactor & Document (10 min)
   ├── Apply learnings
   └── Note key takeaways
```

**📌 Pro Tip:** Use the [LLD Template](./resources/templates/lld-template.md) for consistent practice.

---

### For HLD Projects

Use the interview framework from [DESIGN-TEMPLATE.md](./04-hld-projects/DESIGN-TEMPLATE.md):

```
1. Requirements (5-10 min)
   ├── Functional: What should it do?
   ├── Non-functional: Scale, latency, availability
   └── Clarify assumptions

2. Estimation (5 min)
   ├── QPS calculations
   ├── Storage needs
   └── Bandwidth requirements

3. API Design (5-10 min)
   ├── Core endpoints
   ├── Request/response format
   └── Pagination, errors

4. Data Model (5-10 min)
   ├── Schema design
   ├── Database choice (SQL vs NoSQL)
   └── Indexing strategy

5. High-Level Architecture (15-20 min)
   ├── Draw components
   ├── Data flow (read/write paths)
   └── Technology choices

6. Deep Dives (10-15 min)
   ├── Scaling approach
   ├── Caching strategy
   └── Key algorithm details

7. Trade-offs (5 min)
   ├── Alternatives considered
   └── Justification for choices
```

**📌 Pro Tip:** Use the [HLD Template](./resources/templates/hld-template.md) for structured practice.

---

### For Design Patterns

Follow the Theory → Implementation → Application flow:

```
1. Understand the Pattern (10 min)
   ├── Problem it solves
   ├── When to use
   └── Structure/UML

2. Study Implementation (15-20 min)
   ├── Review code in Java/Python
   └── Understand each component

3. Apply to Real Problems (15-20 min)
   ├── Find usage in LLD projects
   └── Identify applications in your experience
```

---

## 🧭 Navigation Tips

### Emoji Legend

| Emoji | Meaning |
|-------|---------|
| 📚 | Theory/Concept explanation |
| 🏗️ | Implementation/Code |
| ❓ | Interview Q&A |
| ⭐ | Difficulty level |
| 🔗 | Cross-reference link |
| 📌 | Pro tip |
| ⚠️ | Common pitfall |
| ✅ | Best practice |
| 🔜 | Coming soon |

### Cross-Reference Strategy

Each topic links to related content:
- **Patterns** → Link to projects that use them
- **Projects** → Link to concepts they demonstrate
- **Concepts** → Link to practical applications

### Version Progression

For LLD and HLD projects, we follow a versioning approach:
- **v1**: Basic working solution
- **v2**: Optimized with patterns
- **v3**: Production-ready with edge cases

Start with v1 to understand core logic, then progress to v3.

---

## ⏱️ Time Estimates

Plan your study sessions with these estimates:

| Content Type | Time Per Item | Notes |
|--------------|---------------|-------|
| Theory Topic | 30-60 min | Read + take notes |
| Design Pattern | 30-45 min | Theory + implementation |
| LLD Project | 45-90 min | Depends on complexity |
| HLD Concept | 30-45 min | Theory + examples |
| HLD Project | 2-3 hours | Full design exercise |
| Cheatsheet Review | 15-30 min | Quick reference |
| Mock Interview | 45-60 min | Timed practice |

---

## ❓ FAQ

### Which programming language should I focus on?
**A:** Choose the language you're most comfortable with for interviews. Both Java and Python implementations are provided. Most interviewers don't care which language you use as long as you can express your ideas clearly.

### Should I memorize all design patterns?
**A:** No. Focus on understanding when to use each pattern rather than memorizing structure. Know the top 6-8 patterns well (Singleton, Factory, Strategy, Observer, Decorator, State, Command, Adapter). You can always look up others.

### How much time per day should I study?
**A:** Quality over quantity. 2-3 focused hours daily is better than 6 distracted hours. Consistency matters more than intensity. Take breaks to avoid burnout.

### Can I use this for coding interviews too?
**A:** Yes for the core interview pattern breadth. The [05-coding-problems](./05-coding-problems/) section now has live [Two Pointers](./05-coding-problems/two-pointers/README.md), [Sliding Window](./05-coding-problems/sliding-window/README.md), [Binary Search](./05-coding-problems/binary-search/README.md), [BFS/DFS](./05-coding-problems/bfs-dfs/README.md), [Dynamic Programming](./05-coding-problems/dynamic-programming/README.md), [Greedy](./05-coding-problems/greedy/README.md), [Backtracking](./05-coding-problems/backtracking/README.md), [Heap / Priority Queue](./05-coding-problems/heap-priority-queue/README.md), [Trie](./05-coding-problems/trie/README.md), and [Union-Find](./05-coding-problems/union-find/README.md) packs. For comprehensive coding prep, pair this with timed problem practice.

### What's the difference between LLD and HLD?
**A:** 
- **LLD (Low-Level Design)**: Focus on classes, methods, OOP principles. Design a parking lot system with actual code.
- **HLD (High-Level Design)**: Focus on distributed systems, scalability. Design Twitter for 500M users.

See [CONCEPTS.md - LLD vs HLD](./CONCEPTS.md#-lld-vs-hld) for detailed comparison.

### How do I know I'm ready for interviews?
**A:** You're ready when you can:
- [ ] Explain any HLD project without notes in 45 minutes
- [ ] Design a new LLD system using the 7-step framework
- [ ] Discuss trade-offs for any component choice
- [ ] Handle follow-up questions gracefully
- [ ] Finish mock interviews within time limits

### What if I only have 3 days?
**A:** Focus on:
1. **Day 1**: Review [CONCEPTS.md](./CONCEPTS.md), practice URL Shortener
2. **Day 2**: Practice Twitter + Parking Lot
3. **Day 3**: Review [cheatsheets](./resources/cheatsheets/), practice explaining designs out loud

---

## 📋 Recommended First Steps

1. 📖 **Read [CONCEPTS.md](./CONCEPTS.md)** for a quick overview of everything
2. 📅 **Pick your study mode** from above based on your timeline
3. 🔖 **Bookmark this page** for easy navigation
4. ✅ **Track progress** using the checklist in main [README](./README.md)
5. 📝 **Start with one topic** and go deep before moving on

---

## 🔗 Quick Links

| Resource | Description |
|----------|-------------|
| [📋 CONCEPTS.md](./CONCEPTS.md) | Quick reference cheatsheet |
| [📊 Pattern Decision Tree](./resources/cheatsheets/pattern-decision-tree.md) | Which pattern to use |
| [🗺️ HLD Components Map](./resources/cheatsheets/hld-components-map.md) | System design building blocks |
| [⚖️ Trade-offs Matrix](./resources/cheatsheets/trade-offs-matrix.md) | Common design trade-offs |
| [📋 LLD Checklist](./resources/interview-tips/lld-checklist.md) | Step-by-step LLD approach |
| [🏗️ HLD Checklist](./resources/interview-tips/hld-checklist.md) | System design framework |
| [🧠 Behavioral Interview Framework](./resources/interview-tips/behavioral-interview-framework.md) | Decode/select/deliver loop for behavioral rounds |
| [🧠 Behavioral Interviews Quiz](./quizzes/behavioral-interviews-quiz.md) | 36-question behavioral execution check |
| [💬 Salary Negotiation Playbook](./resources/interview-tips/salary-negotiation-playbook.md) | Offer-stage negotiation framework with stakeholder routing and component strategy |
| [💬 Salary Negotiation Quiz](./quizzes/salary-negotiation-quiz.md) | 36-question salary negotiation execution check |

---

<p align="center">
  <b>Ready to start? Pick a section and begin! 🎯</b>
</p>
