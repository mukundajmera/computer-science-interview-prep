# Vending Machine - Follow-Up Questions

## Follow-up questions
1. How would you handle exact-change-only mode before accepting money?
2. How would you add card or mobile payment without rewriting the state machine?
3. What should happen if dispense fails after payment is accepted?
4. How would admin restock and money collection avoid interfering with a customer transaction?
5. How would you make one machine thread-safe while still supporting many machines?

## Variants and extensions
1. Product categories and dynamic pricing.
2. Transaction history for audits and reconciliation.
3. Low-stock and low-change alerts.
4. Timeout-driven cancellation with automatic refund.

## Interviewer probes to prepare
- "Which operation commits the transaction?"
- "Where do you calculate and reserve change?"
- "Why is State a better fit than nested conditionals here?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
