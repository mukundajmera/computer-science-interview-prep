# API Gateway Comparison

## Alternatives
- **Nginx/HAProxy:** Good for basic routing, but harder to implement custom auth and complex rate limiting dynamically.
- **Envoy:** Powerful, but complex to configure and operate for simpler use cases.
- **Custom Gateway:** Allows specific business logic like batching rate limits, matching our design contract [DESIGN.md](./DESIGN.md).

## Failure Trace comparison
- Custom gateway circuit breaker allows fine-grained failure handling compared to basic reverse proxies.

## Beginner vs Staff
### Beginner
- Just knows Nginx.
### Staff
- Understands Envoy's architecture (xDS APIs) and when a custom gateway is more appropriate.
