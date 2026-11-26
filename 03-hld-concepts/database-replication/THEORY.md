# Database Replication

## What is it?

Database replication is the process of copying data from one database server (primary/master) to one or more other servers (replicas/slaves) to ensure data availability, fault tolerance, and read scalability.

## Why do we need it?

**Problem**: A single database server is a single point of failure and cannot handle high read loads.

**Solution**: Replicate data across multiple servers to provide redundancy and distribute read load.

**Real Scenario**: Instagram serves 500 million daily active users. A single database cannot handle this load. Read replicas handle 99% of read queries while the primary handles writes.

## Types/Approaches

### 1. Primary-Replica (Master-Slave)
```
             ┌──────────┐
  Writes ───▶│  Primary │
             └────┬─────┘
                  │ Replication
        ┌─────────┼─────────┐
        ▼         ▼         ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Replica │ │ Replica │ │ Replica │
   └─────────┘ └─────────┘ └─────────┘
        ▲         ▲         ▲
        └─────────┴─────────┘
              Reads
```
- One primary handles all writes
- Replicas handle reads
- **Pros**: Simple, read scalability
- **Cons**: Single write point, replication lag

### 2. Multi-Primary (Master-Master)
```
   Writes ◀──▶ ┌──────────┐ ◀──▶ Writes
               │ Primary 1 │
               └─────┬─────┘
                     │ Bi-directional
               ┌─────▼─────┐
               │ Primary 2 │
               └───────────┘
```
- Multiple primaries accept writes
- Bi-directional replication
- **Pros**: Write availability, geographic distribution
- **Cons**: Conflict resolution, complexity

### 3. Synchronous vs Asynchronous

| Aspect | Synchronous | Asynchronous |
|--------|-------------|--------------|
| **Consistency** | Strong | Eventual |
| **Latency** | Higher (waits for replica) | Lower |
| **Availability** | Lower (replica failure blocks writes) | Higher |
| **Data loss risk** | None | Possible on failure |

## How it works

### Replication Process

```
Primary                                     Replica
   │                                           │
   │  1. Client Write                          │
   ▼                                           │
┌──────────────┐                              │
│ Write to WAL │                              │
│ (Write-Ahead │                              │
│    Log)      │                              │
└──────┬───────┘                              │
       │                                       │
       │  2. Stream WAL                        │
       ├──────────────────────────────────────▶│
       │                                       ▼
       │                              ┌──────────────┐
       │                              │ Apply WAL    │
       │                              │ to Replica   │
       │                              └──────────────┘
       │                                       │
       │  3. ACK (sync only)                   │
       │◀──────────────────────────────────────┤
       ▼                                       │
┌──────────────┐                              │
│ Commit       │                              │
└──────────────┘                              │
```

### Replication Lag

```
Timeline:
Primary:   [Write X] ─────────────────▶ [Write Y]
Replica:           [Apply X] ─ LAG ─▶ [Apply Y]
                   └────────┘
                   Replication Lag
                   
Reads during lag may return stale data:
- Primary: X = 100
- Replica: X = 50 (old value)
```

## When to use

| Scenario | Replication Type |
|----------|------------------|
| High read traffic | Primary + Read Replicas |
| High availability | Synchronous to standby |
| Geographic distribution | Multi-region async |
| Disaster recovery | Cross-region replicas |
| Analytics workload | Async replica for reporting |

## When NOT to use

| Scenario | Why Not |
|----------|---------|
| Write-heavy workload | Replication adds overhead |
| Strong consistency required | Async replication is eventual |
| Small data size | Over-engineering |
| Cost-constrained | Multiple servers = more cost |

## Trade-offs

| Aspect | Trade-off |
|--------|-----------|
| **Consistency** | Sync = strong but slow; Async = fast but eventual |
| **Availability** | More replicas = higher availability |
| **Latency** | Sync adds network RTT; Async doesn't |
| **Cost** | More replicas = more infrastructure |
| **Complexity** | Failover, conflict resolution |

## Conflict Resolution (Multi-Primary)

### Strategies:

1. **Last-Write-Wins (LWW)**: Latest timestamp wins
2. **First-Write-Wins**: Earliest timestamp preserved
3. **Merge**: Combine conflicting values
4. **Custom resolution**: Application-specific logic

```
Primary 1: UPDATE users SET name='Alice' WHERE id=1  (T=100)
Primary 2: UPDATE users SET name='Bob' WHERE id=1    (T=101)

LWW Result: name = 'Bob' (T=101 > T=100)
```

## Failover Strategies

### Automatic Failover
```
              ┌──────────┐
              │ Primary  │ ✗ FAILURE
              └──────────┘
                   │
        Heartbeat timeout
                   │
              ┌────▼────┐
              │ Promote │
              │ Replica │
              └────┬────┘
                   │
              ┌────▼────┐
              │   New   │
              │ Primary │
              └─────────┘
```

### Split-Brain Prevention
- **Quorum-based**: Majority must agree on primary
- **Fencing**: Kill old primary before promoting new
- **Witness node**: Third-party arbiter

