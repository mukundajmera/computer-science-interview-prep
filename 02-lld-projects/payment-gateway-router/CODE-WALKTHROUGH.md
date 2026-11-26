# Payment Gateway Router - Code Walkthrough

1. **PaymentRequest & PaymentResponse**: These objects encapsulate incoming transaction requirements and standardize outbound results.
2. **IdempotencyStore**: Uses an `IN_PROGRESS` lock logic to instantly fail conflicting concurrent requests. It caches the final `COMPLETED` or `FAILED` states to respond immediately to safely repeated requests.
3. **Gateway Adapters (`AbstractPaymentGateway`, `StripeGatewayAdapter`, etc.)**: These wrappers around hypothetical provider SDKs contain their own `CircuitBreaker` and success-rate tracking window.
4. **CircuitBreaker**: Manages the `CLOSED`, `OPEN`, and `HALF_OPEN` states. In our basic implementation, it opens after a fixed number of failures and resets after a defined timeout.
5. **GatewayRouter**: The orchestration layer.
   - It intercepts the request, checks the `IdempotencyStore`.
   - Iterates up to `N` times (where `N` is the number of gateways), calling the `RoutingStrategy` to select the best available gateway.
   - If a gateway returns a `SUCCESS`, the loop exits. If it fails with a retryable issue (like a `TIMEOUT`), the loop continues.
   - Finally, the response is pushed to the `IdempotencyStore` and returned.
6. **HealthBasedRoutingStrategy**: Filters out unavailable gateways (open circuit breakers) and sorts the rest by their tracked sliding-window success rates.
