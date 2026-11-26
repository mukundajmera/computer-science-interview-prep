# Interview Questions: Distributed Coordination (ZooKeeper)

## Basic Questions

### 1. What is ZooKeeper and what problems does it solve?

**A**: ZooKeeper is a centralized coordination service for distributed systems, providing primitives for leader election, distributed locks, configuration management, and service discovery.

**Problems solved:**
- **Leader election**: Automated failover in distributed systems
- **Distributed locks**: Mutual exclusion across nodes
- **Configuration**: Dynamic config updates without restarts
- **Service discovery**: Track available service instances

**Not for:** Primary data storage, high-throughput messaging, low-latency caching

---

### 2. Explain ZNode types

**A**:
- **Persistent**: Remains until explicitly deleted
- **Ephemeral**: Deleted when client session ends
- **Sequential**: Appends monotonically increasing counter
- **Persistent Sequential**: Persistent + sequential
- **Ephemeral Sequential**: Ephemeral + sequential (leader election)

**Example:**
```java
// Ephemeral sequential for leader election
zk.create("/election/candidate-", data,
          OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
// Creates: /election/candidate-0000000001
```

---

### 3. How does leader election work in ZooKeeper?

**A**:
1. Each candidate creates ephemeral sequential ZNode
2. Candidate with lowest sequence number becomes leader
3. Others watch the node before them
4. When leader fails, its ephemeral node deleted
5. Next candidate becomes leader

**Prevents herd effect**: Each node only watches one predecessor

---

### 4. What are watches in ZooKeeper?

**A**: Watches are one-time triggers for ZNode changes.

```java
// Set watch
zk.getData("/config", event -> {
    System.out.println("Config changed!");
    // Must re-register watch for continuous monitoring
    zk.getData("/config", this, null);
}, null);
```

**Types:**
- Data change
- Children change
- Node created/deleted

**Important**: Watches fire once, must be re-registered

---

### 5. What is the ZAB protocol?

**A**: ZooKeeper Atomic Broadcast ensures linearizable consistency:

1. Write request sent to leader
2. Leader proposes to followers
3. Quorum (majority) acknowledges
4. Leader commits and notifies followers
5. Response sent to client

**Quorum**: 2f+1 nodes tolerate f failures
- 3 nodes: 1 failure
- 5 nodes: 2 failures

---

## Intermediate Questions

### 1. How would you implement a distributed lock?

**A**:
```java
public class DistributedLock {
    private ZooKeeper zk;
    private String lockPath;
    private String currentLock;

    public void acquire() throws Exception {
        // Create ephemeral sequential node
        currentLock = zk.create("/locks/lock-", new byte[]{},
                               OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);

        while (true) {
            List<String> children = zk.getChildren("/locks", false);
            Collections.sort(children);

            if (currentLock.endsWith(children.get(0))) {
                return;  // Lock acquired
            }

            // Watch previous lock
            String previous = children.get(
                children.indexOf(currentLock.split("/")[2]) - 1
            );

            CountDownLatch latch = new CountDownLatch(1);
            if (zk.exists("/locks/" + previous, event -> latch.countDown()) != null) {
                latch.await();  // Wait for previous lock release
            }
        }
    }

    public void release() throws Exception {
        zk.delete(currentLock, -1);
    }
}
```

**Prevents herd effect**: Each waiter watches only previous lock

---

### 2. How do you implement service discovery?

**A**:
```java
// Registration
public void registerService(String serviceName, String address) throws Exception {
    String path = "/services/" + serviceName + "/instance-";
    zk.create(path, address.getBytes(),
              OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
}

// Discovery with watch
public List<String> discoverServices(String serviceName) throws Exception {
    String path = "/services/" + serviceName;
    List<String> instances = zk.getChildren(path, event -> {
        // Re-discover on change
        discoverServices(serviceName);
    });

    List<String> addresses = new ArrayList<>();
    for (String instance : instances) {
        byte[] data = zk.getData(path + "/" + instance, false, null);
        addresses.add(new String(data));
    }
    return addresses;
}
```

**Ephemeral nodes**: Auto-cleanup when service dies

---

### 3. What happens during network partition?

**A**:
**Scenario**: 5-node cluster split into 3 + 2

**Partition 1 (3 nodes):**
- Has majority (quorum)
- Continues accepting writes
- Remains available

**Partition 2 (2 nodes):**
- No majority
- Read-only mode
- Cannot accept writes

**After partition heals:**
- Minority nodes sync from majority
- Consistency restored

**CAP theorem**: ZooKeeper chooses CP (Consistency + Partition tolerance) over Availability

---

## Advanced Questions

### 1. How would you prevent watch storms?

**A**: Watch storm = mass watch triggers overwhelm cluster

**Solutions:**
1. **Exponential backoff**:
```java
private void watchWithBackoff(String path, int attempt) {
    long delay = Math.min(1000 * (1 << attempt), 10000);  // Max 10s
    Thread.sleep(delay);
    zk.getData(path, event -> watchWithBackoff(path, attempt + 1), null);
}
```

2. **Caching**:
```java
// Cache data locally, use watch only for invalidation
private volatile String cachedData;

zk.getData("/config", event -> {
    cachedData = null;  // Invalidate cache
}, null);
```

3. **Batching**: Process multiple watch events together

---

### 2. ZooKeeper vs etcd vs Consul?

**A**:

| Feature | ZooKeeper | etcd | Consul |
|---------|-----------|------|--------|
| **Protocol** | ZAB | Raft | Raft |
| **API** | Custom | HTTP/gRPC | HTTP |
| **Language** | Java | Go | Go |
| **Used by** | Kafka, HBase | Kubernetes | HashiCorp stack |
| **Service mesh** | No | No | Yes |
| **Health checks** | No | No | Yes |

**When to use each:**
- ZooKeeper: Legacy systems, Kafka/Hadoop ecosystem
- etcd: Kubernetes, cloud-native
- Consul: Service mesh, microservices

---

## Common Follow-ups

- "How do you handle session expiration?"
- "What's the maximum data size per ZNode?" (1MB)
- "How do you backup ZooKeeper?"
- "What's the typical latency?" (10-50ms for writes, 1-10ms for reads)

---

## Red Flags to Avoid

❌ **Don't say:**
- "Use ZooKeeper for data storage" - 1MB limit, not a database
- "ZooKeeper is highly available" - It's consistent (CP) and may become unavailable during partitions (not AP)
- "Watches are permanent" - They're one-time

---

## How to Explain in 30 Seconds

> "ZooKeeper provides coordination primitives for distributed systems using a hierarchical namespace of ZNodes. Key patterns: ephemeral sequential nodes for leader election (lowest number wins), distributed locks (watch previous node), and service discovery (ephemeral nodes auto-cleanup). Uses ZAB protocol for linearizable consistency with quorum-based writes. Trade-off: strong consistency over availability (CP in CAP). Choose etcd for modern cloud-native, Consul for service mesh."
