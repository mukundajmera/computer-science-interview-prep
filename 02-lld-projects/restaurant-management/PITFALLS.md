# Restaurant Management - Common Pitfalls

## Common pitfalls
1. Treating table status as global availability and ignoring reservation time slots.
2. Letting orders jump from placed to billed without kitchen, ready, served, and payment transitions.
3. Allowing order modifications after preparation has started without a clear correction flow.
4. Calculating one bill total but not modeling tax, tip, split bills, or payment status.
5. Accepting menu items without checking availability or ingredient constraints.

## Why these fail interviews
- They double-book scarce tables during peak hours.
- They make kitchen display updates and server handoffs unreliable.
- They mix reservation, ordering, kitchen, billing, and payment responsibilities into one procedural flow.

## Mitigations
- Model reservations by table, party size, and time slot, not just current table status.
- Make order state transitions explicit: placed, preparing, ready, served, billed, completed.
- Only allow simple modifications before kitchen preparation unless a compensating command is modeled.
- Keep bill calculation tied to order items, tax, tip, split strategy, and payment status.
- Check item availability before submitting an order to the kitchen queue.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
