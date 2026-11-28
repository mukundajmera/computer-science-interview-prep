# Service Discovery

## What is it?

Service discovery is the process of automatically detecting and tracking the network locations (IP addresses and ports) of service instances in a distributed system.

## Why do we need it?

**Problem**: In dynamic environments (containers, auto-scaling), service IPs change frequently. Hardcoded IPs don't work.

**Solution**: Service registry maintains current locations; clients query to find services.

## Types/Approaches

### 1. Client-Side Discovery
- Client queries registry directly
- Client chooses instance (load balancing)
- Examples: Netflix Eureka, Consul

```
┌────────┐     Query      ┌──────────┐
│ Client │ ─────────────▶ │ Registry │
└────┬───┘                └──────────┘
     │
     │ Direct call
     ▼
┌──────────┐
│ Service  │
└──────────┘
```

### 2. Server-Side Discovery
- Load balancer queries registry
- Client calls load balancer
- Examples: Kubernetes, AWS ELB

```
┌────────┐     Call       ┌──────────────┐     Query      ┌──────────┐
│ Client │ ─────────────▶ │Load Balancer │ ─────────────▶ │ Registry │
└────────┘                └──────┬───────┘                └──────────┘
                                 │
                                 ▼
                          ┌──────────┐
                          │ Service  │
                          └──────────┘
```

### 3. DNS-Based Discovery
- Services register in DNS
- Clients resolve DNS names
- Simpler but less dynamic

## Key Components

### Service Registry
- Stores service instances
- Health check integration
- Examples: Consul, etcd, ZooKeeper

### Health Checks
- Active: Registry pings services
- Passive: Services send heartbeats
- Failure: Remove unhealthy instances

## Trade-offs

| Aspect | Client-Side | Server-Side | DNS |
|--------|-------------|-------------|-----|
| **Complexity** | Client logic | Infrastructure | Simple |
| **Latency** | Lower | Higher | Caching issues |
| **Flexibility** | High | Medium | Low |
| **Dependencies** | Registry client | Load balancer | DNS server |

## Key Takeaways

1. **Choose based on environment**: Kubernetes → server-side; microservices → client-side
2. **Health checks are critical**: Detect failures quickly
3. **TTL for deregistration**: Auto-cleanup on crashes
4. **Caching with invalidation**: Balance latency and freshness
5. **Consistency requirements**: CP vs AP trade-offs

## 📊 Diagrams

- [Client-side vs server-side discovery](./diagrams/client-vs-server-side-discovery.mmd) - compares the two discovery flows against a shared registry: clients querying the registry and calling an instance directly, versus clients hitting a load balancer that queries the registry and routes, with health heartbeats keeping the registry current.
