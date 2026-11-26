# Interview Questions: Database Replication

## Basic Questions

### 1. What is database replication and why is it needed?
**Q**: Explain database replication and its purposes.

**A**: Database replication copies data from one server (primary) to others (replicas) for:

- **High Availability**: If primary fails, replica takes over
- **Read Scalability**: Distribute read load across replicas
- **Disaster Recovery**: Geographic redundancy
- **Reduced Latency**: Replicas close to users

---

### 2. What's the difference between synchronous and asynchronous replication?
**Q**: Compare sync and async replication.

**A**:
| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **Commit** | Waits for replica ACK | Returns immediately |
| **Consistency** | Strong | Eventual |
| **Latency** | Higher (network RTT) | Lower |
| **Data loss** | None possible | Possible |
| **Use case** | Financial transactions | Most web apps |

**Example**: Bank transfer needs sync; social media feed can use async.

---

### 3. What is replication lag?
**Q**: Explain replication lag and its implications.

**A**: Replication lag is the delay between a write on primary and its appearance on replica.

**Implications**:
- Read-after-write may see stale data
- Monitoring becomes critical
- May affect user experience

**Solutions**:
- Read from primary for recent writes
- Track lag and route accordingly
- Use synchronous replication for critical data

---

### 4. What is primary-replica (master-slave) replication?
**Q**: Explain primary-replica architecture.

**A**:
```
Writes ───▶ Primary ───▶ Replicas ◀─── Reads
```
- **Primary**: Handles all writes
- **Replicas**: Handle reads, maintain copies
- **Replication**: Primary streams changes to replicas

**Pros**: Simple, good read scaling
**Cons**: Single write point, lag issues

---

### 5. How do read replicas improve performance?
**Q**: Explain how read replicas help scale.

**A**: Read replicas handle read traffic that would otherwise hit the primary:

```
Before:     Primary handles 100% reads + writes
After:      Primary: writes + 10% reads
            3 Replicas: 30% reads each
```

**Benefits**:
- Primary resources for writes
- Linear read scaling with replica count
- Geographic distribution possible

**Limitations**:
- Doesn't scale writes
- Lag may serve stale data

---

## Intermediate Questions

### 6. How do you handle replication lag in application code?
**Q**: A user updates their profile, but immediately reading shows old data. How do you fix this?

**A**: **Read-your-writes consistency solutions**:

1. **Sticky reads**: Route user's reads to same replica
2. **Read from primary**: For recently written data
3. **Lag tracking**: Wait if replica lag > threshold
4. **Client token**: Track write timestamp, compare to replica

```python
def get_user(user_id, last_write_time):
    if replica.lag < last_write_time:
        # Replica hasn't caught up
        return primary.get(user_id)
    return replica.get(user_id)
```

---

### 7. How does failover work in database replication?
**Q**: Primary database fails. Walk through the failover process.

**A**: **Failover steps**:

1. **Detection**: Health check timeout (5-30 seconds)
2. **Verification**: Confirm primary is actually down
3. **Selection**: Choose replica (most up-to-date)
4. **Promotion**: Configure replica as new primary
5. **Reconfiguration**: Update connection strings
6. **Recovery**: Old primary becomes replica or discarded

**Challenges**:
- Split-brain: Two primaries accepting writes
- Data loss: Async replica missing recent writes
- Client reconnection: Applications need to update

---

### 8. What is split-brain and how do you prevent it?
**Q**: Explain split-brain in database clusters.

**A**: **Split-brain**: Network partition causes two primaries to operate independently, leading to divergent data.

```
        Network Partition
             │
Primary A ◀──┼──▶ Primary B
(DC 1)       │    (DC 2)
             │
Both accepting writes!
```

**Prevention**:
1. **Quorum**: Require majority to be primary
2. **Fencing**: Physically isolate old primary
3. **Witness**: Third-party arbiter decides primary
4. **STONITH**: "Shoot The Other Node In The Head"

---

### 9. What is multi-primary (master-master) replication?
**Q**: When would you use multi-primary replication?

**A**: Multi-primary allows writes to multiple nodes with bi-directional sync.

**Use cases**:
- Geographic write distribution
- High write availability
- Active-active data centers

**Challenges**:
- Conflict resolution required
- Complex to debug
- Eventual consistency

**Conflict resolution**:
```
DC-East: UPDATE balance = 100 WHERE id=1  (T=1)
DC-West: UPDATE balance = 200 WHERE id=1  (T=2)

Last-Write-Wins: balance = 200
```

---

### 10. How do you monitor replication health?
**Q**: What metrics would you track for replication?

**A**: **Key metrics**:

| Metric | Alert Threshold | Why |
|--------|-----------------|-----|
| Replication lag | >1 second | Data freshness |
| Replica status | Disconnected | Availability |
| Bytes behind | >10MB | Catch-up needed |
| Failover count | >0 | Stability |
| Write throughput | Varies | Capacity |

**Monitoring tools**:
- MySQL: `SHOW SLAVE STATUS`
- PostgreSQL: `pg_stat_replication`
- Custom: Query primary/replica timestamps

---

## Advanced Questions

### 11. Design a database replication system for a global application
**Q**: Design replication for an e-commerce site with users in US, Europe, and Asia.

**A**: 
```
                    ┌─────────────────┐
                    │  Global Primary │
                    │    (US-East)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Regional │        │ Regional │        │ Regional │
   │  Primary │        │  Primary │        │  Primary │
   │  (US)    │        │  (EU)    │        │  (Asia)  │
   └────┬─────┘        └────┬─────┘        └────┬─────┘
        │                   │                   │
   Read Replicas       Read Replicas       Read Replicas
```

