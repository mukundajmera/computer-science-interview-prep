# Content Map & Future Architecture — Phase 1

> **Purpose:** Define the future content architecture for every top-level area,
> including a complete Generative AI System Design track. This document is the
> output of Prompt 1. It specifies **what** to build and **where**, without
> creating or editing any files yet.

> **Current status note (2026-06-13):** This is a historical future-architecture
> plan with an implementation log. Use
> [`resources/CONTENT-UI-MAP.md`](resources/CONTENT-UI-MAP.md) for live portal
> coverage/counts.

---

## 0. Implementation Update (March 31, 2026)

The Core Concepts 06-09 integration is now implemented across learning, practice, assessment, and demo layers:

- ✅ Added CAP concept pack: `03-hld-concepts/cap-theorem/THEORY.md` + `INTERVIEW-QA.md`
- ✅ Upgraded sharding and consistent hashing concept packs with requirements/rubrics/pitfalls/follow-ups
- ✅ Refreshed theory layer:
  - `00-theory/system-design-fundamentals/cap-theorem.md`
  - `00-theory/database-concepts/sharding.md`
  - `00-theory/cheat-sheets/performance-numbers.md`
- ✅ Added LLD concurrency foundations article:
  - `00-theory/system-design-fundamentals/concurrency-in-lld.md`
- ✅ Added practice assets:
  - `resources/templates/practice-hld-core-concepts.md`
  - `solutions/hld-core-concepts-scaling-judgment.md`
- ✅ Synced assessment artifacts:
  - `quizzes/hld-concepts-quiz.md` (+ answers)
  - `flashcards/hld-concepts.md`
- ✅ Updated Java/Python v3 demos for sharding and consistent hashing to include remap/hotspot/failure narratives
- ✅ Added source 24-28 expansion packs:
  - `04-hld-projects/job-scheduler/`
  - `04-hld-projects/web-crawler/`
  - `04-hld-projects/ad-click-aggregator/`
  - `04-hld-projects/payment-system/`
  - `04-hld-projects/metrics-monitoring/`
- ✅ Added ML SD 04-07 integration packs:
  - `04-hld-projects/content-moderation-platform/`
  - `04-hld-projects/bot-detection-platform/`
  - `04-hld-projects/video-recommendations/` recommendation ranking subsystem
- ✅ Updated `04-hld-projects/realtime-metrics-platform/` as advanced sibling for metrics-monitoring.
- ✅ Added dual-language LLD tracks:
  - `02-lld-projects/job-scheduler/`
  - `02-lld-projects/web-crawler/`
  - `02-lld-projects/ad-click-aggregator/`
  - `02-lld-projects/payment-system/`
- ✅ Integrated source-set 04-08 LLD upgrades:
  - Added `02-lld-projects/inventory-management/` (full docs + Java/Python v1/v2/v3 + tests)
  - Added/updated rubric, pitfalls, follow-ups for Parking Lot, File System, Movie Ticket Booking, and Rate Limiter
  - Expanded LLD assessment assets (quiz + answers + flashcards)
- ✅ Applied Concurrency Upgrade Plan v2 (correctness/coordination/scarcity):
  - Refreshed `movie-ticket-booking`, `rate-limiter`, and `job-scheduler` docs with unified rubric/pitfall/follow-up structure
  - Added concurrency-oriented theory/index cross-links and assessment deltas
  - Aligned `movie-ticket-booking` v3 API contracts with Python/Java test surfaces
- ✅ Added new HLD coach answers:
  - `solutions/hld-job-scheduler.md`
  - `solutions/hld-web-crawler.md`
  - `solutions/hld-ad-click-aggregator.md`
  - `solutions/hld-payment-system.md`
  - `solutions/hld-metrics-monitoring.md`
- ✅ Added full behavioral interview track:
  - `resources/interview-tips/behavioral-*.md` playbooks + `behavioral-interview-framework.md`
  - `resources/templates/behavioral-story-template.md`
  - `quizzes/behavioral-interviews-quiz.md` (+ answers)
  - `flashcards/behavioral-interviews.md`
  - `solutions/behavioral-big-three.md`, `behavioral-leadership-deep-dive.md`, `behavioral-special-rounds.md`
- ✅ Added full salary negotiation track:
  - `resources/interview-tips/salary-negotiation-playbook.md`
  - `resources/templates/practice-salary-negotiation.md`, `resources/templates/salary-negotiation-mock-scorecard.md`
  - `quizzes/salary-negotiation-quiz.md` (+ answers)
  - `flashcards/salary-negotiation.md`
  - `solutions/salary-negotiation-coach-answer.md`

---

## 1. Updated Content Map by Section

### 00-theory — Core CS Fundamentals

