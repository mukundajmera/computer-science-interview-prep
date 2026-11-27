# API Gateway Pitfalls

## Common Mistakes
- Not caching JWKS keys locally.
- Global rate limiting using per-request Redis calls leading to bottleneck.
- Not shedding non-critical traffic during load spikes.
- Retrying downstream failures without circuit breaking or jittered backoff: synchronized retries at 100k peak QPS trigger retry storms that keep an unhealthy microservice from recovering. Trip a Hystrix-style circuit breaker to `OPEN` once the rolling failure rate exceeds threshold and fast-fail with `503` alongside exponential backoff with jitter.
- Skipping header scrubbing in the Security/Auth filter: forwarding raw client headers lets callers spoof internal identity or routing metadata trusted by downstream services. Strip and rewrite internal headers at the gateway before executing the Routing Filter.
- Leaving local token-bucket pre-fetch batches unbounded: fetching oversized token batches from Redis into gateway memory causes large quota overshoot across nodes or wasted quota when a node crashes. Cap local batch sizes per client tier (such as Free vs. Pro) to balance the <10 ms P99 latency budget against acceptable quota drift.
- Neglecting HTTP/1.1 connection pooling during HTTP/2 down-conversion: opening a fresh TCP connection to downstream services for each multiplexed HTTP/2 stream exhausts ephemeral ports and breaches the <10 ms P99 added-latency target. Maintain bounded, persistent upstream connection pools with explicit per-route timeouts that return `504` on expiry.
- Storing non-ephemeral routing or session state locally on gateway nodes: stateful nodes cannot auto-scale cleanly during 15x traffic bursts and lose state on instance restarts. Keep gateway nodes stateless, store distributed rate-limit state in Redis, and resolve downstream targets through Service Discovery.

## Design Contract
- Adheres to the design contract for distributed rate limiting in [DESIGN.md](./DESIGN.md).

## Failure Trace
- Describes how failure in Redis doesn't bring down the entire gateway.

## Beginner vs Staff
### Beginner
- Might not implement caching, or uses centralized Auth Service per request.
### Staff
- Recognizes trade-off of local token caching: slight loss of strict global precision for latency gains.