**Design decisions**:
- **Global primary**: For cross-region consistency
- **Regional primaries**: For local writes (catalog, inventory)
- **Conflict resolution**: Last-write-wins or per-field merge
- **Latency**: Async between regions, sync within region

---

### 12. How do you handle partial failures during replication?
**Q**: A write succeeds on primary but fails to replicate. What happens?

**A**: **Depends on replication mode**:

**Synchronous**:
- Write blocked until replica confirms
- If replica fails, write fails or times out
- No data inconsistency

**Asynchronous**:
- Write succeeds on primary immediately
- Replication retries in background
- If primary fails before replication: data loss

**Semi-synchronous** (best of both):
- Wait for at least one replica ACK
- Fallback to async if all replicas down

---

### 13. How would you implement read-after-write consistency?
**Q**: Implement a system where users always see their own writes.

**A**: **Implementation approach**:

```python
class ReplicatedDB:
    def __init__(self):
        self.primary = PrimaryConnection()
        self.replicas = [ReplicaConnection(r) for r in REPLICAS]
        self.user_write_times = {}  # user_id -> last_write_time
    
    def write(self, user_id, data):
        self.primary.write(data)
        self.user_write_times[user_id] = time.time()
    
    def read(self, user_id, query):
        last_write = self.user_write_times.get(user_id, 0)
        
        # If recent write, read from primary
        if time.time() - last_write < LAG_THRESHOLD:
            return self.primary.read(query)
        
        # Otherwise, use replica
        return self.get_healthy_replica().read(query)
```

---

### 14. Compare PostgreSQL, MySQL, and MongoDB replication
**Q**: What are the differences in replication approaches?

**A**:

| Feature | PostgreSQL | MySQL | MongoDB |
|---------|------------|-------|---------|
| **Method** | WAL streaming | Binary log | Oplog |
| **Sync mode** | Configurable | Semi-sync | Write concern |
| **Multi-primary** | BDR extension | Group Replication | Sharded cluster |
| **Failover** | Manual/Patroni | Orchestrator | Automatic |
| **Logical rep** | Yes (v10+) | Yes | Change streams |

---

### 15. Why is database replication not a backup?
**Q**: If we have three synchronous replicas across different availability zones, do we still need backups?

**A**: Yes, replication is not a backup. Replication provides high availability (if a node fails) and read scalability, but it does not protect against data corruption or human error.

**The Accidental Deletion Trace**:
1. A developer accidentally executes `DROP TABLE users;` on the primary.
2. The primary commits this command.
3. The replication stream instantly propagates the `DROP TABLE` command to all three replicas.
4. All replicas drop their `users` table within milliseconds.

To recover, you need point-in-time history (backups + transaction logs) to restore the database to the exact moment before the accidental drop.

---

### 16. How do you calculate RPO and RTO budgets for recovery?
**Q**: How do you prove your backup strategy meets business requirements?

**A**: A successful backup job does not prove a successful restore. You must calculate Recovery Point Objective (RPO) and Recovery Time Objective (RTO) based on physical limits.

**RPO (Data Loss Window)**:
- Depends on how frequently logs (WAL/Binlog) are shipped to remote storage.
- If shipped every 5 minutes, RPO is 5 minutes.

**RTO (Downtime Window) Budgeting**:
Calculate RTO by summing the required physical operations, explicitly excluding nothing. For a 5 TB dataset:
1. **Provisioning/Boot**: Time to provision new cloud resources (e.g., 10 mins).
2. **Rehydration**: Network transfer limits. At 500 MB/s, 5 TB takes ~2.8 hours.
3. **Log Replay**: Time to apply transaction logs since the last snapshot (e.g., 30 mins).
4. **Index Rebuild/Verification**: Time to verify constraints and rebuild complex indexes (e.g., 1 hour).
**Total RTO**: ~4.5 hours.

---

### 17. How do you perform a safe database restore drill?
**Q**: How do you ensure your backups actually work without risking production?

**A**: You must perform offline restore drills with strict boundaries.

**Safe Drill Acceptance Criteria**:
1. **Isolated Environment**: Run the drill in an offline sandbox or isolated VPC. Never use runbooks that create resources in production or require privileged production data access.
2. **Key Availability**: Prove the drill can successfully authenticate and fetch necessary decryption keys from the KMS.
3. **Integrity Checks**: After rehydration, verify checksums and domain invariants (e.g., total ledger balance matches expected aggregate).
4. **Bounded Rollback**: The drill is only successful if the restored cluster passes canary tests and is then deterministically destroyed within a time limit, ensuring no leaked resources or rogue access points.

---

## Common Follow-ups

- **How do you test failover?** Chaos engineering, regular drills, automated testing
- **What about cross-region replication?** Async usually, handle higher lag
- **How do you handle schema changes?** Rolling updates, backward compatible
- **What's the CAP theorem impact?** Choose between consistency and availability

## Red Flags to Avoid

- **Ignoring lag**: "Replicas are always in sync" - they're not
- **No failover plan**: Every system needs tested failover
- **Sync everywhere**: Performance impact is significant
- **Ignoring conflicts**: Multi-primary needs conflict strategy

## How to Explain in 30 Seconds

"Database replication copies data from a primary server to replica servers for high availability and read scaling. Writes go to primary, which streams changes to replicas via write-ahead log. Replication can be synchronous (waits for replica) for consistency or asynchronous (faster) for performance. Key challenges are replication lag (replicas behind primary), failover automation, and split-brain prevention. For global systems, we use regional primaries with async replication between regions, accepting eventual consistency for lower latency."