**Current state:** ✅ Complete — 8 topic areas, 36 markdown articles, including Merkle Tree and Trie theory articles.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **CAP Theorem & Consistency Models** article | `00-theory/system-design-fundamentals/cap-theorem.md` | ✅ Created as standalone theory article for distributed systems trade-off discussions |
| 2 | **Back-of-Envelope Estimation** article | `00-theory/system-design-fundamentals/back-of-envelope.md` | ✅ Created with interview-oriented QPS/storage/bandwidth estimation flow |
| 3 | **Common Trade-offs Cheatsheet** | `00-theory/cheat-sheets/common-tradeoffs.md` | Quick-reference for latency vs consistency, SQL vs NoSQL, push vs pull, etc. |
| 4 | **GenAI Fundamentals Primer** | `00-theory/genai-fundamentals/README.md` | Bridge article: "What every system designer should know about LLMs" — tokens, embeddings, inference, fine-tuning basics |
| 5 | **Concurrency in LLD** article | `00-theory/system-design-fundamentals/concurrency-in-lld.md` | ✅ Created as canonical correctness/coordination/scarcity bridge to advanced LLD modules |
| 6 | **Merkle Tree** article | `00-theory/big-data-structures/merkle-tree.md` | ✅ Created as the canonical hash-tree, proof-path, and anti-entropy synchronization primer |
| 7 | **Trie** article | `00-theory/big-data-structures/trie.md` | ✅ Created as the canonical prefix-index, autocomplete, wildcard, and compressed-trie primer |

---

### 01-design-patterns — GoF Patterns

**Current state:** ⚠️ Catalog present — 23 GoF patterns with Java/Python examples; v2/v3 progression and full test coverage are still tracked in `01-design-patterns/COMPLETION-MATRIX.md`.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Pattern Selection Flowchart** | `01-design-patterns/PATTERN-SELECTION.md` | Interactive decision tree: "Given problem X, which pattern?" Consolidates `pattern-decision-tree.md` cheatsheet into the patterns section |
| 2 | **Pattern Comparison Tables** | `01-design-patterns/COMPARISONS.md` | Strategy vs State, Factory vs Abstract Factory, Adapter vs Facade, Decorator vs Proxy — side-by-side tables |
| 3 | **Common Pitfalls per Category** | `01-design-patterns/PITFALLS.md` | "Top mistakes when applying creational / structural / behavioral patterns" — sourced from interview feedback |
| 4 | **Patterns-in-LLD Cross-Reference** | `01-design-patterns/LLD-CROSS-REFERENCE.md` | Table mapping each pattern → which LLD projects use it, with links |

---

### 02-lld-projects — Low-Level Design Projects

**Current state:** ⚠️ Catalog present — broad project set with v1/v2/v3 tracks; coaching-doc coverage is validated in the dirty tree and code walkthrough/test-quality review remains tracked.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Scoring Rubric per project** | `02-lld-projects/<project>/RUBRIC.md` | Dimensions: requirements gathering, class design, pattern usage, extensibility, edge cases — each scored 1-5 |
| 2 | **Common Pitfalls per project** | `02-lld-projects/<project>/PITFALLS.md` | Top 5 mistakes interviewers see for each problem |
| 3 | **Follow-Up Variants** | `02-lld-projects/<project>/FOLLOW-UPS.md` | "What if we add X?", "How would this change at scale?" — 3-5 variants per project |
| 4 | **LLD Comparison Matrix** | `02-lld-projects/COMPARISON-MATRIX.md` | Table comparing all LLD projects by complexity, patterns used, data structures, and key design decisions |
| 5 | **Self-Review Checklist** | `02-lld-projects/SELF-REVIEW-CHECKLIST.md` | Generic post-practice checklist: "Did I identify all entities?", "Did I apply SOLID?", etc. |

---

### 03-hld-concepts — System Design Building Blocks

**Current state:** ⚠️ Catalog present — 42 concept directories are portal-visible; SQL fundamentals, MySQL, and MongoDB now have first-level concept pages and interview drills, while broader comparison/follow-up packs remain tracked below.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Concept Comparison Tables** | `03-hld-concepts/COMPARISONS.md` | Side-by-side: "Caching vs CDN", "Sharding vs Replication", "Message Queues vs Event Streams" |
| 2 | **When-to-Use Decision Guide** | `03-hld-concepts/DECISION-GUIDE.md` | Flowchart: given a requirement (high availability, low latency, high throughput), which concepts to apply |
| 3 | **Interview Follow-Ups** | `03-hld-concepts/FOLLOW-UPS.md` | Common interviewer follow-up questions per concept: "What happens when the cache goes down?", "How do you handle hot partitions?" |
| 4 | **Concept-to-System Map** | `03-hld-concepts/SYSTEM-MAP.md` | Table: which HLD projects (04) and case studies use each concept |
| 5 | **Real-time Updates Pack** | `03-hld-concepts/real-time-updates/` | Channel selection, downgrade rules, fanout patterns with Java/Python demos |
| 6 | **Contention Control Pack** | `03-hld-concepts/contention-control/` | Optimistic vs pessimistic vs serial queue vs distributed lock with escalation matrix and demos |
| 7 | **Workflow Orchestration Pack** | `03-hld-concepts/workflow-orchestration/` | Durable saga/orchestrator triggers, idempotency, compensation with demos |

---

### 04-hld-projects — HLD System Designs

**Current state:** ⚠️ Doc-pack catalog present — diagram-source and code-depth hardening remain open.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Scoring Rubric per project** | `04-hld-projects/<project>/RUBRIC.md` | Dimensions: requirements, estimation, API design, data model, architecture, deep dives, trade-offs — each scored 1-5 with "strong answer" outline |
| 2 | **Common Pitfalls per project** | `04-hld-projects/<project>/PITFALLS.md` | Top 5-7 mistakes for each system design problem |
| 3 | **Comparison Table per project** | `04-hld-projects/<project>/COMPARISON.md` | "How this design differs from similar systems" (e.g., URL Shortener vs Pastebin, Chat Service vs Notification Service) |
| 4 | **Follow-Up Variants** | `04-hld-projects/<project>/FOLLOW-UPS.md` | Extension scenarios: "Add real-time features", "Scale to 10x", "Add ML-based recommendations" |
| 5 | **Strong Answer Outline** | `04-hld-projects/<project>/STRONG-ANSWER.md` | "Model answer" structure an interviewer would rate as hire — time-boxed breakdown |

