# Payment Gateway Router - Common Pitfalls

## 1. Non-atomic idempotency checks
- **Failure Signal**: Concurrent requests with the same idempotency key slip past checks and both attempt a charge.
- **Root Cause**: Doing a `get()` and then `put()` in a non-thread-safe manner.
- **Mitigation**: Using `ConcurrentHashMap` (Java) or explicit Locks (Python) and implementing atomic "lock or check" methods.
- **Validation**: Load test with concurrent identical requests.

## 2. Silent double-charging during timeout fallbacks
- **Failure Signal**: Provider 1 times out, Router falls back to Provider 2. However, Provider 1 actually processed the charge but the network response timed out.
- **Root Cause**: Treating network timeouts interchangeably with definitive transaction failures.
- **Mitigation**: Network timeouts on payment attempts are fundamentally ambiguous. Fallbacks must often require either querying Provider 1 for status first or relying on eventual consistency/reconciliation. In interviews, state this constraint clearly.

## 3. Missing health window resets
- **Failure Signal**: A provider goes down, success rate hits 0%, and it is never routed to again, even after it recovers.
- **Root Cause**: The sliding window only records failures and no success-probing mechanisms exist.
- **Mitigation**: Circuit breakers implementing the `HALF_OPEN` state correctly probe the provider after a timeout.

## 4. Tight coupling of gateway client SDKs
- **Failure Signal**: Core routing logic imports classes directly from `com.stripe.Stripe`.
- **Root Cause**: Failure to use the Adapter pattern.
- **Mitigation**: Standardized internal `PaymentRequest` and `PaymentResponse` objects, keeping SDK code strictly inside the adapter implementation.
