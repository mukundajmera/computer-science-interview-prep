# Payment Gateway Router - Problem Statement

## Functional Requirements
- Multi-gateway routing: Support routing payments across Stripe, Razorpay, and Paypal.
- Routing strategies: Support dynamic routing based on gateway health and success rate.
- Idempotency key caching: Implement idempotency deduplication with conflict detection to avoid double charging.
- Circuit breaker: Implement per-gateway circuit breakers to stop traffic to unhealthy gateways.
- Automatic fallback: Provide automatic fallback mechanisms to alternative gateways on retryable failures (e.g. timeouts).
- Webhook event deduplication: Avoid processing duplicate webhook events from gateways.

## Non-Functional Requirements
- High Availability: The router must seamlessly failover when dependencies degrade.
- Low Latency: Gateway selection and idempotency checks must be fast.
- Thread-Safety: Idempotency, circuit breakers, and success rate calculation must be safe for concurrent execution.

## Core Entities
- `PaymentRequest`: Encapsulates transaction ID, idempotency key, amount, currency, and user ID.
- `PaymentResponse`: Encapsulates transaction status (SUCCESS, FAILED, TIMEOUT, CONFLICT), message, and gateway name.
- `PaymentGateway`: Interface for abstracting different providers (Stripe, Razorpay, Paypal).
- `RoutingStrategy`: Strategy interface for dynamically selecting the next gateway to attempt.
- `IdempotencyStore`: Stores states of transactions mapped by idempotency keys to handle duplicates.
- `CircuitBreaker`: Tracks and limits requests to gateways experiencing high failure rates.