---

### 05-coding-problems — Algorithm Patterns

**Current state:** ✅ Core coding breadth complete — Two Pointers, Sliding Window, Binary Search, BFS/DFS, Dynamic Programming, Greedy, Backtracking, Heap / Priority Queue, Trie, and Union-Find pattern packs are live (`README` + 8 guided pages each).

> **Note:** Per North Star, this section is a non-core supplement.
> Current focus is expanding breadth through high-quality pattern verticals rather than placeholder lists.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Two Pointers Vertical (Delivered)** | `05-coding-problems/two-pointers/README.md` + `01-08` topic pages | End-to-end pattern track with requirements, approach, scoring, pitfalls, and follow-ups |
| 2 | **Sliding Window Vertical (Delivered)** | `05-coding-problems/sliding-window/README.md` + `01-08` topic pages | End-to-end pattern track for contiguous ranges, rolling state, frequency windows, and deque windows |
| 3 | **Binary Search Vertical (Delivered)** | `05-coding-problems/binary-search/README.md` + `01-08` topic pages | End-to-end pattern track for exact search, lower bound, rotated arrays, answer-space search, and matrix/index lookup |
| 4 | **BFS/DFS Vertical (Delivered)** | `05-coding-problems/bfs-dfs/README.md` + `01-08` topic pages | End-to-end graph/tree/grid traversal track with visited discipline, shortest unweighted paths, dependency cycles, and reachability |
| 5 | **Dynamic Programming Vertical (Delivered)** | `05-coding-problems/dynamic-programming/README.md` + `01-08` topic pages | End-to-end DP track with state, transition, base cases, sequence DP, feasibility DP, and grid DP |
| 6 | **Greedy Vertical (Delivered)** | `05-coding-problems/greedy/README.md` + `01-08` topic pages | End-to-end proof-first greedy track with intervals, reachability, balance reset, partition boundaries, and endpoint coverage |
| 7 | **Backtracking Vertical (Delivered)** | `05-coding-problems/backtracking/README.md` + `01-08` topic pages | End-to-end decision-tree search track with duplicate handling, pruning, board search, partitioning, and constraint solving |
| 8 | **Heap / Priority Queue Vertical (Delivered)** | `05-coding-problems/heap-priority-queue/README.md` + `01-08` topic pages | End-to-end priority retrieval track with top-K, kth selection, merge-K streams, streaming median, cooldown scheduling, and distance ranking |
| 9 | **Trie Vertical (Delivered)** | `05-coding-problems/trie/README.md` + `01-08` topic pages | End-to-end prefix-index track with wildcard search, prefix aggregates, board pruning, autocomplete, and lexicographic construction |
| 10 | **Union-Find Vertical (Delivered)** | `05-coding-problems/union-find/README.md` + `01-08` topic pages | End-to-end disjoint-set track with component counts, cycle detection, identity merging, row/column grouping, and equality constraints |
| 11 | **Pattern-to-SD Map (Delivered)** | `05-coding-problems/PATTERN-SD-MAP.md` | Maps algorithm templates to distributed-system components and trade-off decisions |
| 12 | **Top Coding Practice Ladder (Delivered)** | `05-coding-problems/TOP-20.md` | Curated internal practice order with difficulty, core insight, related repo content, time targets, and Wave 3 extension rows |

---

### 06-genai-systems — Generative AI System Design

**Current state:** ⚠️ Active refresh — 12 concept folders, 9 GenAI LLD projects, and 7 GenAI HLD projects are present; verify exact counts with `scripts/check_content_inventory.py`.

#### 6a. Concepts to Complete

| # | New Artifact | Path | Status |
|---|-------------|------|--------|
| 1 | **Vector Databases** | `06-genai-systems/00-concepts/vector-databases/README.md` | ✅ Exists; currentness review tracked |
| 2 | **Model Routing & Orchestration** | `06-genai-systems/00-concepts/model-routing-orchestration/README.md` | ✅ Exists; currentness review tracked |
| 3 | **Streaming & KV-Cache** | `06-genai-systems/00-concepts/streaming-kv-cache/README.md` | ✅ Exists; currentness review tracked |
| 4 | **Token / Cost / Latency Planning** | `06-genai-systems/00-concepts/token-cost-latency/README.md` | ✅ Exists; currentness review tracked |
| 5 | **GenAI Design Patterns** | `06-genai-systems/00-concepts/genai-design-patterns/README.md` | ✅ Exists; currentness review tracked |

#### 6b. LLD Components to Complete

| # | New Artifact | Path | Status |
|---|-------------|------|--------|
| 1 | **Embedding Service** | `06-genai-systems/01-llm-lld-projects/embedding-service/` | ✅ Exists with Python implementation/tests |
| 2 | **Tool Router** | `06-genai-systems/01-llm-lld-projects/tool-router/` | ✅ Exists with Python implementation/tests |
| 3 | **Evaluation Harness** | `06-genai-systems/01-llm-lld-projects/evaluation-harness/` | ✅ Exists with Python implementation/tests |

