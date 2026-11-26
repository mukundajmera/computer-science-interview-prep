# Online Auction - Common Pitfalls

## Common pitfalls
1. Treating the auction as a generic key/value store and skipping domain states.
2. Accepting bids without proving the auction is open and the amount is strictly valid.
3. Updating the highest bid before the validation and persistence boundary is clear.
4. Returning read snapshots that can disagree with the canonical auction record.
5. Adding v3 idempotency as a logging note instead of a replay-safe mutation contract.

## Why these fail interviews
- They allow invalid transitions such as bidding on closed auctions.
- They make concurrent bid races and duplicate retries ambiguous.
- They blur the difference between mutable records, mutation intents, and read snapshots.

## Mitigations
- Name the auction states and the allowed transitions before coding.
- Keep bid validation in a policy that can check amount, bidder, and lifecycle rules.
- Persist the accepted mutation before exposing the new highest-bid snapshot.
- Treat idempotency keys as part of the write contract, not as optional metadata.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
