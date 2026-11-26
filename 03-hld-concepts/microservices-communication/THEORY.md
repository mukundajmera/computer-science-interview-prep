# Microservices Communication

## What is it?

Microservices communication refers to patterns and protocols for services to exchange data and coordinate actions in a distributed system.

## Why do we need it?

**Problem**: In a monolith, function calls are fast and reliable. In microservices, network calls are slow and can fail.

**Solution**: Use appropriate communication patterns (sync/async) with resilience patterns (circuit breakers, retries).

## Types/Approaches

### 1. Synchronous Communication
- **HTTP/REST**: Simple, widely supported
- **gRPC**: Binary protocol, faster, typed
- **GraphQL**: Flexible queries

### 2. Asynchronous Communication  
- **Message Queues**: Kafka, RabbitMQ, SQS
- **Event-Driven**: Publish-subscribe
- **Event Sourcing**: Store events as source of truth

## How it works

```
Synchronous (Request-Response):
┌─────────┐    HTTP/gRPC    ┌─────────┐
│Service A│ ───────────────▶│Service B│
└─────────┘ ◀─────────────── └─────────┘
              Response

Asynchronous (Event-Driven):
┌─────────┐    Publish      ┌─────────────┐    Subscribe    ┌─────────┐
│Service A│ ───────────────▶│Message Queue│ ───────────────▶│Service B│
└─────────┘                 └─────────────┘                 └─────────┘
                                  │
                                  ▼
                            ┌─────────┐
                            │Service C│
                            └─────────┘
```

## Resilience Patterns

### Circuit Breaker
Prevents cascading failures by stopping calls to failing services.

```
States: CLOSED → OPEN → HALF_OPEN → CLOSED

CLOSED:   Normal operation, track failures
OPEN:     Stop calling, return error immediately  
HALF_OPEN: Allow test request to check recovery
```

### Retry with Exponential Backoff
```
Attempt 1: Wait 0ms
Attempt 2: Wait 100ms
Attempt 3: Wait 200ms  
Attempt 4: Wait 400ms + jitter
```

### Bulkhead
Isolate resources to prevent one failure from consuming all resources.

### Timeout
Fail fast rather than wait indefinitely.

## Trade-offs

| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **Latency** | Higher (waits) | Lower (fire-and-forget) |
| **Coupling** | Tight | Loose |
| **Complexity** | Lower | Higher |
| **Debugging** | Easier | Harder |
| **Consistency** | Immediate | Eventual |

## When to use

| Pattern | Use When |
|---------|----------|
| Sync HTTP | Simple CRUD, low latency required |
| gRPC | High throughput, internal services |
| Message Queue | Decoupling, reliability needed |
| Events | Multiple consumers, audit trail |

## Key Takeaways

1. **Choose sync for simplicity, async for scalability**
2. **Always implement timeouts and retries**
3. **Circuit breakers prevent cascading failures**
4. **Idempotency is crucial for retries**
5. **Monitor latency and error rates**