#### 6c. New Framework Document

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **How to Answer Any GenAI SD Question** | `06-genai-systems/GENAI-SD-FRAMEWORK.md` | Reusable 6-step framework: (1) Clarify use case & LLM role, (2) Estimate token budgets & costs, (3) Sketch architecture (retrieval? agents? streaming?), (4) Deep-dive the LLM pipeline, (5) Safety & guardrails, (6) Evaluation & observability. Expands on the existing one-pager cheatsheet into a full guide. |

#### 6d. Section-Level Supplementary Artifacts

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **GenAI Pitfalls Guide** | `06-genai-systems/PITFALLS.md` | Top 10 GenAI SD interview mistakes (ignoring safety, not estimating token costs, over-engineering agents, etc.) |
| 2 | **GenAI vs Classic SD Comparison** | `06-genai-systems/CLASSIC-VS-GENAI.md` | Side-by-side: how GenAI SD interviews differ from classic SD in scope, trade-offs, evaluation, and follow-ups |
| 3 | **GenAI HLD Scoring Rubric** | `06-genai-systems/02-llm-hld-projects/RUBRIC.md` | Shared rubric for all GenAI HLD problems: LLM pipeline design, safety, cost awareness, retrieval quality, evaluation plan |

---

### case-studies — Real Company Architectures

**Current state:** ⚠️ Existing catalog present — 12 deep-dive studies are visible in the dirty tree; the two GenAI-era studies require source/provenance review before this lane marks them accepted.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Cross-Study Comparison Table** | `case-studies/COMPARISON-TABLE.md` | Matrix: all current studies compared by scale, primary patterns, data stores, key trade-offs |
| 2 | **Interview Relevance Guide** | `case-studies/INTERVIEW-GUIDE.md` | "If asked to design X, study Y" — maps interview problems to most relevant case studies |
| 3 | **GenAI Case Studies** (concurrent work detected) | `case-studies/chatgpt-inference/README.md`, `case-studies/github-copilot/README.md` | Modern GenAI architecture case studies to complement the GenAI track; source/provenance review required before acceptance |

---

### resources — Study Aids

**Current state:** ⚠️ Supporting catalog present — study plans, cheatsheets, interview tips, and templates exist; assessment coverage mapping remains active.

| # | New Artifact | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Integrated Study Plan** | `resources/study-plans/integrated-plan.md` | Single plan weaving classic SD + GenAI SD + practice, replacing the need to cross-reference multiple plans |
| 2 | **GenAI Interview Checklist** | `resources/interview-tips/genai-checklist.md` | Complements existing `lld-checklist.md` and `hld-checklist.md` |
| 3 | **Practice Template: GenAI HLD** | `resources/templates/genai-hld-template.md` | Complements existing `lld-template.md` and `hld-template.md` |
| 4 | **Behavioral Interview Suite** | `resources/interview-tips/behavioral-*.md` + `resources/templates/behavioral-story-template.md` | Adds interviewer-signal-based behavioral preparation, pitfalls, and practice loops |
| 5 | **Salary Negotiation Suite** | `resources/interview-tips/salary-negotiation-playbook.md` + `resources/templates/practice-salary-negotiation.md` + `resources/templates/salary-negotiation-mock-scorecard.md` | Adds offer-stage negotiation framework, simulation template, and scoring workflow with Global/India adaptations |

---

### flashcards — Question Decks

**Current state:** ✅ 20 decks (design-patterns, lld-concepts, hld-concepts, infra-technologies, genai-system-design, ai-coding-interview, ai-coding-interviews, applied-ml-system-design, two-pointers, sliding-window, binary-search, bfs-dfs, dynamic-programming, greedy, backtracking, heap-priority-queue, trie, union-find, behavioral-interviews, salary-negotiation). The singular AI coding deck covers AI-assisted build ownership; the plural deck covers AI-enabled interview format strategy.

| # | Live Deck | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Design Patterns** | `flashcards/design-patterns.md` | GoF pattern recognition and trade-offs |
| 2 | **LLD Concepts** | `flashcards/lld-concepts.md` | Object modeling, APIs, and class-design prompts |
| 3 | **HLD Concepts** | `flashcards/hld-concepts.md` | Core distributed-system building blocks |
| 4 | **Infrastructure Technologies** | `flashcards/infra-technologies.md` | Datastores, queues, caches, networking, and ops |
| 5 | **GenAI System Design** | `flashcards/genai-system-design.md` | RAG, safety/eval, routing, token economics, agents, GenAI LLD components, and HLD drills |
| 6 | **Two Pointers** | `flashcards/two-pointers.md` | Array/string pointer invariants |
| 7 | **Sliding Window** | `flashcards/sliding-window.md` | Fixed and variable window recognition |
| 8 | **Binary Search** | `flashcards/binary-search.md` | Boundary-search templates and pitfalls |
| 9 | **BFS/DFS** | `flashcards/bfs-dfs.md` | Traversal frontier, visited, and graph-state recall |
| 10 | **Dynamic Programming** | `flashcards/dynamic-programming.md` | State, transition, base-case, and reconstruction drills |
| 11 | **Greedy** | `flashcards/greedy.md` | Exchange, stays-ahead, boundary, and counterexample recall |
| 12 | **Backtracking** | `flashcards/backtracking.md` | Decision-tree, pruning, duplicate-suppression, and constraint-search recall |
| 13 | **Heap / Priority Queue** | `flashcards/heap-priority-queue.md` | Top-K, merge, median, cooldown, stale-entry, and tie-policy recall |
| 14 | **Trie** | `flashcards/trie.md` | Prefix indexes, terminal markers, wildcard branching, autocomplete, and board-pruning recall |
| 15 | **Union-Find** | `flashcards/union-find.md` | DSU roots, path compression, component counting, identity merge, and equality-constraint recall |
| 16 | **AI Coding Interview** | `flashcards/ai-coding-interview.md` | AI-assisted build ownership and review |
| 17 | **AI Coding Interviews** | `flashcards/ai-coding-interviews.md` | AI-enabled interview format strategy |
| 18 | **Applied ML System Design** | `flashcards/applied-ml-system-design.md` | ML design, evaluation, and serving trade-offs |
| 19 | **Behavioral Interviews** | `flashcards/behavioral-interviews.md` | Story structure and interviewer-signal drills |
| 20 | **Salary Negotiation** | `flashcards/salary-negotiation.md` | Offer-stage strategy and compensation levers |

