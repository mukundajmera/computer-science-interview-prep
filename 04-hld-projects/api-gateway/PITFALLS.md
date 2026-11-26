# API Gateway Pitfalls

## Common Mistakes
- Not caching JWKS keys locally.
- Global rate limiting using per-request Redis calls leading to bottleneck.
- Not shedding non-critical traffic during load spikes.

## Design Contract
- Adheres to the design contract for distributed rate limiting in [DESIGN.md](./DESIGN.md).

## Failure Trace
- Describes how failure in Redis doesn't bring down the entire gateway.

## Beginner vs Staff
### Beginner
- Might not implement caching, or uses centralized Auth Service per request.
### Staff
- Recognizes trade-off of local token caching: slight loss of strict global precision for latency gains.
