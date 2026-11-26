# ⚠️ Common Pitfalls

Mistakes to avoid in system design interviews and how to prevent them.

---

## 📋 Overview

| Category | Top Pitfalls |
|----------|--------------|
| **LLD Pitfalls** | Jumping to code, ignoring SOLID, over-engineering |
| **HLD Pitfalls** | Skipping requirements, ignoring scale, no trade-offs |
| **Communication** | Not thinking aloud, ignoring feedback |
| **General** | Poor time management, giving up too easily |

---

## 🏗️ LLD Interview Pitfalls

### Pitfall 1: Jumping to Code Without Design

**What It Looks Like:**
- Immediately start writing class definitions
- No entity identification or relationship mapping
- Skip design patterns discussion

**Why It's Bad:**
- Shows lack of systematic thinking
- Leads to messy, unorganized code
- Miss important design decisions
- Hard to refactor mid-interview

**How to Avoid:**
```
✅ Spend first 15-20 minutes on:
   1. Requirements clarification
   2. Entity identification
   3. Relationship mapping
   4. Pattern selection

✅ Only then start writing classes
```

**What to Say:**
> "Before I start coding, let me identify the core entities and their relationships..."

---

### Pitfall 2: Ignoring SOLID Principles

**What It Looks Like:**
- Giant classes with multiple responsibilities
- God objects that do everything
- Tight coupling between classes
- No interfaces or abstractions

**Why It's Bad:**
- Shows lack of software engineering fundamentals
- Results in unmaintainable code
- Missed opportunity to discuss patterns

**How to Avoid:**

| Principle | Checklist |
|-----------|-----------|
| **S - Single Responsibility** | Does each class have ONE reason to change? |
| **O - Open/Closed** | Can I extend without modifying existing code? |
| **L - Liskov Substitution** | Can subtypes replace base types? |
| **I - Interface Segregation** | Are my interfaces focused and small? |
| **D - Dependency Inversion** | Do I depend on abstractions, not concretions? |

**Bad Example:**
```java
// God class - violates SRP
class ParkingLot {
    void parkVehicle() { }
    void calculateFee() { }
    void processPayment() { }
    void printReceipt() { }
    void sendNotification() { }
    // Everything in one class!
}
```

**Good Example:**
```java
// Separate responsibilities
class ParkingLot { void parkVehicle() { } }
class FeeCalculator { double calculate() { } }
class PaymentProcessor { void process() { } }
class ReceiptPrinter { void print() { } }
class NotificationService { void notify() { } }
```

---

### Pitfall 3: Over-Engineering Simple Problems

**What It Looks Like:**
- Using 5 patterns when 1 would suffice
- Unnecessary abstraction layers
- Complex solutions for simple requirements
- Designing for imaginary future needs

**Why It's Bad:**
- Wastes interview time
- Makes design harder to explain
- Shows poor judgment about complexity
- Interviewers may think you don't know simpler solutions

**How to Avoid:**
- Start with the simplest solution that works
- Only add complexity when required by requirements
- Ask: "Does this pattern actually help here?"

**What to Say:**
> "I could use [complex pattern] here, but given our requirements, a simpler approach would be..."

---

### Pitfall 4: Not Discussing Trade-offs

**What It Looks Like:**
- Present only one approach
- No comparison of alternatives
- No explanation of why you chose something

**Why It's Bad:**
- Missed opportunity to show depth
- May seem like you don't know alternatives
- Can't justify your design choices

**How to Avoid:**
> "I'm choosing [A] over [B] because [reason]. The trade-off is [trade-off], but given our requirement for [X], this makes more sense."

---

### Pitfall 5: Forgetting Edge Cases

**What It Looks Like:**
- No null checks
- No validation
- No error handling
- Assuming happy path always

**Why It's Bad:**
- Shows lack of production experience
- Results in brittle code
- Common interviewer follow-up: "What if X is null?"

**How to Avoid:**

| Edge Case | Check For |
|-----------|-----------|
| Null inputs | What if parameter is null? |
| Empty collections | What if list is empty? |
| Boundaries | Full capacity? Zero items? |
| Concurrency | Two threads accessing same resource? |
| Invalid states | Operation called in wrong state? |

---

### Pitfall 6: Ignoring Concurrency

**What It Looks Like:**
- No synchronization for shared resources
- Race conditions in booking/reservation
- No consideration of thread safety

**Why It's Bad:**
- Critical for real-world systems
- Common interview follow-up
- Shows lack of awareness about production issues

