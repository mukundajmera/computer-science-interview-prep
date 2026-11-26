# Online Auction - Follow-Up Questions

## Follow-up questions
1. How would you prevent two concurrent bids from both appearing to win?
2. What should an idempotent retry return if the original bid was already accepted?
3. How would you model reserve price, bid increment, and auction close time?
4. How would read snapshots stay consistent with the canonical mutable auction record?
5. What changes if storage moves from one in-memory repository to a distributed backing store?

## Variants and extensions
1. Auto-bidding with maximum bidder limits.
2. Anti-sniping extension windows near auction close.
3. Seller cancellation and buyer withdrawal rules.
4. Audit log of bid mutation intents and final snapshots.

## Interviewer probes to prepare
- "Which state transitions reject a bid?"
- "Where is monotonic bidding enforced?"
- "What makes the mutation replay-safe in v3?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
