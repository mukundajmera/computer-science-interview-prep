# Rubric: Online Code Judge

Evaluates behavior and defensible trade-offs.

| Level | Criteria | Example Case |
|---|---|---|
| **L4 (Good)** | Intuitive minimum example. Working synchronous code judge with hardcoded languages. | Implements `v1-basic` correctly. fast-fails test cases on first WA/RE/CE. |
| **L5 (Strong)** | Clean Strategy Pattern & Trade-offs. Asynchronous queue used with proper producer-consumer setup and graceful shutdown. | Implements `v2-extended` and `v3-optimized`. Explains in-memory hash map vs distributed DB trade-offs. |
| **L6/L7 (Staff)** | Optional failure trace with assumptions. Handles concurrent state corruption. Distinguishes simulations/proof sketches from deployed systems/formal verification. | Identifies deadlocks, handles worker thread exceptions, clearly bounds VM/container isolation outside of standard library limits. |
