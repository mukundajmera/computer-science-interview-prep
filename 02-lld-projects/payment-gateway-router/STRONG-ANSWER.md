# Strong Answer: Payment Gateway Router

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "The core requirement is to design a Payment Gateway Router that seamlessly proxies incoming payment requests to third-party payment providers like Stripe, Razorpay, or PayPal. It needs to handle dynamic routing based on gateway health, execute automatic fallbacks for retryable failures, and rigorously enforce idempotency to prevent duplicate charges. High availability and thread safety are critical non-functional requirements."

## 2. Entity Modeling & APIs (10 mins)
**Say:** "Let's define the primary entities and their relationships. We have a `GatewayRouter` which acts as the orchestrator. It receives a `PaymentRequest` and returns a `PaymentResponse`.
The router relies on three main components:
1. **`PaymentGateway` Interface:** Abstracts the third-party providers using the Adapter Pattern.
2. **`RoutingStrategy`:** Defines how we select the next gateway to attempt, such as a `HealthBasedRoutingStrategy`.
3. **`IdempotencyStore`:** Tracks transaction states by their idempotency keys to handle duplicate requests."

## 3. Data Structure & Design Pattern Rationale (10 mins)
**Say:** "For modularity, I'll use the **Adapter Pattern** for the gateways, allowing us to add new providers without modifying the core router. The **Strategy Pattern** will be used for routing, so we can swap between Health-Based routing and other strategies like Cost-Based routing.
To manage availability, each gateway will have a **Circuit Breaker** implemented as a state machine (`CLOSED`, `OPEN`, `HALF_OPEN`), tracking success rates over a sliding window.
For the `IdempotencyStore`, I will use a `ConcurrentHashMap` mapping an idempotency key to a `Record` containing a state (`IN_PROGRESS`, `COMPLETED`, `FAILED`) and a `ReentrantLock` (or Python Lock) to ensure thread-safe atomic updates."

## 4. Concurrency Defense & Correctness (10 mins)
**Say:** "Given that this system handles financial transactions concurrently, ensuring thread safety is paramount—especially around idempotency. If two requests with the same idempotency key arrive simultaneously, we use the `ConcurrentHashMap.compute()` or atomic `lock_or_check` logic. The first thread registers the key as `IN_PROGRESS` and proceeds. The second thread detects the `IN_PROGRESS` state and immediately returns a `CONFLICT` error, safely avoiding a race condition that could lead to double charging. Once the first thread finishes, it updates the state to `COMPLETED` and caches the response for future identical requests."

## 5. Failure Handling & Fallbacks (7 mins)
**Say:** "Systems fail, so we need to anticipate and handle gateway degradation gracefully. I implement a fallback loop in the `GatewayRouter`. When a payment request arrives, the router queries the `RoutingStrategy` to get an available gateway (one whose circuit breaker is not `OPEN`). It attempts the payment. If the gateway times out or returns a retryable failure, the router catches this, records the failure (which may trip the gateway's circuit breaker), and continues the loop to try the next available gateway. If a gateway returns `SUCCESS`, the loop breaks."

## 6. Production Trade-offs (3 mins)
**Say:** "In a real production environment, keeping the `IdempotencyStore` strictly in-memory means data is lost on a router restart. We would transition this to a distributed cache like Redis with TTL expiration and atomic `SETNX` commands. Additionally, network timeouts during payment attempts are ambiguous—did the provider process it or not? Our fallback logic must acknowledge this trade-off, potentially requiring reconciliation jobs or querying the first provider's status before blindly retrying on a second provider."
