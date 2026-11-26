# Distributed Unique ID - Interview Q&A

This document contains 10 rigorous interview Q&As for the Distributed Unique ID generator (Snowflake pattern), covering napkin math, trade-offs, and failure mode mitigations.

### Q1: Why not just use `AUTO_INCREMENT` in a relational database?
**A:** `AUTO_INCREMENT` works perfectly for single-node databases, ensuring strict monotonically increasing IDs. However, in a distributed system with high write throughput, a single database becomes a bottleneck and a Single Point of Failure (SPOF). While multi-master replication with offset/step (e.g., Master 1 generates 1, 3, 5; Master 2 generates 2, 4, 6) can scale writes slightly, it is notoriously hard to scale out dynamically (adding Master 3 requires complex reconfiguration) and IDs are not perfectly time-sortable across the fleet.

### Q2: Why are UUIDv4s considered harmful as primary keys in relational databases?
**A:** UUIDv4s are 128-bit completely random strings. When used as a Primary Key in a database like MySQL (InnoDB) or PostgreSQL, they cause massive B-Tree index fragmentation. Because they are inserted randomly rather than sequentially, the database constantly has to split index pages and perform heavy disk I/O. Furthermore, secondary indexes usually store the primary key, so a 128-bit PK significantly inflates the storage footprint across the entire database compared to a 64-bit Snowflake ID.

### Q3: Explain the 64-bit layout of a Snowflake ID and calculate its longevity.
**A:** The standard layout is:
- **1 bit:** Sign bit, kept at `0` so the ID is always positive.
- **41 bits:** Timestamp in milliseconds since a custom epoch.
- **10 bits:** Node/Machine ID (often split into 5-bit Datacenter ID and 5-bit Worker ID).
- **12 bits:** Sequence number for concurrent generation within the same millisecond.

**Napkin Math for longevity:** $2^{41}$ milliseconds $\approx 2.199 \times 10^{12}$ ms. Dividing by $(1000 \times 60 \times 60 \times 24 \times 365.25)$ yields exactly 69.73 years. This longevity only applies starting from the *custom epoch*, which is why we don't use the standard 1970 Unix epoch (which would exhaust the 41 bits by 2039).

### Q4: What happens if a single node receives 5,000 requests in one millisecond?
**A:** The 12-bit sequence number can hold $2^{12} = 4096$ unique values (0 to 4095). If a node tries to generate the 4097th ID in the same millisecond, the sequence counter hits its maximum bitmask limit. The application code must implement a `spin-wait` (a tight `while` loop) continuously checking the system clock until the millisecond ticks over to the next one. At that point, the sequence resets to 0, and generation resumes.

### Q5: How do you handle NTP Clock Drift, specifically when the clock moves backward?
**A:** NTP syncs can occasionally pull a server's clock backward. If we blindly use the backward timestamp, we risk generating duplicate IDs (same time, same node, same sequence). 
**Mitigation Trade-offs:**
1. **Spin-Wait:** If the drift is very small (e.g., $< 5$ms), thread-sleep until the clock catches up to the `lastTimestamp`. 
2. **Fail-Fast:** If the drift is large, throw an exception (`ClockMovedBackwardsException`) and fail the request, relying on the client/LB to retry on a different node.
3. **Borrow Worker ID:** The node requests an emergency backup Worker ID from ZooKeeper, treating itself as a newly provisioned node, bypassing the time collision.

### Q6: How do you dynamically assign Worker IDs without hardcoding them in configuration files?
**A:** Hardcoding is an anti-pattern in cloud environments (like AWS ASGs or Kubernetes) where pods/nodes are ephemeral. 
**Modern approaches:**
- **ZooKeeper/Etcd:** The node creates an ephemeral sequential znode upon startup. It reads the sequence number, applies `% 1024`, and uses that as its Worker ID. When the node dies, the session closes, and the ID is freed.
- **Kubernetes StatefulSets:** K8s assigns a stable, monotonically increasing index to each pod (e.g., `id-generator-pod-3`). The application parses its hostname at startup and uses `3` as the Worker ID.

### Q7: If you use ZooKeeper for Worker IDs, what happens if a node loses its ZooKeeper connection during generation?
**A:** The beauty of Snowflake is that generation requires zero network coordination. Once the node acquires its Worker ID at startup, it caches it locally. If ZooKeeper goes down or the node loses connection, the node can safely continue generating IDs indefinitely. The only risk is if the node crashes, restarts without ZK, and cannot re-acquire an ID.

### Q8: What is UUIDv7, and how does it compare to Snowflake?
**A:** UUIDv7 (RFC 9562) is a time-ordered UUID format that includes a 48-bit Unix timestamp at the beginning, followed by random bits. 
**Trade-offs:** 
- *Pros:* Standardized, time-sortable (avoids DB index fragmentation), and completely stateless (requires zero worker ID coordination or ZooKeeper). 
- *Cons:* It is 128-bit, meaning it takes exactly twice as much storage/memory as a 64-bit Snowflake ID, which can be significant at Twitter/Instagram scale.

### Q9: Can Snowflake IDs be guessed? Why does this matter?
**A:** Yes, they are highly guessable because the timestamp is sequential. If an attacker creates a resource and gets ID `X`, they can immediately create another resource and get `X + N`. They can then iterate and scrape IDs in between to access other users' private resources (Insecure Direct Object Reference - IDOR).
**Mitigation:** Snowflake is for internal Primary Keys. For public-facing endpoints sharing sensitive data (like Google Drive links or password reset tokens), use randomly generated strings or UUIDv4s, mapped back to the Snowflake PK in the DB.

### Q10: How would you design the Snowflake system for 100,000 requests per second across 3 regions?
**A:** $100,000$ RPS is well within Snowflake's capacity (a single node can do $4,000,000$ RPS). 
- Deploy a cluster of 3-5 lightweight stateless ID Generator microservices per region (Node.js/Go/Java) behind an internal API Gateway/Load Balancer.
- Use the 10-bit Node ID optimally: allocate 2 bits for Region (up to 4 regions), and 8 bits for Worker ID (up to 256 workers per region).
- Use local Etcd clusters in each region to assign Worker IDs. 
- The services generate IDs entirely in memory and return them via high-performance gRPC or internal REST calls in $\sim 1$ms.