---

### quizzes — Assessment

**Current state:** ✅ 22 active quizzes for design patterns, LLD, LLD interview delivery, HLD, infrastructure, GenAI system design, coding, GenAI-adjacent AI coding, applied ML, behavioral, and negotiation practice. Verify exact counts with `scripts/check_content_inventory.py`.

| # | Live Quiz | Path | Rationale |
|---|-------------|------|-----------|
| 1 | **Design Patterns** | `quizzes/design-patterns-quiz.md` + `quizzes/answers/design-patterns-answers.md` | Pattern recognition and trade-offs |
| 2 | **LLD Projects** | `quizzes/lld-projects-quiz.md` + `quizzes/answers/lld-projects-answers.md` | LLD problem and rubric practice |
| 3 | **LLD Interview Framework** | `quizzes/lld-interview-framework-quiz.md` + `quizzes/answers/lld-interview-framework-answers.md` | Delivery rhythm and scoring practice |
| 4 | **HLD Concepts** | `quizzes/hld-concepts-quiz.md` + `quizzes/answers/hld-concepts-answers.md` | Core distributed-system concepts |
| 5 | **HLD Projects** | `quizzes/hld-projects-quiz.md` + `quizzes/answers/hld-projects-answers.md` | Full-system design decisions |
| 6 | **Infrastructure Technologies** | `quizzes/infra-technologies-quiz.md` + `quizzes/answers/infra-technologies-answers.md` | Datastore, queue, cache, and ops decisions |
| 7 | **GenAI System Design** | `quizzes/genai-system-design-quiz.md` + `quizzes/answers/genai-system-design-answers.md` | RAG, safety/eval, routing, token economics, agents, GenAI LLD components, and HLD drills |
| 8 | **Two Pointers** | `quizzes/two-pointers-quiz.md` + `quizzes/answers/two-pointers-answers.md` | Pointer movement and invariant checks |
| 9 | **Sliding Window** | `quizzes/sliding-window-quiz.md` + `quizzes/answers/sliding-window-answers.md` | Window-recognition drills |
| 10 | **Binary Search** | `quizzes/binary-search-quiz.md` + `quizzes/answers/binary-search-answers.md` | Boundary-search practice |
| 11 | **BFS/DFS** | `quizzes/bfs-dfs-quiz.md` + `quizzes/answers/bfs-dfs-answers.md` | Traversal and graph-state practice |
| 12 | **Dynamic Programming** | `quizzes/dynamic-programming-quiz.md` + `quizzes/answers/dynamic-programming-answers.md` | State/transition/base-case practice |
| 13 | **Greedy** | `quizzes/greedy-quiz.md` + `quizzes/answers/greedy-answers.md` | Proof-first greedy and counterexample practice |
| 14 | **Backtracking** | `quizzes/backtracking-quiz.md` + `quizzes/answers/backtracking-answers.md` | Decision-tree search, pruning, duplicate suppression, and constraint solving |
| 15 | **Heap / Priority Queue** | `quizzes/heap-priority-queue-quiz.md` + `quizzes/answers/heap-priority-queue-answers.md` | Top-K, merge, median, cooldown, stale entries, and tie policies |
| 16 | **Trie** | `quizzes/trie-quiz.md` + `quizzes/answers/trie-answers.md` | Prefix-index, wildcard, autocomplete, and board-pruning practice |
| 17 | **Union-Find** | `quizzes/union-find-quiz.md` + `quizzes/answers/union-find-answers.md` | DSU roots, component counting, cycle detection, and identity-merge practice |
| 18 | **AI Coding Interview** | `quizzes/ai-coding-interview-quiz.md` + `quizzes/answers/ai-coding-interview-answers.md` | AI-assisted coding workflow |
| 19 | **AI Coding Interviews** | `quizzes/ai-coding-interviews-quiz.md` + `quizzes/answers/ai-coding-interviews-answers.md` | AI-enabled interview format strategy |
| 20 | **Applied ML System Design** | `quizzes/applied-ml-system-design-quiz.md` + `quizzes/answers/applied-ml-system-design-answers.md` | ML system design practice |
| 21 | **Behavioral Interviews** | `quizzes/behavioral-interviews-quiz.md` + `quizzes/answers/behavioral-interviews-answers.md` | Story, signal, and follow-up drills |
| 22 | **Salary Negotiation** | `quizzes/salary-negotiation-quiz.md` + `quizzes/answers/salary-negotiation-answers.md` | Offer-stage strategy and compensation levers |

---

## 2. GenAI Track — Historical Definition And Current State

### Learning Path

