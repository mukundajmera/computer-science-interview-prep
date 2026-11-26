# Lru Cache - Grading Rubric

Weighted rubric (100%) with scale descriptors.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Requirements Gathering & Scope (15%)

Evaluates how well the candidate handles requirements gathering & scope specifically for the lru-cache architecture.

- **Excellent (4/4)**: Flawless execution. Proactively fulfills these criteria:
  - Clarifies the data types for keys and values (generics).
  - Asks about capacity limits and behavior when full.
  - Inquires about concurrency requirements (single-threaded vs multi-threaded).
  - Determines if additional features like TTL or eviction callbacks are needed.
  - Demonstrates absolute mastery of advanced requirements gathering & scope patterns. Requires zero interviewer hints to identify edge cases.

- **Good (3/4)**: Solid understanding with minor gaps. Covers the main
requirements listed above but might miss nuances. Needs slight prompting to
optimize for scale. Overall design is highly workable.

- **Fair (2/4)**: Basic completion. Misses significant edge cases or relies
heavily on interviewer hints. The approach is naive or tightly coupled,
struggling with complex trade-offs.

- **Poor (1/4)**: Significant flaws. Fails to complete core requirements.
Fundamental misunderstanding of requirements gathering & scope concepts. Design
would fail catastrophically in production.

**Interviewer Focus**: Pay close attention to how they justify their decisions
in this section. The 'why' is more important than the 'what'. Did they consider
the specific operational realities of lru-cache?

## 2. API Design & System Interface (15%)

Evaluates how well the candidate handles api design & system interface specifically for the lru-cache architecture.

- **Excellent (4/4)**: Flawless execution. Proactively fulfills these criteria:
  - Defines a clean interface with generic types (e.g., `interface Cache<K, V>`).
  - Includes standard methods: `get`, `put`, `remove`, `clear`, `size`.
  - Uses appropriate return types (e.g., `Optional<V>` to handle nulls gracefully).
  - Designs for testability and dependency injection.
  - Demonstrates absolute mastery of advanced api design & system interface patterns. Requires zero interviewer hints to identify edge cases.

- **Good (3/4)**: Solid understanding with minor gaps. Covers the main
requirements listed above but might miss nuances. Needs slight prompting to
optimize for scale. Overall design is highly workable.

- **Fair (2/4)**: Basic completion. Misses significant edge cases or relies
heavily on interviewer hints. The approach is naive or tightly coupled,
struggling with complex trade-offs.

- **Poor (1/4)**: Significant flaws. Fails to complete core requirements.
Fundamental misunderstanding of api design & system interface concepts. Design
would fail catastrophically in production.

**Interviewer Focus**: Pay close attention to how they justify their decisions
in this section. The 'why' is more important than the 'what'. Did they consider
the specific operational realities of lru-cache?

## 3. Data Model & Storage (15%)

Evaluates how well the candidate handles data model & storage specifically for the lru-cache architecture.

- **Excellent (4/4)**: Flawless execution. Proactively fulfills these criteria:
  - Correctly identifies the need for a Hash Map + Doubly Linked List combination.
  - Designs the internal `Node` class correctly (key, value, prev, next).
  - Explains why a singly linked list is insufficient for O(1) deletion.
  - Manages memory overhead appropriately.
  - Demonstrates absolute mastery of advanced data model & storage patterns. Requires zero interviewer hints to identify edge cases.

- **Good (3/4)**: Solid understanding with minor gaps. Covers the main
requirements listed above but might miss nuances. Needs slight prompting to
optimize for scale. Overall design is highly workable.

- **Fair (2/4)**: Basic completion. Misses significant edge cases or relies
heavily on interviewer hints. The approach is naive or tightly coupled,
struggling with complex trade-offs.

- **Poor (1/4)**: Significant flaws. Fails to complete core requirements.
Fundamental misunderstanding of data model & storage concepts. Design would fail
catastrophically in production.

**Interviewer Focus**: Pay close attention to how they justify their decisions
in this section. The 'why' is more important than the 'what'. Did they consider
the specific operational realities of lru-cache?

## 4. High-Level Architecture (25%)

Evaluates how well the candidate handles high-level architecture specifically for the lru-cache architecture.

- **Excellent (4/4)**: Flawless execution. Proactively fulfills these criteria:
  - If discussing distributed caching, clearly explains Consistent Hashing.
  - Maps out the flow of a read-through or write-through cache.
  - Identifies single points of failure in a distributed setup.
  - Discusses client-side vs server-side caching strategies.
  - Demonstrates absolute mastery of advanced high-level architecture patterns. Requires zero interviewer hints to identify edge cases.

- **Good (3/4)**: Solid understanding with minor gaps. Covers the main
requirements listed above but might miss nuances. Needs slight prompting to
optimize for scale. Overall design is highly workable.

- **Fair (2/4)**: Basic completion. Misses significant edge cases or relies
heavily on interviewer hints. The approach is naive or tightly coupled,
struggling with complex trade-offs.

- **Poor (1/4)**: Significant flaws. Fails to complete core requirements.
Fundamental misunderstanding of high-level architecture concepts. Design would
fail catastrophically in production.

**Interviewer Focus**: Pay close attention to how they justify their decisions
in this section. The 'why' is more important than the 'what'. Did they consider
the specific operational realities of lru-cache?

## 5. Deep Dive & Component Design (20%)

Evaluates how well the candidate handles deep dive & component design specifically for the lru-cache architecture.

