# Distributed Coordination (ZooKeeper)

**Code and tests**: See [ZooKeeper](../zookeeper/THEORY.md) for canonical code and tests.

## What is it?

Apache ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and group services in distributed systems. It provides primitives for building coordination services like leader election, distributed locks, and service discovery.

## Why do we need it?

**Problem it solves**: Distributed systems need coordination mechanisms for consensus, configuration management, and synchronization that are consistent, reliable, and fault-tolerant across network partitions and node failures.

**Without ZooKeeper**:
- Manual leader election with race conditions
- Configuration changes require restarting all nodes
- No reliable distributed locks
- Service discovery requires hardcoded addresses
- Difficult to maintain consistency across nodes

**With ZooKeeper**:
- Automated leader election with failover
- Dynamic configuration updates without restarts
- Distributed locks and barriers
- Service registry with watches for changes
- Sequential consistency for updates and FIFO client ordering

## Core Concepts

### 1. ZNode Hierarchy

```
ZooKeeper Namespace (like a file system):

/
├── /config
│   ├── /database
│   │   └── connection_string: "db.example.com:5432"
│   └── /cache
│       └── redis_url: "redis.example.com:6379"
├── /services
│   ├── /api-service
│   │   ├── /server1: "10.0.1.1:8080"  (ephemeral)
│   │   └── /server2: "10.0.1.2:8080"  (ephemeral)
│   └── /worker-service
│       └── /worker1: "10.0.2.1:9000"  (ephemeral)
└── /locks
    └── /distributed-lock-1

Each node stores data (max 1MB)
```

**ZNode types**:
- **Persistent**: Remains until explicitly deleted
- **Ephemeral**: Deleted when client session ends
- **Sequential**: Appends monotonically increasing counter
- **Container**: Deleted when no children (ZK 3.5+)

### 2. Watches

Clients can set watches on ZNodes to get notified of changes:

```
Client 1: getChildren("/services/api", watch=True)
         → Returns: [server1, server2]
         → Watch set

Server 3 joins:
         → Creates /services/api/server3

Client 1: Receives notification
         → "Children of /services/api changed"
         → Re-read to get updated list
```

**One-time triggers**: Watches fire once, must be re-registered

### Consistency Guarantees and Allowed Stale Reads

