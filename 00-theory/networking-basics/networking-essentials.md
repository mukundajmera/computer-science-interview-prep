# Networking Essentials

Networking is the substrate for every distributed system decision. In interviews, you are expected to reason about protocol choice, latency budgets, regional routing, and failure behavior without going deep into packet-level internals.

---

## What to Know by Default

- Layered model: network (`IP`) -> transport (`TCP`/`UDP`/`QUIC`) -> application (`HTTP`, `WebSocket`, `gRPC`, `DNS`).
- `TCP` is the safe default for reliable ordered delivery.
- `UDP` is justified when latency matters more than guaranteed delivery.
- `QUIC`/`HTTP/3` reduces connection setup and helps under lossy networks.
- DNS and load-balancer hops are part of request latency and should be included in your mental model.

---

## Protocol Selection Cheatsheet

| Need | Default Choice | Why |
|------|----------------|-----|
| CRUD APIs | HTTP over TCP | Ubiquitous tooling and reliability |
| Internal low-latency RPC | gRPC over HTTP/2 | Efficient transport + typed contracts |
| Server push / one-way realtime | SSE / WebSocket | Avoid polling overhead |
| Bi-directional realtime | WebSocket | Persistent full-duplex channel |
| Loss-tolerant realtime media | UDP/WebRTC | Lower latency and no retransmit blocking |

---

## Latency and Throughput Reality

- Reduce round trips first; protocol micro-optimizations come second.
- Tail latency (`p95`/`p99`) drives user experience under load.
- Connection reuse (keep-alive, HTTP/2 multiplexing) is often a bigger win than payload tuning.
- Cross-region traffic should be explicit in design: what must be global vs local.

---

## Failure Handling Basics

- Use bounded timeouts (`connect`, `read`, `write`) on every network hop.
- Retries require idempotency and jittered backoff.
- Circuit breakers and load shedding prevent retry storms during outages.
- Prefer degraded responses over total failure for user-facing paths.

---

## Requirements and constraints

- Keep request path stateless where possible so horizontal scale remains simple.
- Bound the hop count on latency-critical flows.
- Define protocol per interface type (client API vs internal RPC vs realtime channel).
- Set explicit SLOs: p95 latency, error rate, and availability target.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Protocol fit | Explains TCP/UDP/WebSocket/gRPC with requirement match | Uses protocol names without rationale |
| Latency model | Mentions round trips, tails, and regional impact | Talks only average latency |
| Failure design | Timeouts, retries, jitter, circuit breaker, fallback | "Retry until success" |
| Trade-offs | States what is optimized and what is sacrificed | Claims all goals are achieved simultaneously |

## Common pitfalls

- Treating all workloads as plain request/response HTTP.
- Ignoring DNS and LB hops in latency estimates.
- Adding aggressive retries without idempotency protection.
- Assuming cross-region consistency is free.

## Follow-up questions

- When do you move from REST to gRPC for internal service calls?
- What changes when clients are globally distributed?
- How do you avoid cascading failure when a dependency is slow?
- When is UDP justified for product-facing features?

## Variants and extensions

- Multi-region active-active with geo-routing and failover.
- Edge-heavy architectures with CDN and edge compute.
- Mixed-protocol systems: HTTP for control plane, WebSocket/UDP for data plane.

## Related Topics

- [HTTP/HTTPS](./http-https.md)
- [REST API Design](./rest-api-design.md)
- [gRPC](./grpc.md)
- [Load Balancing](../../03-hld-concepts/load-balancing/)
- [Service Discovery](../../03-hld-concepts/service-discovery/)
- [Chat Service HLD](../../04-hld-projects/chat-service/)
