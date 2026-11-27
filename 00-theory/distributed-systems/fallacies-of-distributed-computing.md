# Fallacies of Distributed Computing

When engineers move from single-process applications to networked services, they often carry over assumptions that hold inside one machine but fail across a network. First compiled by L. Peter Deutsch and colleagues at Sun Microsystems in the 1990s, the **Eight Fallacies of Distributed Computing** name the hidden assumptions behind most production outages.

The core intuition is **partial failure**: inside one process, a call either succeeds or the whole process crashes. Across a network, a request can be lost, delayed, executed twice, or left in an unknown state while both caller and callee remain alive.

> Executable walkthroughs for all eight fallacies are available in [Python](./code/python/fallacies/fallacies_demo.py) and [Java](./code/java/fallacies/FallaciesDemo.java).

## The Eight Fallacies

### 1. The network is reliable
Packets are dropped by congested switches, NICs fail, fiber is cut, and asymmetric partitions drop responses while requests succeed.
- **Concrete failure:** A payment service charges a customer's card, but the response packet is dropped; the caller times out and retries, double-charging the customer.
- **Mitigation:** Set bounded timeouts on every call, retry only with exponential backoff and jitter, and enforce **idempotency keys** on mutating endpoints.

### 2. Latency is zero
An L1 cache read takes ~1 ns and an in-process call takes nanoseconds, whereas a cross-datacenter round trip takes 1–100+ ms.
- **Concrete failure:** An API gateway loops over 50 cart items and makes one RPC per item (the N+1 RPC problem), turning a 10 ms call into a 500 ms tail-latency bottleneck.
- **Mitigation:** Design coarse-grained batch APIs, push static and read-heavy data to CDNs and edge caches, and colocate chatty services in the same availability zone.

### 3. Bandwidth is infinite
Links saturate during traffic spikes, cache cold starts, or large fan-out broadcasts, causing queuing delay and packet drops.
- **Concrete failure:** A service serializes full 2 MB JSON user profiles on every internal lookup; during a flash sale, East-West network saturation starves health checks and triggers cascading failovers.
- **Mitigation:** Use compact binary encodings (Protobuf, Avro), compress payloads, paginate responses, and send deltas rather than full snapshots.

### 4. The network is secure
Even internal VPC networks are vulnerable to compromised containers, misconfigured security groups, BGP hijacking, and lateral movement.
- **Concrete failure:** An unencrypted internal admin RPC is exposed via a misconfigured ingress rule, allowing an attacker to spoof requests and exfiltrate session tokens.
- **Mitigation:** Adopt zero-trust networking: enforce mutual TLS (mTLS) between services, rotate short-lived credentials, and authorize every request at the service boundary.

### 5. Topology doesn't change
Auto-scaling, rolling deployments, spot-instance evictions, and availability-zone failovers constantly replace hosts and IP addresses.
- **Concrete failure:** A worker service caches a database primary's IP address indefinitely; after an automated failover promotes a replica at a new IP, writes fail until the workers are manually restarted.
- **Mitigation:** Never hardcode IPs; route through service discovery, DNS with short TTLs, or L4/L7 load balancers backed by active health checks.

### 6. There is one administrator
Modern systems span internal product teams, platform teams, cloud providers, and third-party APIs with independent deployment schedules and priorities.
- **Concrete failure:** A partner shipping API rolls out a breaking schema change or enters maintenance without notice, blocking your checkout flow because you call it synchronously.
- **Mitigation:** Isolate external dependencies behind circuit breakers, bulkheads, strict schema versioning, and asynchronous queues with fallback behavior.

### 7. Transport cost is zero
Every network hop consumes CPU for serialization, TLS handshakes, and kernel socket copies, plus direct cloud billing for cross-AZ and internet egress.
- **Concrete failure:** Replicating verbose audit logs synchronously across three cloud regions generates six-figure monthly cross-region egress charges and consumes 30% of application CPU in JSON parsing.
- **Mitigation:** Account for egress pricing in topology design, keep high-chatter traffic within a single AZ where fault tolerance permits, and batch/compress cross-region replication.

