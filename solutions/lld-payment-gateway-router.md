# 🏆 Coach Answer: Payment Gateway Router — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate/Hard  
> **Time Target:** 45 minutes

---

## Canonical Interview Answer

This project has a definitive canonical interview answer that thoroughly explains the adapter pattern for gateways, idempotency store concurrency, dynamic routing strategy, and circuit-breaker fallback mechanisms.

Please refer to the full canonical answer here:
[Payment Gateway Router - Strong Answer](../02-lld-projects/payment-gateway-router/STRONG-ANSWER.md)

---

## Key Takeaways

1. **Idempotency**: Thread-safe locks (`IN_PROGRESS` vs `COMPLETED`), proper conflict detection, returning cached transaction IDs for duplicates.
2. **Failover/Fallback**: Clean iteration loop attempting multiple gateways upon provider timeouts or 500s.
3. **Health Tracking**: Encapsulated Circuit Breaker logic and moving average success rate calculation without tight coupling.
4. **Extensibility**: Adding new gateways (like Paypal) or new routing strategies (like cost-based routing) without modifying the core router.
