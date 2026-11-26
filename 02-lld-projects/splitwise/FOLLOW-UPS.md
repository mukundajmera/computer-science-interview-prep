# Splitwise - Follow-Up Questions

## Follow-up questions
1. How would you represent money to avoid rounding drift across equal splits?
2. Should balances be stored, derived on demand, or cached with invalidation?
3. How would settlement records affect future balance calculations?
4. What changes when expenses are added concurrently to the same group?
5. How would you explain the difference between greedy simplification and optimal minimization?

## Variants and extensions
1. Recurring expenses with scheduled split creation.
2. Expense categories, attachments, and audit export.
3. Multi-currency expenses with conversion and settlement currency choices.
4. Group notifications when expenses or settlements are added.

## Interviewer probes to prepare
- "What invariant keeps balances reconcilable?"
- "How do you handle the leftover cent in equal splits?"
- "Is `Balance` source data or derived data?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
