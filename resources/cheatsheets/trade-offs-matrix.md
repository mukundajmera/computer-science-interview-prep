# ⚖️ Trade-offs Matrix

Common design trade-offs and when to choose each option.

---

## 📋 How to Use This Guide

In system design interviews, discussing trade-offs is crucial. For each decision:
1. **State both options** clearly
2. **Explain pros and cons** of each
3. **Choose one** based on requirements
4. **Justify** your choice

---

## 1. Consistency vs Availability (CAP Theorem)

### The Trade-off

In a distributed system with network partitions, you can only guarantee **Consistency** OR **Availability**, not both.

| Aspect | CP (Consistency) | AP (Availability) |
|--------|------------------|-------------------|
| **Behavior during partition** | Reject requests to maintain consistency | Serve requests, may return stale data |
| **Data guarantee** | All nodes see same data | Data may be temporarily inconsistent |
| **User experience** | May see errors | Always get a response |

### When to Choose

| Choose CP When | Choose AP When |
|----------------|----------------|
| Financial transactions | Social media feeds |
| Inventory management | User sessions |
| Booking systems | Cache data |
| Medical records | Analytics/metrics |
| Anything with money | Content delivery |

### Real-World Examples

| System | Choice | Reasoning |
|--------|--------|-----------|
| **Banking** | CP | Money can't be inconsistent |
| **Twitter Timeline** | AP | Slightly stale feed is acceptable |
| **MongoDB** | CP | Strong consistency mode |
| **Cassandra** | AP | High availability priority |
| **DynamoDB** | Configurable | Choose per use case |

### Interview Phrases

> "For a banking system, I'd choose consistency over availability because incorrect balances could lead to financial losses."

> "For a social media feed, availability is more important—users expect a response even if it's slightly stale."

---

## 2. SQL vs NoSQL

### The Trade-off

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| **Schema** | Fixed, predefined | Flexible, dynamic |
| **Scaling** | Vertical (scale up) | Horizontal (scale out) |
| **Queries** | Complex JOINs, aggregations | Simple lookups, limited joins |
| **Transactions** | ACID guaranteed | Usually eventual consistency |
| **Data model** | Relational tables | Document, key-value, wide-column, graph |

### When to Choose

| Choose SQL When | Choose NoSQL When |
|-----------------|-------------------|
| Data has clear relationships | Schema evolves frequently |
| Need complex queries | Simple access patterns |
| ACID transactions required | High write throughput |
| Data integrity critical | Need horizontal scaling |
| Known, stable schema | Unstructured or semi-structured data |

### Decision by Use Case

| Use Case | Recommendation | Reasoning |
|----------|----------------|-----------|
| E-commerce orders | SQL (PostgreSQL) | Transactions, relationships |
| User profiles | NoSQL (MongoDB) | Flexible schema, simple access |
| Session storage | NoSQL (Redis) | Simple key-value, fast |
| Analytics logs | NoSQL (Cassandra) | High write volume, time-series |
| Social graph | Graph DB (Neo4j) | Relationship-heavy queries |
| Real-time leaderboard | NoSQL (Redis) | Sorted sets, fast reads |

### Interview Phrases

> "I'd choose PostgreSQL here because we need ACID transactions for order processing and complex queries for inventory management."

> "For storing user activity logs, Cassandra makes sense due to the high write volume and time-series nature of the data."

---

## 3. Synchronous vs Asynchronous Communication

### The Trade-off

| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **Response** | Wait for completion | Return immediately |
| **Coupling** | Tight (caller blocked) | Loose (fire and forget) |
| **Latency** | Higher (wait for all) | Lower (immediate response) |
| **Reliability** | Simpler error handling | Need retry mechanisms |
| **Complexity** | Lower | Higher (message queues, eventual consistency) |

### When to Choose

| Choose Sync When | Choose Async When |
|------------------|-------------------|
| Need immediate response | Can process later |
| Simple request-response | Heavy processing |
| Low latency critical | Need to decouple services |
| Must know result immediately | Handle traffic spikes |
| User waits for result | Fire-and-forget acceptable |

### Real-World Examples

