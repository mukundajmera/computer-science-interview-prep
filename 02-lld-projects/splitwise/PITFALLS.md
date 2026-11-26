# Splitwise - Common Pitfalls

## Common pitfalls
1. Skipping validation that exact splits sum to the expense and percentage splits sum to 100%.
2. Using floating-point money math without a rounding policy for equal splits.
3. Updating cached balances without preserving the underlying expense and settlement history.
4. Creating self-loops or duplicate opposite-direction balances between the same users.
5. Treating debt simplification as exact optimal minimization without explaining the greedy tradeoff.

## Why these fail interviews
- They produce balances users cannot reconcile from the expense ledger.
- They make rounding drift accumulate across groups and settlements.
- They hide whether balance is source-of-truth data or derived from audit history.

## Mitigations
- Validate every split type before accepting an expense.
- Use decimal money semantics and assign rounding remainders deterministically.
- Treat expenses and settlements as the audit trail; derive or carefully invalidate cached balances.
- Normalize pairwise balances so each user pair has one direction and no self debt.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Design patterns](../../01-design-patterns/README.md)