```
00-theory/genai-fundamentals/           → "What every SD person needs to know about LLMs"
        ↓
06-genai-systems/00-concepts/           → 12 concept deep-dives (RAG, vector DBs, routing, safety, evaluation, cost, patterns, …)
        ↓
06-genai-systems/01-llm-lld-projects/   → 9 component-level builds (Python, v1 → v3)
        ↓
06-genai-systems/02-llm-hld-projects/   → 7 flagship system designs (docs + diagrams)
        ↓
06-genai-systems/GENAI-SD-FRAMEWORK.md  → Reusable interview framework
        ↓
case-studies/chatgpt-inference/         → GenAI-era deep dives visible in dirty tree; source review required
case-studies/github-copilot/
```

### Concept Coverage (12 total)

| Concept | File | Status |
|---------|------|--------|
| RAG Architecture | `00-concepts/rag-architecture/README.md` | ✅ Exists |
| LLM-Oriented System Design | `00-concepts/llm-system-design/README.md` | ✅ Exists |
| Prompting, Tools & Agents | `00-concepts/prompting-tools-agents/README.md` | ✅ Exists |
| Safety & Governance | `00-concepts/safety-governance/README.md` | ✅ Exists |
| LLM Evaluation | `00-concepts/llm-evaluation/README.md` | ✅ Exists |
| Safety & Eval (consolidated) | `00-concepts/safety-eval/README.md` | ✅ Exists — combines safety-governance + llm-evaluation into a single reference sheet |
| Vector Databases | `00-concepts/vector-databases/README.md` | ✅ Exists; currentness review tracked |
| Model Routing & Orchestration | `00-concepts/model-routing-orchestration/README.md` | ✅ Exists; currentness review tracked |
| Streaming & KV-Cache | `00-concepts/streaming-kv-cache/README.md` | ✅ Exists; currentness review tracked |

**Cross-cutting concepts:**

| Concept | File | Status |
|---------|------|--------|
| Token / Cost / Latency Planning | `00-concepts/token-cost-latency/README.md` | ✅ Exists; currentness review tracked |
| GenAI Design Patterns | `00-concepts/genai-design-patterns/README.md` | ✅ Exists; currentness review tracked |

### LLD Components (9 total)

| Component | Directory | Status |
|-----------|-----------|--------|
| Chunker & Metadata Indexer | `01-llm-lld-projects/chunker-metadata-indexer/` | ✅ Coded |
| Retriever & Ranker | `01-llm-lld-projects/retriever-ranker/` | ✅ Coded |
| Prompt Builder | `01-llm-lld-projects/prompt-builder/` | ✅ Coded |
| Conversation Memory Store | `01-llm-lld-projects/conversation-memory-store/` | ✅ Coded |
| Safety Filter & Policy Engine | `01-llm-lld-projects/safety-filter-policy-engine/` | ✅ Coded |
| LLM Request Orchestrator | `01-llm-lld-projects/llm-request-orchestrator/` | ✅ Coded |
| Embedding Service | `01-llm-lld-projects/embedding-service/` | ✅ Coded |
| Tool Router | `01-llm-lld-projects/tool-router/` | ✅ Coded |
| Evaluation Harness | `01-llm-lld-projects/evaluation-harness/` | ✅ Coded |

### HLD Systems (7 total)

| System | Directory | Status |
|--------|-----------|--------|
| Document Q&A (RAG) | `02-llm-hld-projects/document-qa-rag/` | ✅ Designed |
| Multi-Tenant Chat Assistant | `02-llm-hld-projects/multi-tenant-chat-assistant/` | ✅ Designed |
| AI Coding Copilot | `02-llm-hld-projects/ai-coding-copilot/` | ✅ Designed |
| Agentic Workflow Orchestrator | `02-llm-hld-projects/agentic-workflow-orchestrator/` | ✅ Designed |
| LLM Evaluation & Safety Platform | `02-llm-hld-projects/llm-evaluation-safety-platform/` | ✅ Designed — focuses on observability, A/B testing, and online safety monitoring |
| LLM Safety & Eval Platform (Governance) | `02-llm-hld-projects/llm-safety-eval-platform/` | ✅ Designed — focuses on compliance, red-teaming, and regulatory reporting (EU AI Act / NIST) |
| Semantic Retrieval Platform | `02-llm-hld-projects/semantic-retrieval-platform/` | ✅ Designed — focuses on hybrid retrieval, index lifecycle, ranking quality, and retrieval operations |

### Framework Document

| Document | Path | Description |
|----------|------|-------------|
| **How to Answer Any GenAI SD Question** | `06-genai-systems/GENAI-SD-FRAMEWORK.md` | Comprehensive 6-step reusable framework expanding on the existing one-pager cheatsheet. Covers: clarify LLM role → estimate tokens/costs → sketch architecture → deep-dive pipeline → safety & guardrails → evaluation & observability. Includes a worked example. |

---

## 3. File-Level Plan — New Files to Create

### New Files (sorted by section)