- **Excellent (4/4)**: Flawless execution. Proactively fulfills these criteria:
  - Writes bug-free, edge-case handling pointer manipulation code for the linked list.
  - Implements thread safety efficiently (e.g., ReadWriteLocks, Striped Locks).
  - Addresses the Cache Stampede problem with concrete solutions.
  - Explains exactly how to implement O(1) LFU if asked.
  - Demonstrates absolute mastery of advanced deep dive & component design patterns. Requires zero interviewer hints to identify edge cases.

- **Good (3/4)**: Solid understanding with minor gaps. Covers the main
requirements listed above but might miss nuances. Needs slight prompting to
optimize for scale. Overall design is highly workable.

- **Fair (2/4)**: Basic completion. Misses significant edge cases or relies
heavily on interviewer hints. The approach is naive or tightly coupled,
struggling with complex trade-offs.

- **Poor (1/4)**: Significant flaws. Fails to complete core requirements.
Fundamental misunderstanding of deep dive & component design concepts. Design
would fail catastrophically in production.

**Interviewer Focus**: Pay close attention to how they justify their decisions
in this section. The 'why' is more important than the 'what'. Did they consider
the specific operational realities of lru-cache?

## 6. Communication & Trade-offs (10%)

Evaluates how well the candidate handles communication & trade-offs specifically for the lru-cache architecture.

- **Excellent (4/4)**: Flawless execution. Proactively fulfills these criteria:
  - Clearly articulates the time vs space complexity trade-offs.
  - Explains why garbage collection impact matters for high-throughput caches.
  - Discusses the trade-offs of different eviction policies (LRU vs LFU vs FIFO).
  - Writes clean, readable, modular code on the whiteboard/editor.
  - Demonstrates absolute mastery of advanced communication & trade-offs patterns. Requires zero interviewer hints to identify edge cases.

- **Good (3/4)**: Solid understanding with minor gaps. Covers the main
requirements listed above but might miss nuances. Needs slight prompting to
optimize for scale. Overall design is highly workable.

- **Fair (2/4)**: Basic completion. Misses significant edge cases or relies
heavily on interviewer hints. The approach is naive or tightly coupled,
struggling with complex trade-offs.

- **Poor (1/4)**: Significant flaws. Fails to complete core requirements.
Fundamental misunderstanding of communication & trade-offs concepts. Design
would fail catastrophically in production.

**Interviewer Focus**: Pay close attention to how they justify their decisions
in this section. The 'why' is more important than the 'what'. Did they consider
the specific operational realities of lru-cache?

---

Total Weight: 100%

This rubric is designed to provide a standardized, objective framework for
evaluating candidates on the complex task of system design. However,
interviewers must apply context. A junior candidate might score highly by
following standard patterns well, while a staff candidate is expected to invent
novel solutions to edge-case bottlenecks.

Scoring note for Clarity of Thought: Look for this specific signal during evaluation.
Scoring note for Whiteboarding Skills: Look for this specific signal during evaluation.
Scoring note for Handling Ambiguity: Look for this specific signal during evaluation.
Scoring note for Receptiveness to Feedback: Look for this specific signal during evaluation.
Scoring note for Domain Knowledge: Look for this specific signal during evaluation.
Scoring note for System Intuition: Look for this specific signal during evaluation.
Scoring note for Pacing and Time Management: Look for this specific signal during evaluation.
Scoring note for Breadth of Experience: Look for this specific signal during evaluation.
Scoring note for Depth of Expertise: Look for this specific signal during evaluation.
Scoring note for Pragmatism vs Perfectionism: Look for this specific signal during evaluation.
Scoring note for Customer Empathy: Look for this specific signal during evaluation.
Scoring note for Business Acumen: Look for this specific signal during evaluation.
Scoring note for Security Awareness: Look for this specific signal during evaluation.
Scoring note for Operational Readiness: Look for this specific signal during evaluation.
Scoring note for Mentorship Potential: Look for this specific signal during evaluation.
Scoring note for Technical Leadership: Look for this specific signal during evaluation.
Scoring note for Decision Making Framework: Look for this specific signal during evaluation.
Scoring note for Risk Assessment: Look for this specific signal during evaluation.
Scoring note for Conflict Resolution (Technical): Look for this specific signal during evaluation.
Scoring note for Self-Correction: Look for this specific signal during evaluation.

Red Flag Warning: Candidate fails to address Scalability limits effectively.
Red Flag Warning: Candidate fails to address Single points of failure effectively.
Red Flag Warning: Candidate fails to address Data consistency guarantees effectively.
Red Flag Warning: Candidate fails to address Security vulnerabilities effectively.
Red Flag Warning: Candidate fails to address Network latency effectively.
Red Flag Warning: Candidate fails to address Storage costs effectively.
Red Flag Warning: Candidate fails to address Algorithmic complexity effectively.
Red Flag Warning: Candidate fails to address Database bottlenecks effectively.
Red Flag Warning: Candidate fails to address Message loss effectively.
Red Flag Warning: Candidate fails to address Cache stampedes effectively.
Red Flag Warning: Candidate fails to address Race conditions effectively.
Red Flag Warning: Candidate fails to address Schema evolution effectively.
Red Flag Warning: Candidate fails to address Code Maintainability effectively.
Red Flag Warning: Candidate fails to address Extensibility effectively.
Red Flag Warning: Candidate fails to address Deployment Strategies effectively.
Red Flag Warning: Candidate fails to address Observability Practices effectively.
