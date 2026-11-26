# Quick Commerce Delivery — Follow-Up Questions

## 1. How do you include traffic and weather in delivery guarantees?

Introduce ETA service inputs into center eligibility and dynamically reduce eligible radius when conditions worsen.

## 2. How do you support substitutions automatically?

Add substitution preferences to order lines and resolve alternatives within same transactional reservation boundary.

## 3. How do you handle inventory update lag from warehouse systems?

Use event streams for frequent deltas plus periodic reconciliation jobs; surface confidence score in availability API.

## 4. How does design change for multi-city expansion?

Partition by region/city, keep inventory writers local, and replicate read summaries for nearby cross-border zones.

## 5. How do you support scheduled deliveries?

Add reservation windows and hold buckets by time slot instead of immediate decrement only.

## 6. What if one center fails mid-order?

Add orchestration fallback to alternate center with partial fulfillment rules and explicit user confirmation flow.
