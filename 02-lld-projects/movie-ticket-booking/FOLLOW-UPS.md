# Movie Ticket Booking - Follow-Up Questions

## Follow-up questions
1. How would you run lock-expiry cleanup without blocking booking hot paths?
2. How would you handle partial payment success and rollback semantics?
3. How would you expose real-time seat-map updates to clients?
4. How would you introduce waitlists with fairness and anti-starvation guarantees?
5. How would you partition shows across nodes while preserving seat correctness?

## Variants and extensions
1. Group booking with adjacency constraints.
2. Dynamic pricing policies by demand and timing.
3. Promo-code and refund policies as pluggable strategies.
4. Multi-currency payment abstraction with idempotent confirmation.

## Interviewer probes to prepare
- "What is the exact atomic boundary in your design?"
- "How do you prove no double booking under concurrent confirms?"
- "What breaks first at 10x show traffic?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
