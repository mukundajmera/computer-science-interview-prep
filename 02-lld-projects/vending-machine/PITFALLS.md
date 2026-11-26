# Vending Machine - Common Pitfalls

## Common pitfalls
1. Modeling the flow as one large method instead of explicit machine states.
2. Dispensing before proving stock, sufficient payment, and change availability.
3. Losing inserted money on cancel, invalid slot selection, or dispense failure.
4. Mixing product inventory and coin inventory into one unclear abstraction.
5. Ignoring the one-transaction-per-machine constraint when discussing concurrency.

## Why these fail interviews
- They make invalid transitions possible and hard to test.
- They risk money loss or double dispense in partial-failure paths.
- They blur where payment, inventory, and state responsibilities belong.

## Mitigations
- Name the allowed transitions from `IDLE` to `HAS_MONEY` to selection/dispense and back.
- Validate stock, balance, and change before reducing inventory.
- Keep inserted funds refundable until dispense is committed.
- Separate slot inventory from coin/change inventory.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Design patterns](../../01-design-patterns/README.md)
