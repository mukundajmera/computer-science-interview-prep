# Market Alert Engine - Strong Answer

## Strategy
1.  Establish the basic `Tick` format.
2.  Design the rule evaluation core using the Composite pattern.
3.  Address the cooldown requirement with a thread-safe state map.
4.  Optimize the routing of ticks to rules by indexing.

## Key Considerations

**Say:** "To handle complex boolean expressions cleanly, I'll use the Composite design pattern. This means an `AndCondition` and a simple `PriceCondition` both implement the same `Condition` interface."

**Say:** "For the cooldown mechanism, it's stateful. We need to prevent alert floods. I will use a thread-safe structure like `ConcurrentHashMap` keyed by a combination of the rule ID and the symbol. We'll update the timestamp atomically to avoid race conditions when multiple ticks cross the threshold simultaneously."

## Cross-links
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
