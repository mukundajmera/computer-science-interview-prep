# 🧭 LLD Interview Framework Quiz

> **25 questions to test delivery quality in low-level design interviews**
>
> ⏱️ Time: 30 minutes | ⭐⭐⭐ Difficulty

---

## Section 1: Requirements and Constraints (5 questions)

### Question 1 ⭐⭐
What is the best first move in an LLD interview?

**A)** Start coding entities immediately  
**B)** Clarify requirements, constraints, and scope boundaries  
**C)** Draw a full UML upfront  
**D)** Explain design patterns before domain model

---

### Question 2 ⭐⭐
Which assumption should be made explicit early?

**A)** Programming language preference  
**B)** Concurrency expectations  
**C)** Naming style  
**D)** IDE shortcuts

---

### Question 3 ⭐⭐⭐
What is the strongest scope statement?

**A)** "I'll try to cover everything."  
**B)** "I'll design core flows and skip all edge cases."  
**C)** "I'll finish core v1 flows, then handle edge cases and extensions if time permits."  
**D)** "I'll focus only on class names."

---

### Question 4 ⭐⭐⭐
Which is an example of an out-of-scope declaration?

**A)** "I'll optimize for O(1) everywhere."  
**B)** "I will not cover analytics dashboards in v1."  
**C)** "I will use Java for faster coding."  
**D)** "I will avoid exceptions."

---

### Question 5 ⭐⭐⭐
If requirements are ambiguous, what should you do?

**A)** Wait silently for interviewer detail  
**B)** Assume the most complex scenario  
**C)** Present two assumptions, pick one default, and proceed  
**D)** Refuse to continue until exact requirements are provided

---

## Section 2: Modeling and Design Quality (8 questions)

### Question 6 ⭐⭐
What is the best way to identify core entities?

**A)** Start from design patterns  
**B)** Extract nouns, then validate responsibilities  
**C)** Copy a known system design  
**D)** Use inheritance for all entities

---

### Question 7 ⭐⭐
Which relationship implies strongest ownership?

**A)** Dependency  
**B)** Association  
**C)** Aggregation  
**D)** Composition

---

### Question 8 ⭐⭐⭐
What indicates over-modeling?

**A)** Clear invariants  
**B)** Too many classes with unclear responsibilities  
**C)** Private fields and public methods  
**D)** Focused interfaces

---

### Question 9 ⭐⭐⭐
When is Strategy pattern most justified?

**A)** Behavior varies by algorithm/policy at runtime  
**B)** Need exactly one instance  
**C)** Need to simplify subsystem API  
**D)** Need to notify subscribers

---

### Question 10 ⭐⭐⭐
What is the most common Singleton misuse?

**A)** Using static factory methods  
**B)** Centralized logging  
**C)** Hiding dependencies that should be injected  
**D)** One app-wide configuration object

---

### Question 11 ⭐⭐⭐
What is the strongest class API signal?

**A)** Many public mutable fields  
**B)** Explicit method contracts and invariants  
**C)** Deep inheritance hierarchy  
**D)** No exceptions raised

---

### Question 12 ⭐⭐⭐
If two operations can race on shared state, the first design action is:

**A)** Add more patterns  
**B)** Define lock/atomic ownership boundary  
**C)** Remove validation  
**D)** Use global variables

---

### Question 13 ⭐⭐⭐
Which is the best extension-ready design move?

**A)** Giant switch statement in one class  
**B)** Separate policy interface for change-prone behavior  
**C)** Duplicate code everywhere for speed  
**D)** Avoid abstractions entirely

---

## Section 3: Pitfalls, Follow-ups, Communication (7 questions)

### Question 14 ⭐⭐
Which pitfall hurts interview score the most?

**A)** Minor naming inconsistency  
**B)** Coding before requirement clarification  
**C)** Using enums  
**D)** Writing helper methods

---

### Question 15 ⭐⭐⭐
Best way to explain a pattern choice:

**A)** "I always use this pattern."  
**B)** "It is popular in interviews."  
**C)** "This requirement changes often, so this pattern localizes modifications."  
**D)** "It reduces lines of code."

---

### Question 16 ⭐⭐⭐
A strong recap at the end should include:

**A)** Only class names  
**B)** Requirements met, trade-offs, and extension path  
**C)** Implementation details only  
**D)** Language-specific optimizations only

---

### Question 17 ⭐⭐⭐
If interviewer asks "what breaks first at 10x?" you should:

**A)** Say "nothing breaks"  
**B)** Identify likely bottleneck and propose targeted mitigation  
**C)** Redraw the entire system from scratch  
**D)** Avoid answering without benchmarks

---

### Question 18 ⭐⭐⭐
What is the best response to follow-up scope increase mid-round?

**A)** Ignore it to finish original design  
**B)** Restart everything  
**C)** State impact, adapt model at extension points, continue  
**D)** Add unrelated patterns

---

### Question 19 ⭐⭐⭐
Which communication behavior is strongest?

**A)** Silent coding  
**B)** Long theoretical monologue  
**C)** Structured think-aloud tied to requirements  
**D)** Constantly changing direction without summary

---

### Question 20 ⭐⭐⭐
When should you discuss alternatives?

**A)** Never; one approach only  
**B)** Only if asked at the end  
**C)** At key decisions with concise trade-offs  
**D)** Before requirements are clear

---

## Section 4: Scenario-Based Judgment (5 questions)

### Question 21 ⭐⭐⭐
Parking lot pricing is changing monthly by tenant. Best design move?

**A)** Hardcode tenant rules in ParkingLot class  
**B)** Introduce ParkingPricingPolicy abstraction  
**C)** Duplicate ParkingLot per tenant  
**D)** Remove pricing from domain

---

### Question 22 ⭐⭐⭐
Tic-tac-toe now supports multiple win rules. Best extension point?

**A)** Replace all code with inheritance tree  
**B)** Add WinResolutionPolicy strategy  
**C)** Inline conditionals in UI layer  
**D)** Ignore variant support

---

### Question 23 ⭐⭐⭐
Vending machine payment pipeline needs fraud checks. Best path?

**A)** Add checks inside every state class separately  
**B)** Add PaymentCommand/Workflow policy layer  
**C)** Disable cancel flow  
**D)** Skip inventory checks

---

### Question 24 ⭐⭐⭐
Which answer best demonstrates YAGNI with extensibility?

**A)** "I implemented all future features now."  
**B)** "I left extension interfaces but implemented only current requirements."  
**C)** "I avoided all abstractions."  
**D)** "I optimized distributed scaling first."

---

### Question 25 ⭐⭐⭐
Which response best demonstrates senior interview judgment?

**A)** "My design is perfect."  
**B)** "I used many patterns so it is correct."  
**C)** "Here are solved requirements, known trade-offs, and the first safe scaling step."  
**D)** "I need more time to pick a language."

---

## Answer Sheet

Write your answers as:

`1:B, 2:B, 3:C ... 25:C`

Then check with: [LLD Interview Framework Answer Key](./answers/lld-interview-framework-answers.md)
