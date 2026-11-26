# ATM System — Interview Scoring Rubric

Use this rubric to score solution quality consistently across design depth, correctness, and communication.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Interview Timeline (45 Minutes)

- **00:00 - 05:00**: Requirements gathering and scope alignment. Clarifying hardware vs software boundaries.
- **05:00 - 10:00**: Core domain modeling (identifying entities, states) and API definition.
- **10:00 - 30:00**: Detailed LLD implementation. Applying State and Chain of Responsibility patterns.
- **30:00 - 40:00**: Addressing concurrency, transactions, and hardware failure modes.
- **40:00 - 45:00**: Follow-up questions, scalability discussions, and Q&A.

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Distinguishes hardware interfaces, bank APIs, and ATM state. Validates constraints. |
| Domain modeling | 20% | Clean separation: ATM Controller, States, Hardware Interfaces, Bank Service. |
| Behavioral correctness | 25% | Valid state transitions, robust transaction rollback, PIN limits handled. |
| Extensibility and variants | 20% | Easy to add new states, configurable denominations, clear abstractions. |
| Code and communication quality | 15% | Clear APIs, articulate narrative, handles failure scenarios well. |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: Starts coding immediately without scoping or clarifying requirements.
- **3**: Captures basic features but misses hardware abstraction or network realities.
- **5**: Explicitly separates physical ATM logic from the central bank backend.

### 2. Domain modeling
- **1**: Produces a "God object" ATM class handling everything.
- **3**: Core entities exist, but boundaries between hardware and logic are fuzzy.
- **5**: Strong SRP. Uses interfaces for CardReader, CashDispenser, Screen.

### 3. Behavioral correctness
- **1**: Flawed logic, allows withdrawal without authentication, ignores rollbacks.
- **3**: Mostly correct happy path, but leaves edge cases (e.g., partial dispense) unhandled.
- **5**: Handles state transitions flawlessly, robust transaction safety.

### 4. Extensibility and variants
- **1**: Hard-coded denominations; if-else state machine.
- **3**: Mentions patterns conceptually but fails to code them.
- **5**: Uses State pattern for lifecycle and Chain of Responsibility for dispensing.

### 5. Code and communication quality
- **1**: Confusing narrative, poor variable naming, unable to explain choices.
- **3**: Understandable design with moderate justification.
- **5**: Crisp explanation, focused APIs, clean and readable code.

---

## Hard Gates (Failing Any Gate Caps Score)

1. No clear abstraction for hardware components.
2. Missing or flawed state machine implementation.
3. Completely ignores transactional safety for cash dispensing.
4. Fails to handle basic security (e.g., plaintext PINs).
