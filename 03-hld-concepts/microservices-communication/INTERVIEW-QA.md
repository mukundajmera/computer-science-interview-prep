# Interview Questions: Microservices Communication

## Basic Questions

### 1. What are the main communication patterns in microservices?
**Q**: Describe sync vs async communication patterns.

**A**: 
- **Synchronous**: Request-response, caller waits (HTTP, gRPC)
- **Asynchronous**: Fire-and-forget, message queues, events

Trade-off: Sync is simpler but creates coupling; async is complex but more resilient.

---

### 2. What is a circuit breaker?
**Q**: Explain the circuit breaker pattern.

**A**: Prevents cascading failures by stopping calls to failing services:
- **CLOSED**: Normal, track failures
- **OPEN**: Fail fast, don't call
- **HALF_OPEN**: Test if service recovered

---

### 3. When would you use gRPC vs REST?
**Q**: Compare gRPC and REST APIs.

**A**:
| Aspect | REST | gRPC |
|--------|------|------|
| Protocol | HTTP/1.1 | HTTP/2 |
| Format | JSON (text) | Protobuf (binary) |
| Speed | Slower | Faster |
| Browser | Native | Needs proxy |
| Use case | Public APIs | Internal services |

---

## Intermediate Questions

### 4. How do you handle cascading failures?
**Q**: Service A calls B calls C. C is slow. What happens?

**A**: **Problems**:
- Thread pool exhaustion
- Timeout accumulation
- Memory pressure

**Solutions**:
- Timeouts at each level
- Circuit breakers
- Bulkhead isolation
- Async where possible

---

### 5. Explain retry with exponential backoff
**Q**: Why use exponential backoff for retries?

**A**: 
- Linear retries can overwhelm recovering service
- Exponential: 1s, 2s, 4s, 8s...
- Jitter: Add randomness to prevent thundering herd
- Max retries: Eventually give up

---

## Advanced Questions

### 6. Design service-to-service auth
**Q**: How do services authenticate each other?

**A**:
- **mTLS**: Mutual TLS with certificates
- **JWT tokens**: Service identity tokens
- **Service mesh**: Sidecar handles auth (Istio)
- **API keys**: Simple but less secure

---

### 7. How do you debug distributed systems?
**Q**: A request fails. How do you trace it?

**A**:
- **Distributed tracing**: Jaeger, Zipkin
- **Correlation IDs**: Pass through all services
- **Centralized logging**: ELK stack
- **Service mesh observability**

---

## How to Explain in 30 Seconds

"Microservices communicate either synchronously via HTTP/gRPC for immediate responses, or asynchronously via message queues for decoupling. Key resilience patterns include circuit breakers to prevent cascading failures, retries with exponential backoff for transient errors, and timeouts to fail fast. The choice depends on consistency requirements—sync for immediate, async for eventual—and observability through distributed tracing is essential for debugging."
