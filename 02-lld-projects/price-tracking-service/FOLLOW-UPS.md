# Price Tracking Service - Follow-Up Questions

## Follow-up questions
1. How would you deduplicate repeated price events without suppressing legitimate changes?
2. What should happen if alert dispatch fails after the price history was recorded?
3. How would you query the latest price and a bounded history window efficiently?
4. How would threshold subscriptions handle price drops, price rises, and unchanged values?
5. What changes when collectors write to a distributed repository by region?

## Variants and extensions
1. Percent-change and absolute-threshold subscriptions.
2. Multiple marketplaces or regions per product.
3. Alert delivery retries with idempotent notification keys.
4. Compacted history retention for old price events.

## Interviewer probes to prepare
- "What is the canonical record for a price event?"
- "When is an alert safe to dispatch?"
- "Where does v3 idempotency sit in the write path?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
