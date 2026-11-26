# Splitwise - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies users, groups, split types, settlements, currency, rounding, and audit scope |
| Split validation | 25% | Validates equal, exact, and percentage splits against total amount and participant rules |
| Balance correctness | 25% | Maintains accurate owed/owed-by views without self loops, sign errors, or stale derived data |
| Settlement design | 20% | Explains derived balances, transaction history, and greedy debt simplification tradeoffs |
| Extensibility and communication | 15% | Evolves from equal splits to groups, settlements, notifications, and v3 concurrency cleanly |

## Performance bands
- `1/5`: stores pairwise debts ad hoc and skips split validation.
- `3/5`: supports core split types and balance display with partial rounding and settlement handling.
- `5/5`: invariant-driven expense ledger with validated splits, accurate derived balances, settlement audit, and clear simplification limits.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Payment System rubric](../payment-system/RUBRIC.md)