```
# 00-theory (4 new files)
00-theory/system-design-fundamentals/cap-theorem.md
00-theory/system-design-fundamentals/back-of-envelope.md
00-theory/cheat-sheets/common-tradeoffs.md
00-theory/genai-fundamentals/README.md

# 01-design-patterns (4 new files)
01-design-patterns/PATTERN-SELECTION.md
01-design-patterns/COMPARISONS.md
01-design-patterns/PITFALLS.md
01-design-patterns/LLD-CROSS-REFERENCE.md

# 02-lld-projects (section-level files + per-project files)
02-lld-projects/COMPARISON-MATRIX.md
02-lld-projects/SELF-REVIEW-CHECKLIST.md
02-lld-projects/<each project>/RUBRIC.md
02-lld-projects/<each project>/PITFALLS.md
02-lld-projects/<each project>/FOLLOW-UPS.md

# 03-hld-concepts (4 new files)
03-hld-concepts/COMPARISONS.md
03-hld-concepts/DECISION-GUIDE.md
03-hld-concepts/FOLLOW-UPS.md
03-hld-concepts/SYSTEM-MAP.md

# 04-hld-projects (per-project files)
04-hld-projects/<each project>/RUBRIC.md
04-hld-projects/<each project>/PITFALLS.md
04-hld-projects/<each project>/COMPARISON.md
04-hld-projects/<each project>/FOLLOW-UPS.md
04-hld-projects/<each project>/STRONG-ANSWER.md

# 05-coding-problems (delivered pattern packs + pending expansions)
05-coding-problems/two-pointers/README.md
05-coding-problems/two-pointers/01-overview.md
05-coding-problems/two-pointers/02-container-with-most-water.md
05-coding-problems/two-pointers/03-two-sum-sorted-array.md
05-coding-problems/two-pointers/04-three-sum.md
05-coding-problems/two-pointers/05-valid-triangle-number.md
05-coding-problems/two-pointers/06-move-zeroes.md
05-coding-problems/two-pointers/07-sort-colors.md
05-coding-problems/two-pointers/08-trapping-rain-water.md
05-coding-problems/sliding-window/README.md
05-coding-problems/sliding-window/01-overview.md
05-coding-problems/sliding-window/02-maximum-sum-subarray-size-k.md
05-coding-problems/sliding-window/03-minimum-size-subarray-sum.md
05-coding-problems/sliding-window/04-longest-substring-without-repeating.md
05-coding-problems/sliding-window/05-longest-substring-at-most-k-distinct.md
05-coding-problems/sliding-window/06-subarrays-with-exactly-k-distinct.md
05-coding-problems/sliding-window/07-permutation-in-string.md
05-coding-problems/sliding-window/08-sliding-window-maximum.md
05-coding-problems/binary-search/README.md
05-coding-problems/binary-search/01-overview.md
05-coding-problems/binary-search/02-classic-binary-search.md
05-coding-problems/binary-search/03-first-position-lower-bound.md
05-coding-problems/binary-search/04-search-insert-position.md
05-coding-problems/binary-search/05-search-in-rotated-sorted-array.md
05-coding-problems/binary-search/06-find-minimum-in-rotated-sorted-array.md
05-coding-problems/binary-search/07-koko-eating-bananas.md
05-coding-problems/binary-search/08-search-a-2d-matrix.md
05-coding-problems/bfs-dfs/README.md
05-coding-problems/bfs-dfs/01-overview.md
05-coding-problems/bfs-dfs/02-binary-tree-level-order-traversal.md
05-coding-problems/bfs-dfs/03-number-of-islands.md
05-coding-problems/bfs-dfs/04-clone-graph.md
05-coding-problems/bfs-dfs/05-rotting-oranges.md
05-coding-problems/bfs-dfs/06-course-schedule.md
05-coding-problems/bfs-dfs/07-word-ladder.md
05-coding-problems/bfs-dfs/08-pacific-atlantic-water-flow.md
05-coding-problems/dynamic-programming/README.md
05-coding-problems/dynamic-programming/01-overview.md
05-coding-problems/dynamic-programming/02-climbing-stairs.md
05-coding-problems/dynamic-programming/03-house-robber.md
05-coding-problems/dynamic-programming/04-coin-change.md
05-coding-problems/dynamic-programming/05-longest-increasing-subsequence.md
05-coding-problems/dynamic-programming/06-longest-common-subsequence.md
05-coding-problems/dynamic-programming/07-word-break.md
05-coding-problems/dynamic-programming/08-unique-paths.md
05-coding-problems/greedy/README.md
05-coding-problems/greedy/01-overview.md
05-coding-problems/greedy/02-activity-selection.md
05-coding-problems/greedy/03-non-overlapping-intervals.md
05-coding-problems/greedy/04-jump-game.md
05-coding-problems/greedy/05-gas-station.md
05-coding-problems/greedy/06-partition-labels.md
05-coding-problems/greedy/07-best-time-to-buy-sell-stock.md
05-coding-problems/greedy/08-minimum-arrows-burst-balloons.md
05-coding-problems/backtracking/README.md
05-coding-problems/backtracking/01-overview.md
05-coding-problems/backtracking/02-subsets.md
05-coding-problems/backtracking/03-permutations.md
05-coding-problems/backtracking/04-combination-sum.md
05-coding-problems/backtracking/05-word-search.md
05-coding-problems/backtracking/06-palindrome-partitioning.md
05-coding-problems/backtracking/07-n-queens.md
05-coding-problems/backtracking/08-sudoku-solver.md
05-coding-problems/heap-priority-queue/README.md
05-coding-problems/heap-priority-queue/01-overview.md
05-coding-problems/heap-priority-queue/02-top-k-frequent-elements.md
05-coding-problems/heap-priority-queue/03-kth-largest-element.md
05-coding-problems/heap-priority-queue/04-merge-k-sorted-lists.md
05-coding-problems/heap-priority-queue/05-find-median-from-data-stream.md
05-coding-problems/heap-priority-queue/06-task-scheduler.md
05-coding-problems/heap-priority-queue/07-reorganize-string.md
05-coding-problems/heap-priority-queue/08-k-closest-points.md
05-coding-problems/PATTERN-SD-MAP.md
05-coding-problems/TOP-20.md

# 06-genai-systems (8 new files + 3 concept stubs + 3 LLD project stubs)
06-genai-systems/GENAI-SD-FRAMEWORK.md
06-genai-systems/PITFALLS.md
06-genai-systems/CLASSIC-VS-GENAI.md
06-genai-systems/00-concepts/token-cost-latency/README.md
06-genai-systems/00-concepts/genai-design-patterns/README.md
06-genai-systems/00-concepts/vector-databases/README.md         # fill existing stub
06-genai-systems/00-concepts/model-routing-orchestration/README.md  # fill existing stub
06-genai-systems/00-concepts/streaming-kv-cache/README.md       # fill existing stub
06-genai-systems/01-llm-lld-projects/embedding-service/         # fill existing stub
06-genai-systems/01-llm-lld-projects/tool-router/               # fill existing stub
06-genai-systems/01-llm-lld-projects/evaluation-harness/        # fill existing stub
06-genai-systems/02-llm-hld-projects/RUBRIC.md

# case-studies (4 new files)
case-studies/COMPARISON-TABLE.md
case-studies/INTERVIEW-GUIDE.md
case-studies/chatgpt-inference/README.md
case-studies/github-copilot/README.md

# resources (3 new files)
resources/study-plans/integrated-plan.md
resources/interview-tips/genai-checklist.md
resources/templates/genai-hld-template.md

# flashcards (3 new files)
flashcards/hld-concepts.md
flashcards/genai-systems.md
flashcards/case-studies.md

# quizzes (4 new files)
quizzes/hld-systems-quiz.md
quizzes/answers/hld-systems-answers.md
quizzes/genai-systems-quiz.md
quizzes/answers/genai-systems-answers.md
```