## Real-world examples

### MySQL
- **Async replication**: Default, log-based
- **Semi-sync**: Waits for at least one replica ACK
- **Group Replication**: Multi-primary with Paxos

### PostgreSQL
- **Streaming replication**: WAL-based
- **Synchronous mode**: Configurable per-transaction
- **Logical replication**: Table-level, selective

### MongoDB
- **Replica sets**: Automatic failover
- **Arbiter nodes**: Voting-only members
- **Read preferences**: Control read routing

## Complexity Analysis

| Operation | Primary | Replica |
|-----------|---------|---------|
| Write | O(1) + replication | N/A |
| Read | O(log n) | O(log n) |
| Failover | O(seconds) | - |
| Catch-up | O(lag data size) | - |

## Key Metrics

| Metric | Good Value | Why |
|--------|------------|-----|
| Replication lag | <1s | Data freshness |
| Replica count | 2-3 | Availability vs cost |
| Failover time | <30s | Minimize downtime |
| Write throughput | Depends | Not limited by replicas |
| Read throughput | Linear scaling | Per replica |

## Replication vs. Backup & Recovery Budgets

A dangerous operational anti-pattern is assuming that database replication replaces the need for backups. Replication provides high availability and read scalability; backups provide historical state and point-in-time recovery.

### The Accidental Deletion Trace

If an administrator or application bug executes `DELETE FROM users WHERE tenant_id = 'A';` without a proper `WHERE` clause, or if a table is accidentally dropped:
1. **Primary**: Immediately commits the deletion.
2. **Replication Stream**: The `DELETE` or `DROP` command is propagated to all live replicas almost instantly (e.g., within 10ms).
3. **Replicas**: Apply the deletion. 

Within seconds, the data is completely gone from the entire replication topology. To recover from this, you need **point-in-time history**. See specific database notes on [PostgreSQL PITR](../postgresql/THEORY.md) or [MySQL delayed recovery/binary logs](../mysql/THEORY.md).

### Components of a Robust Backup Architecture

True backup and recovery require mechanisms completely disjoint from the live replication stream:
- **Checkpoint + Log Retention**: A full snapshot baseline plus immutable transaction logs (WAL/Binlog) retained securely.
- **Durability Acknowledgements**: Ensuring the backup storage (e.g., S3) has securely flushed the logs to disk before acknowledging them.
- **Consistent Restore Point**: The ability to replay logs up to an exact timestamp or transaction ID prior to the incident.
- **Protected/Immutable Storage**: Backups stored in a write-once-read-many (WORM) environment isolated from the production environment's primary credentials.
- **Encryption/Key Dependency**: Storing the KMS or encryption keys required to read the backups in a separately managed, highly available vault.

### RPO and RTO Budget Calculations

Recovery Point Objective (RPO) and Recovery Time Objective (RTO) must be grounded in physical limits, not just "we have 3 replicas." 

*A successful backup job is not proof of a successful restore.* You must budget for the actual work required to recreate the database.

**Assume a 5 TB Dataset Scenario:**
- **RPO (Data Loss Window)**: Determined by the interval of WAL/Binlog shipping to remote storage. If logs are shipped every 5 minutes, your actual RPO is up to 5 minutes of lost data, regardless of replication lag.
- **RTO (Downtime Window)**: Restoring 5 TB is constrained by storage throughput and CPU for rebuilding indexes.
  - *Provisioning/Boot*: 10 minutes (Spinning up new database nodes).
  - *Rehydration Budget*: At 500 MB/s sustained network throughput, downloading 5 TB takes ~2.8 hours.
  - *Log Replay*: Applying 4 hours of transaction logs takes ~30 minutes.
  - *Index Rebuild/Verification*: Verifying constraints and rebuilding complex indexes takes ~1 hour.
  - *Total RTO*: **~4.5 hours** (Excluded stages in naive estimates often ignore boot time, network bandwidth limits, and index rebuilding).

### Safe Offline Restore Drills

To prove the backup is viable without touching production or using dangerous "create infrastructure" scripts on the live environment:
1. **Isolated Provisioning**: Run an offline drill in an isolated VPC or sandbox environment.
2. **Key Availability Check**: Verify that the restore process can successfully authenticate and fetch the necessary decryption keys from the KMS.
3. **Integrity & Invariant Checks**: Once data is rehydrated, run checksums on key tables or verify domain invariants (e.g., `SELECT SUM(balance) FROM accounts == total_ledger_value`).
4. **Rollback/Canary Acceptance**: The drill is marked successful only if the restored offline cluster successfully passes application integration tests and can be deterministically destroyed (rolled back) within a set time limit, ensuring no lingering cloud costs or rogue access points.

## Key Takeaways

1. **Async is common**: Most systems use async for performance
2. **Lag is inevitable**: Design for eventual consistency
3. **Failover is hard**: Test regularly, automate carefully
4. **Read replicas scale reads**: Not writes
5. **Split-brain is dangerous**: Use proper fencing and quorum
