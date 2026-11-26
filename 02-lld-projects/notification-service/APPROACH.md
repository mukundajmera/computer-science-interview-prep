# Approach

We will build the system iteratively over three versions:

## v1: Basic Dispatcher
- Implement basic channel interfaces (Email, SMS).
- Dispatch notifications directly without queuing.
- Basic user preferences setup.
- Idempotency checks: Same event/recipient/channel idempotency key produces at most one recorded delivery intent.
- Enforce explicit routing, user preference checks, and unsubscribe logic.
- Fixed version-specific APIs and deterministic fixture inputs/expected outputs (no production/security promise inferred).

## v2: Priority Queuing & Rate Limiting
- Introduce an in-memory queue to decouple request intake from dispatching.
- Implement priority queues to handle high-priority messages first.
- Add rate limiting logic per channel.
- Bounded queue overflow handling that preserves intent state.

## v3: Resiliency & Advanced Routing
- Implement a Retry Engine using exponential backoff.
- Add advanced user preference routing (falling back to alternative channels if a primary one fails).
- Handle multi-threading for dispatching to improve throughput.
- Handle fake provider timeout/unknown outcome, permanent failure, and duplicate callbacks.
- Preserve intent state without promising external exactly-once delivery.