### 8. The network is homogeneous
Production fleets mix Linux distributions, CPU architectures (x86 and ARM), mobile clients on lossy 4G, and polyglot services in Java, Go, and Python.
- **Concrete failure:** A Java service serializes objects using native Java serialization; a new Go consumer cannot deserialize the payload, and endianness/encoding bugs corrupt binary fields.
- **Mitigation:** Standardize on language-agnostic protocols (HTTP/2, gRPC) and explicit schemas (Protobuf, JSON Schema) with backward-compatible evolution rules.

## Worked Example: Compounding Fallacies in an Order Checkout

Trace a single user clicking **Place Order** (`API Gateway -> Order Service -> Inventory Service -> External Payment API`):

1. **N+1 calls (Fallacies 2 & 3):** Order Service fetches 20 SKU records one by one from Inventory Service (20 round trips, 20x header overhead) instead of one batched `GetItems(sku_ids)` call.
2. **Hardcoded endpoint (Fallacy 5):** Inventory Service scales down an old pod; a stale IP in Order Service causes a 5-second connect timeout.
3. **Ambiguous timeout (Fallacies 1 & 6):** Order Service calls the third-party Payment API, which captures the funds but stalls before replying. Order Service times out at 3 seconds and retries without an idempotency key, charging the card twice.

Fixing this flow requires batching the inventory read, routing via load-balanced service discovery, wrapping the external payment call in a circuit breaker, and attaching a deterministic `order_id` idempotency key.

## Failure Cases

- **Retry storms (metastable failure):** When a downstream service slows down, aggressive client retries multiply traffic 3–5x, keeping the service pinned in overload even after the root cause clears.
- **Split-brain from unreliable health checks:** Treating a dropped heartbeat as proof of node death (Fallacy 1) can promote a second primary while the original is still accepting writes.
- **Hidden cross-AZ egress:** Multi-AZ Kafka or microservice meshes that route every RPC to a random zone double network latency and incur per-GB cross-AZ transfer fees (Fallacy 7).

## Trade-offs

| Mitigation | Benefit | Cost / Trade-off |
| :--- | :--- | :--- |
| Retries + idempotency keys | Recovers from transient drops | Extra storage/TTL for deduplication state |
| Coarse-grained batch APIs | Cuts round trips and latency | Harder caching, larger single-request payloads |
| mTLS everywhere | Blocks eavesdropping and spoofing | Certificate rotation complexity, handshake CPU |
| Circuit breakers + fallbacks | Prevents cascading outages | Temporary degraded UX or stale fallback data |
| Zone-aware routing | Cuts latency and cross-AZ egress | Uneven load if one AZ has fewer healthy replicas |

## Interview Traps

- **Treating RPC like a local function call:** Hiding network calls behind transparent proxies encourages chatty loops and obscures failure modes.
- **Assuming a timeout means the operation failed:** A timeout only means you did not receive a reply; the server may have already committed the write.
- **Retrying blindly without backoff or jitter:** Synchronized retries from thousands of clients create thundering herds that prolong outages.
- **Ignoring Fallacy 6 in microservice designs:** Saying "we'll just coordinate a simultaneous deployment across five teams" fails in real organizations; contracts must be backward-compatible.

## Self-Check Questions

1. Why does an HTTP timeout from a payment provider require an idempotency key before retrying?
2. How can "Latency is zero" and "Bandwidth is infinite" interact to cause an outage during a cache flush?
3. What is the difference between a retry storm and a normal traffic spike, and which two client-side controls stop it?
4. Why does multi-AZ deployment directly surface Fallacy 7 (transport cost is zero), and how does zone-aware routing mitigate it?

## Conclusion

Ignoring these fallacies produces systems that pass local tests yet fail unpredictably under real network conditions. Designing explicitly for partial failure, non-zero latency, dynamic topology, and independent administrative domains is the foundation of resilient distributed architecture.
