# Payment Gateway Router - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
| --- | --- | --- |
| **Idempotency** | 30% | Thread-safe locks (`IN_PROGRESS` vs `COMPLETED`), proper conflict detection, returning cached transaction IDs for duplicates. |
| **Failover/Fallback** | 25% | Clean iteration loop attempting multiple gateways upon provider timeouts or 500s. |
| **Health Tracking** | 25% | Encapsulated Circuit Breaker logic and moving average success rate calculation without tight coupling. |
| **Extensibility** | 20% | Adding new gateways (like Paypal) or new routing strategies (like cost-based routing) without modifying the core router. |

## Performance bands

- **Hire**: The system correctly deduplicates requests, implements a clear adapter pattern for gateways, correctly routes based on metrics, and demonstrates a functional circuit breaker and fallback loop.
- **Leaning Hire**: Missing some optimization or minor thread-safety concerns in sliding window calculations, but the core abstractions and failure handling are present.
- **No Hire**: Hits hard failure gates.

## Hard failure gates
- Duplicate charges on identical idempotency keys (No thread safety or locking).
- Unhandled gateway failovers (No loop, single failure cascades to client).
- Cascading timeouts without circuit breaker.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design](DESIGN.md)