**How to Avoid:**
> "Since multiple users might try to book the same seat, I'll use [locks/synchronized/atomic operations] to prevent race conditions."

### Pitfall 7: Poor Delivery Sequencing in LLD

**What It Looks Like:**
- Spending too long on requirement minutiae and never finishing class APIs
- Writing full implementations before establishing method contracts
- Ending without extension strategy or recap

**Why It's Bad:**
- Interview rounds are time-boxed; sequencing quality is part of evaluation
- Strong designs can still score low if narrative and pacing are weak

**How to Avoid:**
1. Time-box 5/5/5/15/10/5 for requirements, entities, relationships, class design, edge cases, wrap-up.
2. Prioritize API contracts and invariants before implementation detail.
3. End with one-minute recap: what is solved, what is deferred, what extends cleanly.

**What to Say:**
> "I'll finish core contracts first, then implement one critical path, and reserve final minutes for edge cases and extensibility."

---

## ☁️ HLD Interview Pitfalls

### Pitfall 1: Not Asking Clarifying Questions

**What It Looks Like:**
- Start designing immediately
- Make assumptions without confirming
- Design wrong system

**Why It's Bad:**
- Waste time on wrong requirements
- Miss important constraints
- Show poor requirement gathering skills

**How to Avoid:**
```
Always ask about:
1. Core features (what to include/exclude)
2. Scale (users, QPS, data size)
3. Latency requirements
4. Consistency vs availability preference
5. Geographic distribution
```

**What to Say:**
> "Before I start, I'd like to clarify a few things to make sure I'm designing the right system..."

---

### Pitfall 2: Skipping Estimations

**What It Looks Like:**
- No QPS calculations
- No storage estimates
- No bandwidth calculations
- Vague statements like "a lot of data"

**Why It's Bad:**
- Can't justify infrastructure choices
- May design for wrong scale
- Miss key interview criteria

**How to Avoid:**
```
Always calculate:
- Read QPS = DAU × reads per user / 86,400
- Write QPS = DAU × writes per user / 86,400
- Storage = size × count × retention period
- Bandwidth = QPS × average size
```

**What to Say:**
> "Let me do some quick estimates. With 100M DAU and 10 requests per user per day, we're looking at about 11.5K QPS..."

---

### Pitfall 3: Single Points of Failure

**What It Looks Like:**
- One database with no replicas
- No load balancer
- Single server for critical path
- No backup or failover plan

**Why It's Bad:**
- System will go down
- Shows lack of production thinking
- Unacceptable for any real system

**How to Avoid:**

| Component | Redundancy Strategy |
|-----------|---------------------|
| Application servers | Multiple behind load balancer |
| Database | Primary + replicas, failover |
| Cache | Cluster with replication |
| Load balancer | Multiple (active-passive) |

---

### Pitfall 4: Not Discussing Trade-offs

**What It Looks Like:**
- Present design as the only option
- No comparison of alternatives
- No justification for choices

**Why It's Bad:**
- Trade-off discussion is crucial evaluation criteria
- Shows depth of understanding
- Real systems require trade-off decisions

**How to Avoid:**
> "For the database, I'm choosing PostgreSQL over MongoDB because we need ACID transactions. The trade-off is horizontal scaling is harder, but we can use read replicas and sharding later."

---

### Pitfall 5: Ignoring CAP Theorem

**What It Looks Like:**
- Claim system is consistent AND available
- No discussion of partition handling
- Unrealistic guarantees

**Why It's Bad:**
- Shows lack of distributed systems understanding
- Fundamental concept for system design
- Real systems must make CAP choices

**How to Avoid:**
> "During a network partition, this system will favor availability over consistency. Users might see slightly stale data, but the system remains responsive. For financial transactions, we'd need the opposite."

---

### Pitfall 6: Over-focusing on One Area

**What It Looks Like:**
- Spend 30 minutes on database design
- Rush through or skip other components
- Imbalanced coverage

**Why It's Bad:**
- Miss important parts of the system
- Looks like you only know one area
- Poor time management

**How to Avoid:**
- Allocate time for each phase
- Get feedback on priorities
- Cover all major components first, then deep dive

---

### Pitfall 7: Not Handling Failures

**What It Looks Like:**
- Assume everything works
- No retry logic
- No dead letter queues
- No monitoring discussion

**Why It's Bad:**
- Shows lack of production experience
- Real systems fail constantly
- Reliability is key evaluation criteria

**How to Avoid:**
> "What happens if the message queue is down? We'll need retry logic with exponential backoff and a dead letter queue for messages that repeatedly fail."