| Operation | Pattern | Reasoning |
|-----------|---------|-----------|
| **User login** | Sync | User needs immediate result |
| **Send email** | Async | User doesn't wait for delivery |
| **Place order** | Sync | User needs confirmation |
| **Video transcoding** | Async | Takes minutes, user notified later |
| **Payment processing** | Sync | User waits for confirmation |
| **Report generation** | Async | Takes time, email when done |

### Interview Phrases

> "Sending emails should be asynchronous because users shouldn't wait for email delivery, and it allows us to handle failures with retries."

> "Order placement should be synchronous so users get immediate confirmation and can see their order status."

---

## 4. Monolith vs Microservices

### The Trade-off

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| **Deployment** | Single unit | Independent services |
| **Complexity** | Lower initial | Higher operational |
| **Scaling** | Scale entire app | Scale individual services |
| **Development** | Simpler for small teams | Better for large teams |
| **Data consistency** | Easy (single DB) | Harder (distributed) |
| **Debugging** | Easier | Harder (distributed tracing) |

### When to Choose

| Choose Monolith When | Choose Microservices When |
|----------------------|---------------------------|
| Small team (< 10) | Large team (10+) |
| Early stage startup | Scaling proven product |
| Simple domain | Complex, diverse domains |
| Need to move fast | Need independent scaling |
| Unclear boundaries | Clear service boundaries |

### Migration Path

```
Start with Monolith → Identify boundaries → Extract services gradually
```

### Interview Phrases

> "For a startup, I'd recommend starting with a monolith to move fast, with clear module boundaries that make future extraction easier."

> "Given the team size and distinct domains, microservices would allow independent deployment and scaling of each service."

---

## 5. Vertical vs Horizontal Scaling

### The Trade-off

| Aspect | Vertical (Scale Up) | Horizontal (Scale Out) |
|--------|---------------------|------------------------|
| **How** | Bigger machine | More machines |
| **Limit** | Hardware limits | Theoretically unlimited |
| **Complexity** | Lower | Higher (distributed) |
| **Cost** | Expensive at high end | Linear cost |
| **Downtime** | Usually required | Rolling updates possible |
| **State management** | Simple | Need external storage |

### When to Choose

| Choose Vertical When | Choose Horizontal When |
|----------------------|------------------------|
| Initial scaling | Beyond single machine limits |
| Database primary | Stateless application servers |
| Simple architecture | High availability required |
| Predictable load | Variable traffic |
| Legacy applications | Modern cloud-native apps |

### Interview Phrases

> "For the application servers, we should scale horizontally behind a load balancer for high availability and to handle variable traffic."

> "For the database, we'll start with vertical scaling until we hit limits, then implement sharding for horizontal scaling."

---

## 6. Push vs Pull Model

### The Trade-off

| Aspect | Push (Fan-out on Write) | Pull (Fan-out on Read) |
|--------|-------------------------|------------------------|
| **When work happens** | At write time | At read time |
| **Read latency** | Low (pre-computed) | Higher (computed on demand) |
| **Write latency** | Higher (fan-out) | Low (just store) |
| **Storage** | More (copies per user) | Less (single copy) |
| **Stale data risk** | Lower | Higher |

### When to Choose

| Choose Push When | Choose Pull When |
|------------------|------------------|
| Read-heavy | Write-heavy |
| Need low read latency | Storage is limited |
| Users have similar content | Content is highly personalized |
| Moderate number of followers | Celebrity problem (millions of followers) |

### Real-World Examples

| System | Approach | Reasoning |
|--------|----------|-----------|
| **Twitter (normal users)** | Push | Pre-compute timeline for fast reads |
| **Twitter (celebrities)** | Pull | Too expensive to push to millions |
| **CDN cache** | Pull then cache | Content fetched on first request |
| **Notifications** | Push | Send immediately when event occurs |

### Interview Phrases

> "For regular users with <10K followers, we'll use push to pre-compute timelines. For celebrities with millions of followers, we'll fetch their tweets at read time."

---

## 7. Client-side vs Server-side Rendering

### The Trade-off