ZooKeeper does **not** provide strict linearizability for all operations. According to the [Apache ZooKeeper documentation](https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html#ch_zkGuarantees), it provides two core guarantees:
1. **Sequential Consistency**: Updates from a client will be applied in the order that they were sent.
2. **Single System Image**: A client will see the same view of the service regardless of the server it connects to.

**Ordinary reads can be stale**: A client connected to a follower can read a value that does not yet include a committed write from another client. 

**Two-Client Stale Read Trace:**
*   **Time 1**: Client A (Leader) writes `/config=v2`. Write is committed by quorum.
*   **Time 2**: Client B (Follower 1) reads `/config`. Follower 1 has not yet processed the commit for `v2`.
*   **Time 3**: Client B receives `/config=v1` (Stale read).

Even the `sync` operation, which asks the server to catch up with the leader, only guarantees that the server's state is at least as fresh as the leader's state at the moment the `sync` was issued. It does not establish strict latest data for subsequent reads if a new write commits concurrently.

### Session Expiration and Watch Re-registration
Watches in ZooKeeper are one-time triggers. Once a watch fires, the client must explicitly re-register it. If a client's session expires (due to GC pauses or network partitions), its ephemeral nodes are deleted. The client must re-establish a session, recreate ephemeral nodes, and re-register watches, but must also account for any events that were missed during the downtime.


### 3. ZAB Protocol (Consensus)

ZooKeeper Atomic Broadcast (ZAB) ensures sequential consistency for writes, but follower reads may be stale:

```
ZooKeeper Ensemble (cluster):

Leader (1)
├── Follower 1
├── Follower 2
└── Follower 3

Write request:
Client → Any server (leader or follower)
       → Forwarded to leader
       → Leader proposes to followers
       → Quorum (majority) acknowledges
       → Leader commits and notifies followers
       → Response to client
```

**Quorum**: Majority of nodes (e.g., 3 out of 5)
- Tolerates f failures with 2f+1 nodes
- 3 nodes: Tolerates 1 failure
- 5 nodes: Tolerates 2 failures
- 7 nodes: Tolerates 3 failures

## Use Cases

### 1. Leader Election

```
Election Algorithm:
1. Each candidate creates ephemeral sequential ZNode:
   /election/candidate-0000000001
   /election/candidate-0000000002
   /election/candidate-0000000003

2. Each candidate checks if they have lowest number:
   - If yes → Become leader
   - If no → Watch next lower numbered node

3. If watched node disappears:
   - Check again if now have lowest number
   - Repeat until becoming leader or stopped

Java example:
public class LeaderElection {
    private static final String ELECTION_PATH = "/election";
    private ZooKeeper zk;
    private String currentZnode;

    public void electLeader() throws Exception {
        // Create ephemeral sequential node
        currentZnode = zk.create(
            ELECTION_PATH + "/candidate-",
            new byte[]{},
            ZooDefs.Ids.OPEN_ACL_UNSAFE,
            CreateMode.EPHEMERAL_SEQUENTIAL
        );

        List<String> children = zk.getChildren(ELECTION_PATH, false);
        Collections.sort(children);

        if (currentZnode.endsWith(children.get(0))) {
            System.out.println("I am the leader!");
            performLeaderDuties();
        } else {
            // Watch the node before me
            String nodeToWatch = ELECTION_PATH + "/" + children.get(children.indexOf(currentZnode.substring(currentZnode.lastIndexOf('/') + 1)) - 1);
            zk.exists(nodeToWatch, event -> {
                try {
                    electLeader();  // Re-check if I'm leader
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }
    }
}
```

### 2. Distributed Locks

```
Lock Acquisition:
1. Create ephemeral sequential ZNode: /locks/lock-0000000001
2. Get children of /locks
3. If my node has lowest number → Acquired lock
4. Else → Watch next lower numbered node
5. When watched node deleted → Check again

Lock Release:
1. Delete my ZNode → Next waiter acquires lock

Java example:
public class DistributedLock {
    private ZooKeeper zk;
    private String lockPath = "/locks/lock-";
    private String currentLockNode;

    public void acquireLock() throws Exception {
        currentLockNode = zk.create(
            lockPath,
            new byte[]{},
            ZooDefs.Ids.OPEN_ACL_UNSAFE,
            CreateMode.EPHEMERAL_SEQUENTIAL
        );

        List<String> children = zk.getChildren("/locks", false);
        Collections.sort(children);

        if (currentLockNode.endsWith(children.get(0))) {
            System.out.println("Lock acquired");
            return;
        }

        // Wait for previous lock
        String previousNode = children.get(children.indexOf(currentLockNode.substring(currentLockNode.lastIndexOf('/') + 1)) - 1);
        CountDownLatch latch = new CountDownLatch(1);
        zk.exists("/locks/" + previousNode, event -> latch.countDown());
        latch.await();

        acquireLock();  // Recursively try again
    }

    public void releaseLock() throws Exception {
        zk.delete(currentLockNode, -1);
        System.out.println("Lock released");
    }
}
```

### 3. Service Discovery

```
Service Registration:
public class ServiceRegistry {
    private ZooKeeper zk;
    private static final String REGISTRY_PATH = "/services";

    public void register(String serviceName, String serviceAddress) throws Exception {
        String servicePath = REGISTRY_PATH + "/" + serviceName;

        // Ensure service directory exists
        if (zk.exists(servicePath, false) == null) {
            zk.create(servicePath, new byte[]{},
                      ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.PERSISTENT);
        }

        // Register instance (ephemeral)
        zk.create(
            servicePath + "/instance-",
            serviceAddress.getBytes(),
            ZooDefs.Ids.OPEN_ACL_UNSAFE,
            CreateMode.EPHEMERAL_SEQUENTIAL
        );
    }
}

Service Discovery:
public class ServiceDiscovery {
    public List<String> discoverServices(String serviceName) throws Exception {
        String servicePath = "/services/" + serviceName;

        List<String> instances = zk.getChildren(servicePath, event -> {
            // Re-discover on change
            discoverServices(serviceName);
        });

        List<String> addresses = new ArrayList<>();
        for (String instance : instances) {
            byte[] data = zk.getData(servicePath + "/" + instance, false, null);
            addresses.add(new String(data));
        }
        return addresses;
    }
}
```

### 4. Configuration Management

```
Dynamic Configuration:
public class ConfigManager {
    private ZooKeeper zk;
    private String configPath = "/config/app";

    public void watchConfig() throws Exception {
        byte[] data = zk.getData(configPath, event -> {
            try {
                // Reload config on change
                watchConfig();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, null);

        String config = new String(data);
        applyConfiguration(config);
    }

    public void updateConfig(String newConfig) throws Exception {
        zk.setData(configPath, newConfig.getBytes(), -1);
        // All watching clients automatically notified
    }
}
```

## When to use

✅ **Use ZooKeeper when:**
- Need leader election in distributed systems
- Require distributed locks or barriers
- Service discovery and registration
- Configuration management across cluster
- Cluster membership tracking
- Coordination primitives for distributed algorithms

**Specific scenarios:**
- Kafka: Broker coordination and consumer group management
- HBase: Master election and region server coordination
- Hadoop: NameNode HA coordination
- Solr: Cluster state management

## When NOT to use

❌ **Avoid or reconsider when:**
- Primary data storage (1MB limit per ZNode)
- High-throughput data store
- Message queue or pub/sub system
- Low-latency requirements (<10ms)
- Simple single-node applications
- Frequently changing data (watch storms)

**Consider alternatives:**
- **etcd**: Modern alternative, better API, used by Kubernetes
- **Consul**: Service mesh features, better for microservices
- **Redis**: For simple locks with lower latency
- **Database**: For configuration with richer queries

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Sequential consistency** | Ordered writes, single-client FIFO | Follower reads may be stale |
| **Watches** | Event-driven updates | One-time triggers, must re-register |
| **Ephemeral nodes** | Auto cleanup on disconnect | Session management complexity |
| **Sequential nodes** | Ordering guarantees | Extra metadata per node |
| **Centralized** | Simple coordination model | Single point of coordination |
| **ZAB consensus** | Fault tolerance | Performance overhead |

## Real-world examples

### Kafka
- **Usage**: Broker discovery, leader election, consumer group coordination
- **Pattern**: Ephemeral nodes for brokers, watchers for rebalancing

### HBase
- **Usage**: Master election, region server registration
- **Pattern**: Ephemeral nodes track active region servers

### Apache Solr
- **Usage**: SolrCloud cluster state management
- **Pattern**: ZNodes represent shards, replicas, and collection state

### Dubbo (Alibaba)
- **Usage**: Service registry and discovery
- **Pattern**: Services register as ephemeral nodes

## Complexity Analysis

| Operation | Complexity | Latency |
|-----------|-----------|---------|
| **Create** | O(1) | ~10-50ms |
| **Read** | O(1) | ~1-10ms |
| **Update** | O(1) | ~10-50ms |
| **Delete** | O(1) | ~10-50ms |
| **List children** | O(N) | ~10-50ms |

## Common Problems and Solutions

### 1. Watch Storms

**Problem**: Mass watch triggers overwhelm cluster

**Solution**:
```java
// Use exponential backoff for watch re-registration
private void watchWithBackoff(String path) {
    try {
        zk.exists(path, event -> {
            // Backoff before re-registering
            Thread.sleep(100 + (long)(Math.random() * 1000));
            watchWithBackoff(path);
        });
    } catch (Exception e) {
        // Handle
    }
}
```

### 2. Session Expiration

**Problem**: Client disconnected, ephemeral nodes deleted

**Solution**:
```java
// Implement session reconnection logic
zk = new ZooKeeper(connectionString, sessionTimeout, event -> {
    if (event.getState() == KeeperState.Expired) {
        // Re-create client and re-register
        reconnect();
        reRegisterNodes();
    }
});
```

## Key Takeaways

1. **Coordination primitive**: Not a data store; for coordination logic
2. **Sequential consistency**: Ordered writes, but follower reads may be stale
3. **Quorum-based**: Requires majority for operations
4. **Ephemeral nodes**: Track liveness of distributed components
5. **Sequential nodes**: Enable fair ordering (locks, elections)
6. **Watches**: One-time event notifications
7. **ZAB protocol**: Ensures consistency across ensemble

---

## Related Concepts
- [Service Discovery](../service-discovery/) - Registration patterns
- [System Design Fundamentals](../../00-theory/system-design-fundamentals/) - Consensus and distributed systems foundations
- [Message Queues](../message-queues/) - Kafka coordination

## ZooKeeper Overview

## Why do we need it?

When systems scale horizontally, components must agree on shared coordination state:
- Which node is leader right now?
- Which instances are healthy members?
- Which config version is active?
- Who owns a lock for critical work?

ZooKeeper provides simple primitives for these patterns with strong consistency and ordered updates.

## Types/Approaches

### 1. Data Primitives (ZNodes)
- **Persistent**: stays until deleted.
- **Ephemeral**: removed when session ends.
- **Sequential**: node name gets an increasing suffix for ordering.

### 2. Watches
- One-shot change notifications on znodes.
- Clients must re-register after event delivery.

### 3. Cluster Roles
- Leader handles writes.
- Followers replicate state and can serve reads.
- Quorum commit ensures fault tolerance.

## How it works

### Coordination model
1. Clients create/read/update znodes.
2. Writes go through quorum commit.
3. Ephemeral nodes encode liveness.
4. Watches trigger client reactions to state changes.

### Consistency and Stale Reads

ZooKeeper provides **Sequential Consistency** for writes and **Single System Image** per client. It does **not** guarantee linearizability for ordinary reads. 
Followers may serve reads from their local state, which might lag behind the leader's committed state, allowing a client to see stale data relative to global time. A `sync` command asks the follower to catch up to the leader's state at the time of invocation, but concurrent commits immediately after can still render subsequent reads stale.

**Two-Client Stale Read Trace:**
*   **Time 1**: Client A (Leader) writes `/state=v2`. Commit succeeds.
*   **Time 2**: Client B (Follower 1) reads `/state`. The follower hasn't applied `v2` yet.
*   **Time 3**: Client B receives `/state=v1` (a stale read).

This makes ordinary ZooKeeper reads unsuitable as the sole synchronization mechanism without application-level fencing.


### Common recipes
- **Leader election**: ephemeral-sequential nodes under election path.
- **Distributed lock**: acquire smallest sequence node.
- **Service discovery**: ephemeral children under service path.
- **Dynamic config**: read config znode + watch for updates.

## When to use

- Apache-stack systems already integrated with ZooKeeper.
- Coordination-heavy workflows requiring strong ordering semantics.
- Stateful systems needing battle-tested leadership and membership logic.

## When NOT to use

- Large mutable data storage.
- High-throughput event streaming.
- Simple cloud-native service discovery where managed alternatives fit better.

## Trade-offs

| Pros | Cons |
|------|------|
| Sequential consistency for writes | Ordinary reads from followers can be stale |
| Mature recipes for election/locks/membership | Not designed for high-throughput writes |
| Ephemeral nodes simplify liveness handling | Watch behavior is one-shot and easy to misuse |
| Proven in many production systems | Often replaced by simpler cloud-native alternatives |

## Modern alternatives

- **etcd**: simpler cloud-native KV + watch model.
- **Consul**: service discovery + health checks + KV.
- **Kubernetes API primitives**: built-in coordination within K8s ecosystems.

## Interview checklist

1. Frame ZooKeeper as coordination, not a primary DB.
2. Use ephemeral/sequential nodes for election/locks.
3. Mention quorum behavior and failure handling.
4. Call out watch re-registration.
5. Compare with etcd/Consul based on environment.

## Key Takeaways

1. ZooKeeper remains a high-signal coordination concept for interviews.
2. It excels at small coordination state with ordered sequential consistency.
3. Recipes are simple to describe but require disciplined client logic.
4. In modern stacks, tool choice often depends on ecosystem fit.

