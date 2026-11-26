# Payment Gateway Router - Approach

## Entity Identification
- **Gateway Abstraction**: The core of the system uses the Adapter pattern via the `PaymentGateway` interface to standardize the behavior of various third-party gateways (Stripe, Razorpay, Paypal).
- **Routing Strategy**: A Strategy pattern defines `RoutingStrategy`. The `HealthBasedRoutingStrategy` examines gateway availability (circuit breaker states) and success rates.
- **Idempotency Store**: A centralized store holding mappings from idempotency keys to states (IN_PROGRESS, COMPLETED, FAILED) and stored `PaymentResponse`s.
- **Circuit Breaker**: Implementing a state machine with CLOSED, OPEN, and HALF_OPEN states to gracefully fail when a gateway is unresponsive.

## Design Patterns Used
- **Adapter Pattern**: To standardize external payment providers.
- **Strategy Pattern**: To cleanly separate routing algorithms.
- **State Machine**: For managing both idempotency states and circuit breaker states.

## Success Rate Tracking
Gateways track their successes and failures using a sliding window. This enables dynamic routing strategies to prioritize healthier gateways or failover entirely when the success rate dips below thresholds.