| Aspect | Client-side (CSR) | Server-side (SSR) |
|--------|-------------------|-------------------|
| **Initial load** | Slower (download JS first) | Faster (HTML ready) |
| **SEO** | Poor (without SSR) | Good (content in HTML) |
| **Server load** | Lower (client does work) | Higher (server renders) |
| **Interactivity** | Fast after load | Page reloads needed |
| **Complexity** | Frontend heavy | Full-stack |

### When to Choose

| Choose CSR When | Choose SSR When |
|-----------------|-----------------|
| SPA with rich interactions | SEO critical (blog, e-commerce) |
| Internal tools | First page load performance critical |
| Authenticated content only | Static or semi-static content |
| Mobile-app-like experience | Wide device support needed |

### Hybrid Approaches

- **Static Site Generation (SSG)**: Pre-render at build time
- **Incremental Static Regeneration (ISR)**: Static with periodic updates
- **Partial Hydration**: SSR + selective client-side enhancement

---

## 8. Strong vs Eventual Consistency

### The Trade-off

| Aspect | Strong Consistency | Eventual Consistency |
|--------|-------------------|---------------------|
| **Guarantee** | All reads see latest write | Reads may see older data |
| **Latency** | Higher (wait for confirmation) | Lower (immediate return) |
| **Availability** | Lower during partitions | Higher during partitions |
| **Implementation** | Synchronous replication | Asynchronous replication |

### When to Choose

| Choose Strong When | Choose Eventual When |
|--------------------|---------------------|
| Financial transactions | Social media content |
| Inventory counts | User preferences |
| Booking systems | Analytics data |
| Primary database writes | Read replicas |
| Critical data | Cache layers |

### Interview Phrases

> "For the shopping cart, eventual consistency is fine—users can refresh to see updates."

> "For inventory during checkout, we need strong consistency to prevent overselling."

---

## 9. Caching Strategy Comparison

### The Trade-off

| Strategy | How It Works | Use When |
|----------|--------------|----------|
| **Cache-Aside** | App checks cache, falls back to DB | General purpose, read-heavy |
| **Write-Through** | Write to cache + DB together | Need strong consistency |
| **Write-Behind** | Write to cache, async to DB | Write-heavy, can lose data |
| **Read-Through** | Cache automatically fetches from DB | Simplify application logic |

### Decision Matrix

| Requirement | Recommended Strategy |
|-------------|---------------------|
| Simple implementation | Cache-Aside |
| Strong consistency | Write-Through |
| High write throughput | Write-Behind |
| Application simplicity | Read-Through |

---

## 10. Sharding Strategy Comparison

### The Trade-off

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Range-based** | Shard by data range | Easy to understand | Hotspots possible |
| **Hash-based** | Hash key to shard | Even distribution | Range queries hard |
| **Directory-based** | Lookup service | Flexible | Extra hop |
| **Geo-based** | By region | Low latency | Uneven data |

### When to Choose

| Choose Range When | Choose Hash When |
|-------------------|------------------|
| Need range queries | Need even distribution |
| Time-series data | Random access patterns |
| Data naturally ranges | No range queries needed |

---

## 📊 Quick Reference Card

### For the Interview

| Trade-off | Question to Ask |
|-----------|-----------------|
| Consistency vs Availability | "Can we tolerate stale data?" |
| SQL vs NoSQL | "What's the access pattern?" |
| Sync vs Async | "Does user need immediate result?" |
| Push vs Pull | "Read-heavy or write-heavy?" |
| Scale Up vs Out | "What's the expected growth?" |

### Standard Answers

| System Type | Standard Trade-offs |
|-------------|---------------------|
| Social Media | AP, NoSQL for feeds, Push for timeline |
| E-commerce | CP for orders, SQL for transactions |
| Chat | AP, NoSQL for messages, WebSocket |
| Analytics | AP, eventual consistency, NoSQL |
| Banking | CP, SQL, strong consistency |

---

## 🔗 Related Resources

- [CONCEPTS.md](../../CONCEPTS.md#cap-theorem) - CAP Theorem details
- [hld-components-map.md](hld-components-map.md) - Component selection
- [04-hld-projects/](../../04-hld-projects/) - See trade-offs in action

---

*Discussing trade-offs shows depth of understanding. Always justify your choices! ⚖️*