**Total new files: ~145** (62 LLD project-level + 40 HLD project-level + 43 section-level across all other areas)

---

## 4. Existing Docs to Update

These existing files must be updated to link to the new content map:

| File | Update Needed |
|------|---------------|
| `README.md` | Add links to new section-level artifacts; update GenAI status when concepts/LLDs are completed |
| `CONCEPTS.md` | Add GenAI design patterns, token/cost/latency, and vector DB entries to the concepts index |
| `QUICK-START.md` | Add GenAI learning path; reference integrated study plan |
| `NORTH-STAR.md` | Update audit counts when new content is delivered |
| `resources/CROSS-REFERENCE-GUIDE.md` | Add cross-reference patterns for GenAI track |
| `resources/CONSISTENCY-AUDIT.md` | Add GenAI section audit checklist |
| `resources/study-plans/1-week-plan.md` | Add GenAI day or optional GenAI extension |
| `resources/study-plans/1-month-plan.md` | Weave GenAI week into the 4-week plan |
| `resources/study-plans/genai-crash-track.md` | Update with new concepts (token planning, design patterns) |
| `resources/study-plans/genai-deep-dive.md` | Update with new concepts and framework doc |
| `06-genai-systems/README.md` | Update status table, add links to framework doc and new concepts |
| `06-genai-systems/AGENTS.md` | Add guidance for new concept and LLD directories |
| `flashcards/README.md` | Add entries for new decks |
| `quizzes/README.md` | Add entries for new quizzes |

---

## 5. Priority & Sequencing

### High Priority (do first — highest learner impact)

1. `06-genai-systems/GENAI-SD-FRAMEWORK.md` — The reusable "how to answer" guide
2. `04-hld-projects/<project>/RUBRIC.md` — Scoring rubrics for HLD projects
3. `04-hld-projects/<project>/PITFALLS.md` — Common mistakes for HLD projects
4. Complete remaining GenAI concepts (for example vector databases, model routing, and streaming/KV-cache)
5. `06-genai-systems/CLASSIC-VS-GENAI.md` — Bridges classic and GenAI prep

### Medium Priority (do second — completes the practice layer)

6. `02-lld-projects/<project>/RUBRIC.md` — Scoring rubrics for LLD projects
7. `02-lld-projects/<project>/PITFALLS.md` — Common mistakes for LLD projects
8. Complete remaining GenAI LLD components (for example embedding service, tool router, and evaluation harness)
9. New flashcard decks (hld-concepts, genai-systems)
10. New quizzes (hld-systems, genai-systems)

### Lower Priority (do third — polish and cross-cutting)

11. Comparison tables and follow-up variants for HLD and LLD projects
12. Case study additions (chatgpt-inference, github-copilot)
13. Theory additions (cap-theorem article, back-of-envelope article)
14. Pattern comparison tables and cross-references
15. Expand 05-coding-problems beyond the three live pattern packs (non-core per North Star)
16. Integrated study plan and resource updates

---

*This document is the output of Prompt 1 (Future Content Map). Review and
approve before proceeding to Prompt 2 (Portal Architecture) or Prompt 4
(Content Deepening).*

---

## 4. March 2026 Source Set 13-18 Execution Update

- Implemented mapped additions from system design source files 13-18 across HLD, LLD, solutions, and practice assets.
- Added four new classic HLD projects and six new LLD projects, with two existing HLD projects upgraded via explicit variants.
