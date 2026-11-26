# Interview Questions: Service Discovery

## Basic Questions

### 1. What is service discovery?
**Q**: Explain service discovery and why it's needed.

**A**: Service discovery automatically locates network addresses of service instances. Needed because:
- Container IPs are dynamic
- Auto-scaling changes instances
- Failover requires rerouting

---

### 2. Client-side vs server-side discovery?
**Q**: Compare the two approaches.

**A**:
| Aspect | Client-Side | Server-Side |
|--------|-------------|-------------|
| Who queries registry | Client | Load balancer |
| Load balancing | Client decides | LB decides |
| Complexity | Client library | Infrastructure |
| Example | Eureka | Kubernetes |

---

### 3. What is a service registry?
**Q**: What does a service registry do?

**A**: Maintains database of service instances:
- **Registration**: Services register on startup
- **Deregistration**: Remove on shutdown or TTL expiry
- **Health checks**: Track instance health
- **Query**: Return healthy instances

Examples: Consul, etcd, ZooKeeper

---

## Intermediate Questions

### 4. How do you handle service registry failures?
**Q**: Registry is a single point of failure. How to mitigate?

**A**:
- **Replication**: Multiple registry nodes (Raft/Paxos)
- **Client caching**: Cache last-known-good locations
- **Fallback**: DNS or config-based backup
- **Self-healing**: Auto-recovery and re-registration

---

### 5. How do health checks work?
**Q**: How does the registry know a service is down?

**A**: Two approaches:
- **Active (pull)**: Registry pings `/health` endpoint
- **Passive (push)**: Service sends heartbeats

On failure:
- Mark unhealthy after N consecutive failures
- Remove after TTL without heartbeat
- Alert monitoring system

---

### 6. DNS vs dedicated service discovery?
**Q**: When to use DNS-based discovery?

**A**:
- **DNS**: Simple, universal support, good for stable services
- **Dedicated**: Dynamic, health-aware, better for microservices

DNS limitations:
- TTL caching causes stale entries
- No health checking
- Limited load balancing

---

## How to Explain in 30 Seconds

"Service discovery solves the problem of finding services in dynamic environments where IPs change frequently. Services register themselves with a registry on startup, and clients query the registry to find healthy instances. There are two patterns: client-side where the client queries directly and does load balancing, and server-side where a load balancer handles discovery. Health checks ensure only healthy instances are returned, and TTL-based deregistration handles crashed services. Common implementations include Consul, Eureka, and Kubernetes DNS."
