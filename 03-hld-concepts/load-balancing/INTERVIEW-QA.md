# Interview Questions: Load Balancing

## Basic Questions

### 1. What is load balancing and why is it important?
**Q**: Explain load balancing and its importance in distributed systems.

**A**: Load balancing distributes incoming network traffic across multiple servers to:

- **Prevent overload**: No single server becomes a bottleneck
- **Increase availability**: If one server fails, others handle traffic
- **Improve performance**: Requests routed to healthiest/fastest server
- **Enable scaling**: Add/remove servers transparently

**Example**: An e-commerce site receiving 50,000 requests/second uses a load balancer to distribute traffic across 10 servers, each handling 5,000 requests/second.

---

### 2. What are the main load balancing algorithms?
**Q**: Describe common load balancing algorithms and when to use each.

**A**:

| Algorithm | How it Works | Best For |
|-----------|--------------|----------|
| **Round Robin** | Rotates through servers sequentially | Homogeneous servers, stateless requests |
| **Weighted Round Robin** | Round robin with server weights | Servers with different capacities |
| **Least Connections** | Routes to server with fewest active connections | Long-lived connections, varying request times |
| **Least Response Time** | Routes to fastest responding server | When response time varies significantly |
| **IP Hash** | Hash of client IP determines server | Session persistence without state |
| **Random** | Randomly selects a server | Simple, good enough for many cases |

---

### 3. What is the difference between Layer 4 and Layer 7 load balancing?
**Q**: Explain Layer 4 vs Layer 7 load balancing.

**A**:

| Aspect | Layer 4 (Transport) | Layer 7 (Application) |
|--------|---------------------|----------------------|
| **Operates on** | TCP/UDP packets | HTTP/HTTPS requests |
| **Can inspect** | IP address, port | URL, headers, cookies, body |
| **Routing decisions** | Source/dest IP and port | Content-based (path, host, headers) |
| **Performance** | Faster, less CPU | Slower, more CPU |
| **Features** | Basic | SSL termination, caching, compression |
| **Use case** | High throughput, simple routing | Content routing, A/B testing |

**Example**:
- Layer 4: Route all TCP port 443 traffic to backend pool
- Layer 7: Route `/api/*` to API servers, `/static/*` to CDN

---

### 4. What are health checks and why are they important?
**Q**: How do load balancers determine if a backend server is healthy?

**A**: Health checks verify backend server availability:

**Types:**
1. **Active checks**: LB periodically sends probe requests
   - HTTP GET /health → expect 200 OK
   - TCP connection check
   - Custom health endpoint

2. **Passive checks**: LB monitors actual traffic responses
   - Track error rates, timeouts
   - Mark unhealthy if errors exceed threshold

**Configuration parameters:**
- **Interval**: How often to check (e.g., every 5 seconds)
- **Timeout**: Max wait for response (e.g., 3 seconds)
- **Threshold**: Failures before marking unhealthy (e.g., 3 consecutive failures)
- **Recovery**: Successes before marking healthy again

---

### 5. What is session persistence (sticky sessions)?
**Q**: Explain sticky sessions and when you would use them.

**A**: Session persistence ensures a client's requests always go to the same backend server.

**Methods:**
1. **Source IP**: Hash client IP to determine server
2. **Cookie-based**: LB inserts/reads routing cookie
3. **URL parameter**: Encode server ID in URL

**When to use:**
- Server stores session state in memory
- Shopping carts, user preferences
- Legacy applications

**When to avoid:**
- Prefer stateless design
- Store sessions in Redis/database
- Use JWT tokens

---

## Intermediate Questions

### 1. How would you handle load balancer as a single point of failure?
**Q**: The load balancer itself can fail. How do you make it highly available?

**A**: Multiple strategies for LB redundancy:

**1. Active-Passive (Failover)**
```
┌─────────────┐    Heartbeat    ┌─────────────┐
│  Primary    │◄───────────────►│  Secondary  │
│     LB      │                 │     LB      │
│  (Active)   │                 │ (Standby)   │
└──────┬──────┘                 └──────┬──────┘
       │                               │
       │ Virtual IP floats to active LB
       ▼
   ┌───────┐
   │ VIP   │ ← Clients connect here
   └───────┘
```

**2. Active-Active**
- Multiple LBs share traffic
- DNS returns multiple LB IPs
- More complex state synchronization