---

## 🗣️ Communication Pitfalls

### Pitfall 1: Not Thinking Out Loud

**What It Looks Like:**
- Long silences while thinking
- Jump from question to answer without explanation
- Interviewer can't follow your thought process

**Why It's Bad:**
- Interviewer can't give partial credit
- No opportunity for hints or guidance
- Feels awkward for everyone

**How to Avoid:**
- Verbalize your thought process
- Explain trade-offs as you consider them
- Say "I'm thinking about..." when processing

---

### Pitfall 2: Ignoring Interviewer Feedback

**What It Looks Like:**
- Continue with original plan after hint
- Dismiss concerns without addressing
- Defensive responses

**Why It's Bad:**
- Shows poor collaboration
- Missed opportunity to improve design
- Appears arrogant or inflexible

**How to Avoid:**
> "That's a great point. Let me adjust my design to address that..."

---

### Pitfall 3: Giving Up Too Easily

**What It Looks Like:**
- Say "I don't know" and stop
- Wait for interviewer to give answer
- Shut down when challenged

**Why It's Bad:**
- No opportunity to show problem-solving
- Interviewers want to see you work through problems
- Shows lack of persistence

**How to Avoid:**
> "I'm not certain about this specific implementation, but let me think through it from first principles... [work through the problem]"

---

## ⏱️ General Pitfalls

### Pitfall 1: Poor Time Management

**What It Looks Like:**
- 25 minutes on requirements
- Rush through actual design
- Never get to trade-offs

**How to Avoid:**
- Allocate time per phase
- Watch the clock
- Ask interviewer about priorities

### Pitfall 2: Not Drawing Diagrams

**What It Looks Like:**
- Verbal-only explanation
- No visual architecture
- Hard to follow data flow

**How to Avoid:**
- Always draw the architecture
- Draw as you explain
- Use diagrams for both LLD and HLD

### Pitfall 3: Using Buzzwords Without Understanding

**What It Looks Like:**
- "We'll use Kubernetes for microservices"
- "Just add Redis for caching"
- Can't explain how/why

**How to Avoid:**
- Only mention technologies you can explain
- Be ready for "why?" and "how?" follow-ups
- Understand trade-offs of technologies you suggest

---

## 🧠 Behavioral Interview Pitfalls

### Pitfall 1: Missing the Underlying Signal

**What It Looks Like:**
- Polished answer that does not match what the prompt is evaluating
- Conflict prompt answered like a project summary
- Leadership prompt answered with only implementation detail

**Why It's Bad:**
- Interviewers score signal alignment first
- Strong stories can still underperform if mismatched

**How to Avoid:**
- Explicitly tag the primary and secondary signal before answering
- Choose story first, then shape answer to signal

### Pitfall 2: Context Overload, Action Deficit

**What It Looks Like:**
- Long setup with little decision detail
- \"What happened\" dominates \"what you decided and drove\"

**Why It's Bad:**
- Reduces action density and ownership signal
- Leaves limited time for follow-up depth

**How to Avoid:**
- Cap context to 20-30% of response time
- Move quickly to decisions, trade-offs, and outcomes

### Pitfall 3: The \"We\" Disease

**What It Looks Like:**
- Heavy team language with unclear personal contribution
- Interviewer cannot infer your ownership boundary

**Why It's Bad:**
- Weakens level calibration
- Raises credibility risk in follow-ups

**How to Avoid:**
- Use both team context and explicit individual actions
- State: what you owned, what was shared, what changed because of you

### Pitfall 4: Story-Scale Mismatch

**What It Looks Like:**
- Senior/staff candidate using low-scope tactical stories
- Manager candidate missing people/operating mechanisms

**Why It's Bad:**
- Signals a level mismatch even if execution quality is good

**How to Avoid:**
- Select stories with scope calibrated to target role
- Include cross-team and second-order impact for higher levels

### Pitfall 5: Fairy-Tale Endings

**What It Looks Like:**
- Story has no trade-offs, setbacks, or imperfect decisions
- Reflection is generic or absent

**Why It's Bad:**
- Sounds rehearsed and low-credibility
- Hides judgment under constraints

**How to Avoid:**
- Include one real tension point and how you resolved it
- Close with concrete learning and changed behavior

### Pitfall 6: Weak Follow-Up Resilience

**What It Looks Like:**
- Story changes under probing
- Answers become defensive or contradictory

**Why It's Bad:**
- Follow-ups are where interviewers test depth and integrity

