# Brokerage Platform — Follow-Up Questions

## 1. How do you support multiple exchanges?
Introduce exchange routing policy per symbol and health-aware failover with deterministic retries.

## 2. How do you keep quote fanout cost under control?
Aggregate subscriptions by symbol, compress updates, and apply adaptive sampling for inactive clients.

## 3. How do you handle cancel/replace flows?
Model cancel/replace as atomic workflow with command IDs and conflict checks.

## 4. What changes for after-hours trading?
Add session-aware validation and execution policies by market phase.

## 5. How do you detect stale client views?
Use monotonic sequence IDs and replay-on-reconnect behavior.

## 6. How do you improve resilience during exchange outage?
Enable circuit breakers, queue gating, and explicit user status for impacted symbols/orders.