**3. Cloud-native solutions**
- AWS ELB: Managed, automatically scales
- Anycast: Same IP announced from multiple locations
- Global load balancing: Route to nearest healthy LB

---

### 2. How do you scale a load balancer itself?
**Q**: What happens when your load balancer becomes the bottleneck?

**A**: **Scale the load balancer layer:**

**1. Horizontal scaling**
- Deploy multiple LB instances
- Use DNS round robin to distribute across LBs
- Each LB manages a subset of traffic

**2. Layer 4 in front of Layer 7**
```
               ┌─────────────┐
               │   DNS       │
               └──────┬──────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐
     │  L4 LB  │ │  L4 LB  │ │  L4 LB  │  (Fast, cheap)
     └────┬────┘ └────┬────┘ └────┬────┘
          └───────────┼───────────┘
                      ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐
     │  L7 LB  │ │  L7 LB  │ │  L7 LB  │  (Smart routing)
     └─────────┘ └─────────┘ └─────────┘
```

**3. Connection optimization**
- Keep-alive connections to backends
- Connection pooling
- TCP multiplexing

---

### 3. How do you handle SSL/TLS with load balancing?
**Q**: Where should SSL termination happen?

**A**: **Options for SSL handling:**

**1. SSL Termination at LB (most common)**
```
Client ──HTTPS──► LB ──HTTP──► Backend
```
- LB handles encryption/decryption
- Backends receive plain HTTP
- Pros: Offloads CPU from backends, centralized cert management
- Cons: Traffic unencrypted internally

**2. SSL Passthrough**
```
Client ──HTTPS──► LB ──HTTPS──► Backend
```
- LB forwards encrypted traffic
- Backend handles SSL
- Pros: End-to-end encryption
- Cons: No content inspection, backends need certs

**3. SSL Re-encryption**
```
Client ──HTTPS──► LB ──HTTPS──► Backend
                 (decrypt/re-encrypt)
```
- LB terminates and re-encrypts
- Pros: Content inspection + internal encryption
- Cons: Double encryption overhead

---

### 4. How would you implement zero-downtime deployments with a load balancer?
**Q**: How do you deploy new code without dropping requests?

**A**: **Rolling deployment with load balancer:**

```
Phase 1: Remove server from LB pool
┌──────┐     ┌──────┐     ┌──────┐
│  S1  │     │  S2  │     │  S3  │
│  v1  │ ←── │  v1  │ ←── │  v1  │
└──────┘     └──────┘     └──────┘
   ▲            ▲            ▲
   │            │            │
   └────────────┴────────────┘
              │
         ┌────┴────┐
         │   LB    │
         └─────────┘

Phase 2: Deploy new version, health check passes
┌──────┐     ┌──────┐     ┌──────┐
│  S1  │     │  S2  │     │  S3  │
│  v2  │ ✓   │  v1  │     │  v1  │
└──────┘     └──────┘     └──────┘

Phase 3: Repeat for all servers
┌──────┐     ┌──────┐     ┌──────┐
│  S1  │     │  S2  │     │  S3  │
│  v2  │ ✓   │  v2  │ ✓   │  v2  │ ✓
└──────┘     └──────┘     └──────┘
```

**Key techniques:**
- **Connection draining**: Wait for active requests to complete
- **Health check delay**: New version must pass health checks
- **Canary release**: Route small % of traffic to new version first

---

### 5. What's the difference between client-side and server-side load balancing?
**Q**: Compare client-side vs server-side load balancing.

**A**:

**Server-side (Traditional)**
```
Client → Load Balancer → Backend Server
```
- LB is a separate infrastructure component
- Client unaware of backend servers
- Centralized control

**Client-side**
```
Client → (client discovers servers) → Backend Server
```
- Client knows all available servers
- Client makes routing decision
- Used in microservices (Netflix Ribbon, gRPC)

| Aspect | Server-side | Client-side |
|--------|-------------|-------------|
| **Discovery** | LB manages pool | Client queries registry |
| **Failure** | LB is SPOF | No central SPOF |
| **Latency** | Extra hop | Direct connection |
| **Complexity** | Simpler clients | Complex client logic |
| **Use case** | External traffic | Internal service-to-service |

---

## Advanced Questions

### 1. Design a global load balancing system
**Q**: How would you distribute traffic across multiple data centers worldwide?

**A**: **Global Server Load Balancing (GSLB)**

