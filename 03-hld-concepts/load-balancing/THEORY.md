# Load Balancing

## What is it?

Load balancing is a technique that distributes incoming network traffic across multiple servers to ensure no single server becomes overwhelmed, improving availability, responsiveness, and reliability of applications.

## Why do we need it?

**Problem it solves**: Consider a popular e-commerce website receiving 100,000 requests per second. A single server can only handle ~10,000 requests per second.

**Without load balancing**:
- Single server becomes bottleneck
- Service unavailable during peak traffic
- No redundancy if server fails

**With load balancing**:
- Traffic distributed across 10+ servers
- Each server handles manageable load
- If one server fails, others continue serving

## Types/Approaches

### 1. By OSI Layer

```
┌─────────────────────────────────────────────────────────────┐
│                   Layer 7 (Application)                      │
│        HTTP/HTTPS, content-based routing                     │
│     Can inspect: URL, headers, cookies, body                 │
│     Example: Route /api/* to API servers                     │
├─────────────────────────────────────────────────────────────┤
│                   Layer 4 (Transport)                        │
│        TCP/UDP, IP + Port based routing                      │
│     Faster, less CPU intensive                               │
│     Cannot inspect application data                          │
└─────────────────────────────────────────────────────────────┘
```

| Aspect | Layer 4 | Layer 7 |
|--------|---------|---------|
| Speed | Faster | Slower |
| Features | Basic | Advanced (SSL, caching, compression) |
| Routing | IP/Port only | URL, headers, cookies |
| Use Case | High throughput, simple routing | Content-based routing |

### 2. Load Balancing Algorithms

#### Round Robin
```
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A  (cycle repeats)
```
**Pros**: Simple, fair distribution
**Cons**: Ignores server capacity and current load

#### Weighted Round Robin
```
Weights: A=5, B=3, C=2
Requests 1-5 → Server A
Requests 6-8 → Server B
Requests 9-10 → Server C
```
**Pros**: Accounts for different server capacities
**Cons**: Static weights, doesn't adapt to load

#### Least Connections
```
Server A: 10 active connections
Server B: 5 active connections
Server C: 15 active connections

Next request → Server B (fewest connections)
```
**Pros**: Considers current load
**Cons**: Doesn't account for request duration

#### Least Response Time
```
Server A: avg 50ms response
Server B: avg 30ms response
Server C: avg 80ms response

Next request → Server B (fastest)
```
**Pros**: Routes to healthiest server
**Cons**: Requires response time tracking

#### IP Hash
```
hash(client_ip) % num_servers = server_index

IP 1.2.3.4 → always Server A
IP 5.6.7.8 → always Server B
```
**Pros**: Session persistence without state
**Cons**: Uneven distribution if IPs cluster

#### Consistent Hashing
```
          0
         /|\
       /  |  \
     A    |    B
    /     |     \
   /      |      \
  C───────┴───────D
        180
```
**Pros**: Minimal redistribution on server changes
**Cons**: More complex, requires virtual nodes

## How it works

### Basic Architecture

```
                    ┌───────────────────────────┐
                    │         Clients           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      Load Balancer        │
                    │    (Virtual IP: VIP)      │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │ Health Check Module │  │
                    │  │ Algorithm Engine    │  │
                    │  │ Connection Pool     │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │  Server A │           │  Server B │           │  Server C │
    │ 10.0.0.1  │           │ 10.0.0.2  │           │ 10.0.0.3  │
    └───────────┘           └───────────┘           └───────────┘
```

### Health Checks

```
Load Balancer                    Server
      │                             │
      │───── Health Check ─────────►│
      │      (HTTP GET /health)     │
      │                             │
      │◄──── 200 OK ───────────────│
      │      (healthy)              │
      │                             │
      │───── Health Check ─────────►│
      │                             │
      │◄──── 503 Error ────────────│
      │      (unhealthy)            │
      │                             │
      │   [Remove from pool]        │
```

**Health check types:**
- **Active**: LB periodically pings servers
- **Passive**: LB observes response codes from real traffic

### Session Persistence (Sticky Sessions)

