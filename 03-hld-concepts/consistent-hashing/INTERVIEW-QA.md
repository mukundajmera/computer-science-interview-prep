# Interview Questions: Consistent Hashing

## Basic Questions

### 1. What is consistent hashing and what does it solve?
**Q**: Why not just use `hash(key) % N`?

**A**: Modulo hashing remaps a large fraction of keys when `N` changes. Consistent hashing maps keys and nodes into the same hash space so membership changes move only a bounded subset of keys.

### 2. How does the hash ring work?
**Q**: Explain key placement quickly.

**A**: Hash the key, move clockwise to the first node, and that node owns the key. For replication, continue clockwise to distinct physical nodes.

### 3. Why are virtual nodes important?
**Q**: What do vnodes fix?

**A**: They reduce ownership skew by spreading each physical node across many ring positions. They also spread failure impact and support weighted capacity.

### 4. How much data moves during scale events?
**Q**: Compare modulo and consistent hashing.

**A**:

| Example | Modulo | Consistent hashing |
|---|---:|---:|
| 3 -> 4 nodes | ~75% moved | ~25% moved |
| 10 -> 11 nodes | ~91% moved | ~9% moved |

### 5. Is consistent hashing enough for hotspots?
**Q**: If one key is extremely hot, does the ring fix it?

**A**: Not fully. The ring spreads key ownership, not traffic popularity. Hot keys need read-replica fan-out, key bucketing/salting, cache coalescing, and protection controls.

## Intermediate Questions

### 1. Ring vs slot-range partitioning
**Q**: How do you compare ring-based routing with fixed hash slots?

**A**: Ring-based routing gives smooth membership behavior and low remap. Slot-based routing gives deterministic ownership and strong operational tooling. Choose based on operational preference and ecosystem.

### 2. How do you implement replication?
**Q**: What is replica selection on a ring?

**A**: Choose primary via clockwise lookup, then keep scanning clockwise until you collect `R` distinct physical nodes. Enforce rack/AZ diversity if required.

### 3. What is bounded-load consistent hashing?
**Q**: Why is it used?

**A**: It avoids assigning to nodes already above a configured overload factor relative to average. It reduces worst-case skew under uneven traffic, but adds routing logic complexity.

### 4. How do you handle node failure day-of?
**Q**: What is your incident flow?

**A**:
1. Mark node unhealthy.
2. Stop routing new traffic there.
3. Serve from replicas.
4. Rebalance/backfill after replacement.
5. Validate parity before restoring full placement.

### 5. How do you rebalance safely when adding nodes?
**Q**: What operational checks do you run?

**A**: Gradual traffic shift, migration throttling, key-count and checksum validation, P99 guardrails, and rollback criteria.

## Scenario Questions

### 1. Cache cluster scale-out
**Q**: You are scaling from 8 to 12 cache nodes. What do you say in an interview?

**A**: "I will use consistent hashing with vnodes so only a bounded slice of keys moves. I will warm high-hit keys first, rate-limit cold misses to protect backing stores, and monitor hit-rate and tail latency during cutover."

### 2. Hot-traffic key
**Q**: One key receives 40x normal traffic. What is your mitigation stack?

**A**:
1. Replicated reads for that key.
2. Key bucketing/salting if semantics allow.
3. Local fallback cache + single-flight on misses.
4. Targeted rate limits/admission control.

### 3. Mixed hardware cluster
**Q**: Half your nodes are 2x larger. How do you reflect that?

**A**: Use weighted vnode assignment so larger nodes own proportionally more ranges while retaining the same routing semantics.

## Advanced Questions

### 1. How would you test a consistent hashing implementation?
**Q**: What should tests prove?

**A**:
- Deterministic routing for same key/ring state
- Bounded remap under node add/remove
- Replica uniqueness and failure-domain diversity
- Acceptable skew under random keys
- Stable behavior under unhealthy-node events

### 2. How do you propagate ring metadata?
**Q**: Why does control-plane design matter?

**A**: Inconsistent ring views cause split routing. Use versioned ring metadata, controlled rollout, and monotonic adoption with fallback.

### 3. When would you avoid consistent hashing entirely?
**Q**: Give practical cases.

**A**: Very small fixed clusters, workloads dominated by range queries, or systems where deterministic slot ownership and explicit rebalance tools are preferred.

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Says "consistent hashing" without explaining remap |
| 3 | Explains ring + vnodes clearly |
| 5 | Adds hotspot handling, failure playbook, and operational rollout details |

## Common follow-ups

1. How many vnodes per node would you start with?
2. How do you ensure replicas are on different failure domains?
3. Which metrics prove rebalance is safe to continue?
4. How do you avoid cache stampede during node add?
5. How do you compare this with jump hash/rendezvous hash?

## Red flags to avoid

- Claiming hot-key problems are solved by the ring alone
- Ignoring metadata consistency/versioning
- No failure handling story beyond "add replicas"
- No remap quantification when discussing scaling

## Strong verbal answers

### 45-second version
"Consistent hashing minimizes remapping during cluster changes by mapping keys and nodes into the same hash space and routing clockwise. I use vnodes for smoother distribution and weighted ownership for mixed hardware. It solves structural ownership churn, but hot keys still need replica reads, key bucketing, and cache protections. Operationally, I use gradual rebalance with guardrails on hit-rate and P99 latency."

### 2-minute version
"Modulo hashing is simple but operationally expensive when `N` changes because most keys remap. Consistent hashing avoids that by giving each node ranges on a ring so scale events move only a bounded fraction. In practice I use virtual nodes to reduce skew and support heterogeneous capacity with weighted vnode counts. For replication I continue clockwise to distinct nodes and enforce failure-domain diversity.

I also call out a common confusion: consistent hashing handles ownership churn, not popularity skew. If a key becomes extremely hot, I add replicated reads, optional key bucketing, single-flight miss protection, and targeted rate controls. On failure day, I remove unhealthy nodes from routing quickly, serve from replicas, and heal with controlled backfill. During planned scaling, I throttle migration and gate progression on hit-rate, P99 latency, and parity checks."

## Related concepts

- [Consistent Hashing Theory](./THEORY.md)
- [Database Sharding](../database-sharding/)
- [Caching](../caching/)
- [Load Balancing](../load-balancing/)
