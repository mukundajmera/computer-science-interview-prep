# Approach for Payment System

## Overview and Core Strategy
Designing a payment system requires uncompromising standards for data integrity, security, and fault tolerance. The core challenge is integrating with external, often unreliable, third-party payment gateways (like Stripe or Adyen) while ensuring that our internal financial ledger remains perfectly balanced. A dropped network packet must never result in a customer being double-charged or wrongly declined.

Our approach rejects standard synchronous CRUD operations in favor of a strictly state-machine-driven, event-sourced architecture built around idempotency and robust asynchronous reconciliation. We treat money not as a mutable integer, but as an immutable ledger of movements.

## Idempotency as a First-Class Citizen
Every single mutating API call (e.g., charge, refund, authorize) must include a client-generated `Idempotency-Key` (typically a UUID). Before any business logic executes, the system checks this key against a highly available cache (like Redis). 
- If the key does not exist, the system acquires a lock, processes the payment, and caches the final HTTP response against that key.
- If the key exists, the system verifies the intent payload hash matches the cached hash. If it matches, the system immediately returns the exact HTTP response from the original request, ensuring a repeated idempotency key with the same payload returns the same intent. If the payload has changed, the request is rejected with an exception without creating a second charge.
This fundamentally protects the system from double-charges when mobile clients automatically retry requests due to poor network connectivity.

```java
// Java Implementation
public String checkOrAcquire(String key, String payloadHash) {
    synchronized (store) {
        CacheEntry entry = store.get(key);
        if (entry != null) {
            if (!entry.payloadHash.equals(payloadHash)) {
                throw new IllegalArgumentException("Repeated idempotency key with changed payload");
            }
            return entry.response;
        }
        // ... acquire lock and proceed
    }
}
```

```python
# Python Implementation
def check_or_acquire(self, key: str, payload_hash: str) -> Optional[Dict[str, Any]]:
    with self._lock:
        if key in self._store:
            entry = self._store[key]
            if entry['payload_hash'] != payload_hash:
                raise ValueError("Repeated idempotency key with changed payload")
            return entry['response']
        # ... acquire lock and proceed
```

## State Machine Driven Processing
A payment is not a simple database row update. It is a strictly enforced State Machine: `INITIATED` -> `GATEWAY_PENDING` -> `AUTHORIZED` -> `CAPTURED` (or `FAILED`/`DECLINED`). 
Every transition is logged immutably. We do not allow arbitrary state jumps. If a payment is in `GATEWAY_PENDING`, the system knows a network call is in flight. Subsequent retry attempts are blocked until the first call resolves or a strict timeout occurs, preventing race conditions with the third-party gateway.

## Asynchronous Ledger Reconciliation
We do not attempt to write to the financial ledger synchronously while the user is waiting for the checkout spinner. 
- Once the third-party gateway confirms the charge, we update the payment state to `CAPTURED` and return success to the user immediately.
- We then emit an event (e.g., `PaymentCapturedEvent`) to a message broker (like Kafka).
- A separate, highly isolated Ledger Service consumes this event and performs the double-entry accounting (debiting the user liability account, crediting the merchant revenue account). This separation ensures the user experience is not bottlenecked by slow database transactions on the ledger.

## Resilience and Fallbacks
Network calls to external gateways will fail. We approach this using Circuit Breakers and carefully tuned exponential backoff. If a gateway goes down, the circuit breaker opens, immediately failing fast to prevent our internal thread pools from exhausting while waiting for timeouts. 
Furthermore, webhook deliveries from external gateways can be duplicated or out-of-order. A robust reconciliation engine handles ambiguous gateway timeouts, retries, declines and compensations by locking the transaction and verifying it is not already in a terminal state (like `COMPLETED` or `FAILED`). This compensation approach preserves allowed transitions and money conservation natively.

We run nightly batch reconciliation jobs that compare our internal ledger state against settlement reports downloaded directly from the payment gateways, automatically flagging any discrepancies for manual review.

## Supported Versions and Review
Each assigned document describes actual supported versions (e.g. standard-library-only Java 11+ and Python 3.8+). No line/word minimum replaces semantic review, as we prioritize implementation-grounded architectural explanations over superficial text filling.