```
┌────────────────────────────────────────────────────────────┐
│                Methods for Session Persistence              │
├────────────────────────────────────────────────────────────┤
│  1. Source IP Hash                                          │
│     - Same client IP → Same server                          │
│     - Problem: NAT, shared IPs                              │
├────────────────────────────────────────────────────────────┤
│  2. Cookie-based                                            │
│     - LB inserts cookie: SERVERID=server-a                  │
│     - Subsequent requests routed by cookie                  │
├────────────────────────────────────────────────────────────┤
│  3. URL Parameter                                           │
│     - Append ?serverid=a to URLs                            │
│     - Works for REST APIs                                   │
└────────────────────────────────────────────────────────────┘
```

## When to use

✅ **Use load balancing when:**
- Traffic exceeds single server capacity
- High availability is required
- Scaling horizontally (adding servers)
- Geographic distribution needed
- Zero-downtime deployments

**Specific scenarios:**
- Web applications with multiple app servers
- Microservices with multiple instances
- Database read replicas
- API gateways distributing to backends

## When NOT to use

❌ **Avoid or reconsider when:**
- Single server handles all traffic easily
- Application requires strong session affinity that can't be externalized
- Cost of LB infrastructure exceeds benefits
- Stateful connections that can't be distributed (some WebSocket cases)

**Consider alternatives:**
- DNS round robin for simple cases
- Client-side load balancing for service meshes
- CDN for static content

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Availability** | No single point of failure (if LB is redundant) | LB itself can be SPOF |
| **Scalability** | Easy horizontal scaling | Added network hop latency |
| **Complexity** | Abstracted from clients | More infrastructure to manage |
| **Cost** | Better resource utilization | LB hardware/software costs |
| **Consistency** | N/A | Session management complexity |

## Real-world examples

### AWS (Elastic Load Balancing)
- **ALB (Application)**: Layer 7, HTTP/HTTPS, path-based routing
- **NLB (Network)**: Layer 4, ultra-low latency, millions of requests/sec
- **CLB (Classic)**: Legacy, both Layer 4 and 7

### Google Cloud Load Balancing
- Global load balancing across regions
- Anycast IP for automatic routing to nearest region
- Integration with CDN

### Netflix
- Zuul for edge routing
- Ribbon for client-side load balancing
- Custom algorithms for A/B testing

### Nginx/HAProxy
- Open-source, widely used
- Nginx: Event-driven, high performance
- HAProxy: Feature-rich, Layer 4/7

## Complexity Analysis

| Operation | Time Complexity |
|-----------|-----------------|
| Round Robin | O(1) |
| Weighted Round Robin | O(1) |
| Least Connections | O(n) or O(log n) with heap |
| IP Hash | O(1) |
| Consistent Hashing | O(log n) with sorted ring |

## Common Problems and Solutions

### 1. Load Balancer as Single Point of Failure
**Problem**: LB fails, entire system down
**Solutions**:
- Active-passive LB pair with heartbeat
- Anycast routing with multiple LBs
- DNS failover between LBs

### 2. Uneven Load Distribution
**Problem**: Some servers overloaded while others idle
**Solutions**:
- Use weighted algorithms
- Implement least connections
- Add health check feedback

### 3. Session Persistence with Scaling
**Problem**: Adding/removing servers breaks sessions
**Solutions**:
- Externalize session storage (Redis)
- Use consistent hashing
- JWT tokens (stateless sessions)

### 4. SSL/TLS Termination
**Problem**: High CPU usage for encryption
**Solutions**:
- SSL termination at LB
- Connection pooling to backends
- Hardware SSL accelerators

## Key Takeaways

1. **Choose the right algorithm**: Round Robin for homogeneous servers; Least Connections for varying request times

2. **Health checks are critical**: Actively monitor backend health; remove unhealthy servers quickly

3. **Plan for LB redundancy**: Load balancer itself needs high availability (active-passive or active-active)

4. **Layer 7 vs Layer 4**: Use Layer 7 for content-based routing; Layer 4 for raw performance

5. **Session handling**: Prefer stateless design; if sessions needed, externalize storage or use consistent hashing

---

## Related Concepts
- [Consistent Hashing](../consistent-hashing/) - For sticky session distribution
- [Service Discovery](../service-discovery/) - Finding backend servers
- [API Gateway](../api-gateway/) - Often includes load balancing