**How to Avoid:**
- Pre-drill likely probes: ownership, alternatives, metrics, reflection
- Keep one factual backbone and adapt emphasis, not facts

### Pitfall 7: Not Practicing Under Pressure

**What It Looks Like:**
- Story sounds good in notes but collapses in timed conversation
- Candidate loses structure when interrupted

**Why It's Bad:**
- Behavioral rounds are real-time communication evaluations

**How to Avoid:**
- Use progressive drills: solo -> AI -> peer -> high-signal mock
- Score each run and re-drill weak signals within 48 hours

Behavioral deep dive:
- [behavioral-pitfalls.md](behavioral-pitfalls.md)
- [behavioral-practice-roadmap.md](behavioral-practice-roadmap.md)
- [behavioral-special-interview-types.md](behavioral-special-interview-types.md)

---

## 🤖 AI-Enabled Coding Interview Pitfalls

### Pitfall 1: Planless Prompting

**What It Looks Like:**
- Paste full prompt into AI before clarifying constraints
- Let generated code define architecture direction
- Discover requirements only after implementation starts

**Why It's Bad:**
- Signals weak problem decomposition
- Increases rework and correctness risk
- Makes trade-off explanations shallow

**How to Avoid:**
1. Clarify requirements first.
2. State a phased plan.
3. Prompt phase-by-phase instead of all-at-once.

### Pitfall 2: Passive AI Acceptance

**What It Looks Like:**
- Accept code without checking invariant or style alignment
- Keep architecture suggestions solely because they "look complete"

**Why It's Bad:**
- Interviewers evaluate your decisions, not model output
- Hidden defects spread quickly across files

**How to Avoid:**
> "I'll review this output against our constraints and existing interfaces before accepting it."

### Pitfall 3: Unverified Edits

**What It Looks Like:**
- Proceed without running tests
- No walkthrough of changed code paths
- Skip edge-case checks after refactors

**Why It's Bad:**
- Breaks confidence in correctness claims
- Misses easy regressions that are visible in round time

**How to Avoid:**
- Require a verify checkpoint after each major AI-generated change.
- Validate with existing tests, targeted tests, and quick manual path checks.

### Pitfall 4: Silent Execution

**What It Looks Like:**
- Long stretches of no narration while prompting
- Interviewer cannot infer your intent or confidence

**Why It's Bad:**
- Removes partial-credit opportunities
- Appears like the AI is driving and candidate is observing

**How to Avoid:**
- Narrate intent before each prompt and summarize outcomes after each result.
- Keep an explicit "next two steps" statement visible throughout the round.

---

## ✅ Pre-Interview Checklist

### Avoid These By Preparation:

- [ ] **Know the framework** - LLD steps, HLD phases
- [ ] **Practice estimation** - Be quick with math
- [ ] **Memorize patterns** - When to use each
- [ ] **Prepare phrases** - Smooth transitions, handling feedback
- [ ] **Time your practice** - Stay within limits

### During the Interview:

- [ ] **Start with questions** - Clarify before designing
- [ ] **Think out loud** - Share your reasoning
- [ ] **Watch the time** - Balance coverage
- [ ] **Draw diagrams** - Visual communication
- [ ] **Discuss trade-offs** - Show depth
- [ ] **Handle failures** - Consider what can go wrong

---

## 📊 Pitfall Quick Reference

| Pitfall | Category | Quick Fix |
|---------|----------|-----------|
| Jump to code | LLD | Spend 15 min on design first |
| Ignore SOLID | LLD | Check each principle |
| Over-engineer | LLD | Start simple |
| No questions | HLD | Ask 3-5 clarifying questions |
| Skip estimation | HLD | Always calculate QPS/storage |
| Single point of failure | HLD | Add redundancy everywhere |
| No trade-offs | Both | Compare at least 2 options |
| Silent thinking | Communication | Verbalize thought process |
| Ignore feedback | Communication | Acknowledge and adapt |
| Poor time management | General | Allocate time per phase |

---

## 🔗 Related Resources

- [lld-checklist.md](lld-checklist.md) - Avoid LLD pitfalls
- [hld-checklist.md](hld-checklist.md) - Avoid HLD pitfalls
- [communication-guide.md](communication-guide.md) - Communicate effectively
- [behavioral-pitfalls.md](behavioral-pitfalls.md) - Behavioral-specific pitfalls and recovery patterns
- [behavioral-big-three.md](behavioral-big-three.md) - High-frequency behavioral prompt playbook

---

*Knowing what NOT to do is just as important as knowing what TO do! ⚠️*
