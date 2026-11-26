# Conversation Memory Store — Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Conversation Memory Store project.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md)

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|-----------|--------|--------------------------|
| Requirements and constraints clarity | 20% | Recognizes need for multiple memory strategies, token constraints, and deterministic testability without external LLMs. |
| Domain modeling | 20% | Clean separation of Message, Conversation, MemoryStrategy, and Summarizer interfaces. |
| Behavioral correctness | 25% | Strategies handle their logic correctly (e.g., token limit truncation, summary state, sliding window limits). |
| Extensibility and variants | 20% | Uses Strategy Pattern for memory types and Dependency Injection for the Summarizer. |
| Code and communication quality | 15% | Clear APIs, test-friendly design (deterministic stubs), and well-articulated trade-offs (e.g., heuristic token count). |

---

## 1 to 5 Guidance

### 1. Requirements and constraints clarity
- **1**: Starts coding without identifying different memory retention strategies.
- **3**: Mentions multiple strategies and token limits, but misses summarization decoupling.
- **5**: Explicitly states memory constraints, decoupling summarization (no hard dependency on LLM), and multi-conversation management.

### 2. Domain modeling
- **1**: Single god-class handling all conversation logic, storage, and summarization.
- **3**: Core entities (Message, Conversation) exist, but memory logic is tightly coupled or uses a mode-flag enum instead of polymorphism.
- **5**: Strong OOP/SOLID design. Uses Strategy Pattern for `MemoryStrategy` and delegates to a pluggable `Summarizer`.

### 3. Behavioral correctness
- **1**: Fails to limit context sizes correctly or loses messages completely.
- **3**: Most strategies work, but edge cases like TokenLimitedMemory exceeding budget on the most recent message or SummaryMemory losing early context are mishandled.
- **5**: All four memory strategies behave correctly according to rules. Token math is robust, and summaries appropriately roll up older context.

### 4. Extensibility and variants
- **1**: Hard-coded summarization logic or rigid memory configurations.
- **3**: Discusses adding new strategies but structure requires modifying existing code.
- **5**: Open/Closed Principle followed. New memory types and real async LLM summarizers can be added with zero changes to existing classes.

### 5. Code and communication quality
- **1**: Confusing APIs, long methods, no clear explanation of context retrieval.
- **3**: Understandable design, moderate justification for token estimation heuristics.
- **5**: Crisp explanation, focused APIs, and a deterministic testing narrative for a traditionally non-deterministic AI component.

---

## Hard Gates (Failing Any Gate Caps Score)

1. No clear abstraction for `MemoryStrategy` (e.g., using massive `if/else` or `switch` statements for modes).
2. Tightly coupling summarization logic to a specific LLM API without an interface/stub.
3. Not adhering to token/message budgets in `WindowMemory`, `SummaryMemory`, or `TokenLimitedMemory`.
4. No isolation between different conversations (global state leakage).

---

## Follow-Up Scoring Boosters

1. Explains how to handle asynchronous summarization in a real LLM environment.
2. Mentions thread-safety requirements for concurrent chat sessions.
3. Proposes an approach for conversation forking (copy-on-write vs. deep copy).
4. Highlights the inaccuracy of word-count heuristic and proposes real tokenization integration.
5. Considers a persistence layer adapter (e.g., saving to Redis/PostgreSQL).

---

## Cross-Links

- Pattern recap: [01-design-patterns](../../../01-design-patterns/README.md)
- Theory recap: [00-theory](../../../00-theory/README.md)