```
                       ┌─────────────────────┐
                       │     DNS Server      │
                       │   (Geo-aware)       │
                       └──────────┬──────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
    ┌───────────┐           ┌───────────┐           ┌───────────┐
    │  US-East  │           │  EU-West  │           │  Asia     │
    │   Region  │           │   Region  │           │   Region  │
    │           │           │           │           │           │
    │ ┌───────┐ │           │ ┌───────┐ │           │ ┌───────┐ │
    │ │  LB   │ │           │ │  LB   │ │           │ │  LB   │ │
    │ └───────┘ │           │ └───────┘ │           │ └───────┘ │
    └───────────┘           └───────────┘           └───────────┘
```

**Routing strategies:**
1. **Geo-proximity**: Route to nearest data center
2. **Latency-based**: Route to lowest latency option
3. **Weighted**: Split traffic by percentage
4. **Failover**: Primary region with backup

**Components:**
- **Anycast DNS**: Same IP advertised from multiple locations
- **Health monitoring**: Cross-region health checks
- **Traffic managers**: AWS Route 53, Cloudflare, Akamai

---

### 2. How would you implement consistent hashing for load balancing?
**Q**: Explain how consistent hashing improves load balancing for sticky sessions.

**A**: **Consistent hashing** minimizes redistribution when servers change.

**Traditional hashing problem:**
```
server = hash(request) % num_servers

If num_servers changes from 3 to 4:
- hash("user1") % 3 = 2 → hash("user1") % 4 = 1  ← Different server!
- Most requests get remapped
```

**Consistent hashing solution:**
```
              0/360°
               │
        ┌──────┴──────┐
       S1             S2
       │               │
       │    user1 ●    │
       │               │
       S4─────────────S3
             180°

user1 → clockwise → S2
```

**Virtual nodes** improve distribution:
```
S1 at positions: 30°, 120°, 240°
S2 at positions: 60°, 180°, 300°
S3 at positions: 90°, 210°, 330°
```

**When server removed:**
- Only keys between removed server and previous server move
- ~1/n keys affected instead of all

---

### 3. How do you handle WebSocket connections with load balancing?
**Q**: WebSockets are long-lived connections. How do you load balance them?

**A**: **Challenges with WebSockets:**
- Long-lived, stateful connections
- Connection can last hours/days
- Adding new servers doesn't help existing connections

**Solutions:**

**1. Sticky sessions (connection affinity)**
```
Initial HTTP upgrade → Load Balancer → Server A
WebSocket traffic    → always to Server A
```

**2. Pub/sub for cross-server messaging**
```
┌────────┐     ┌────────┐     ┌────────┐
│ User A │     │ User B │     │ User C │
└───┬────┘     └───┬────┘     └───┬────┘
    │              │              │
┌───▼────┐     ┌───▼────┐     ┌───▼────┐
│Server 1│     │Server 2│     │Server 1│
└───┬────┘     └───┬────┘     └───┬────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
              ┌────▼────┐
              │  Redis  │
              │ Pub/Sub │
              └─────────┘
```

**3. Connection draining on scale-down**
- Gracefully close connections
- Give time for clients to reconnect to new server

---

## Common Follow-ups

- "How would you handle 1 million concurrent connections?"
- "What happens if the load balancer runs out of ports?"
- "How do you debug issues when traffic goes through a load balancer?"
- "How would you implement rate limiting at the load balancer?"
- "What metrics would you monitor for a load balancer?"

---

## Red Flags to Avoid

❌ **Don't say:**
- "Just use round robin for everything" — Shows lack of understanding of workload patterns
- "Session state should be on the server" — Poor scalability practice
- "One load balancer is enough" — Ignores HA requirements
- "Layer 4 and Layer 7 are the same" — Fundamentally different

❌ **Don't forget:**
- Health checks and their configuration
- Connection draining during deployments
- SSL/TLS handling considerations
- LB redundancy requirements

---

## How to Explain in 30 Seconds

> "Load balancing distributes traffic across multiple servers to improve availability and performance. Key decisions are: algorithm (round robin for simple cases, least connections for varying workloads), Layer 4 vs 7 (tradeoff between speed and smart routing), and session handling (prefer stateless, use external storage if needed). The load balancer itself needs redundancy through active-passive pairs or cloud-managed solutions. Health checks ensure traffic only goes to healthy servers."
