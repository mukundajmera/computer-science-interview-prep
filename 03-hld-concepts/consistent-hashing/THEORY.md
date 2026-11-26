# Consistent Hashing

Consistent hashing is a key-placement strategy that minimizes remapping when nodes are added or removed.

## What is it?

Keys and nodes are mapped to the same hash space (often a ring). A key is assigned to the first node clockwise from its hash position.

## Why do we need it?

Simple modulo hashing (`hash(key) % N`) causes large remaps when `N` changes. In contrast, consistent hashing typically remaps only a bounded fraction of keys.

## Requirements and constraints

Before selecting consistent hashing, define:
- Membership churn frequency (autoscaling, failures, maintenance)
- Replica strategy and failure domain requirements
- Load distribution tolerance (acceptable skew)
- Lookup latency constraints (routing path complexity)
- Operational model for rebalancing and metadata propagation

## Movement math: modulo vs ring

| Cluster resize | Modulo hashing (approx keys moved) | Consistent hashing (approx keys moved) |
|---|---:|---:|
| 3 -> 4 nodes | ~75% | ~25% |
| 10 -> 11 nodes | ~91% | ~9% |
| Remove 1 of N nodes | High remap | Mostly affected ranges only |

## Types/Approaches

### 1. Basic ring
Place each physical node once. Simple, but can be uneven.

### 2. Virtual nodes (vnodes)
Place each physical node many times on the ring.
- Smoother load distribution
- Better failure spreading
- Supports heterogeneous capacity

### 3. Weighted placement
Assign more virtual nodes to bigger machines.

## Vnodes vs weighted nodes guidance

| Situation | Better default |
|---|---|
| Similar hardware, small cluster | Fixed vnode count |
| Mixed hardware capacity | Weighted vnode count |
| Frequent autoscaling | Higher vnode count with strong monitoring |
| Strict simplicity priority | Lower vnode count + accept more skew |

## How it works

1. Hash nodes into ring positions.
2. Hash key.
3. Route to first clockwise node.
4. For replication, continue clockwise to distinct physical nodes.

Complexity (sorted ring):
- Lookup: `O(log n)`
- Add/remove node: `O(k)` for `k` vnodes belonging to that node

## Structural vs traffic imbalance

Consistent hashing mainly solves **structural imbalance** (uneven key ownership under topology changes). It does not fully solve **traffic imbalance** (a few keys getting extreme traffic).

Traffic-hotspot mitigation still needs:
- Replicated read fan-out for hot keys
- Key bucketing/salting where valid
- Local caches and request coalescing
- Targeted rate limits/admission control

## Bounded load

Bounded-load variants avoid assigning keys to nodes beyond a configured overload factor above average. This reduces worst-case skew but adds routing complexity.

## Ring vs slot-range trade-off

| Approach | Strength | Cost |
|---|---|---|
| Ring-based consistent hashing | Simple scaling story, low remap | Tuning vnode strategy |
| Fixed slots (e.g., slot ranges) | Deterministic ownership and tooling | More explicit rebalance coordination |

## Failure-day playbook

1. Detect unhealthy node quickly.
2. Remove from active routing set.
3. Serve from replicas.
4. Backfill or heal once node returns/replaced.
5. Validate parity before restoring normal placement.

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Says "use consistent hashing" with no redistribution or failure detail |
| 3 | Explains ring lookup and vnodes |
| 5 | Quantifies remap, addresses hotspots, replicas, and operations |

## Common pitfalls

- Assuming consistent hashing alone solves hot keys
- Ignoring replica placement across failure domains
- No explanation of metadata/ring update propagation
- Using modulo hashing while claiming low remap behavior

## Follow-up questions

1. How many vnodes would you start with and why?
2. How do you place replicas across zones/racks?
3. How do you detect and mitigate hot keys?
4. How do you safely roll out membership changes?
5. When would you choose slot ranges over a ring?

## Variants and extensions

- Rendezvous hashing
- Jump consistent hash
- Bounded-load consistent hashing
- Capacity-aware weighted rings

## Real-world usage notes

- Cassandra-style token ownership with replication
- Dynamo-like partition placement strategies
- Load balancer stickiness and session affinity
- Distributed cache routing with low churn

## GenAI notes

Useful patterns in GenAI systems:
- Sticky routing by tenant or session to improve cache locality
- Stable partition ownership for conversation memory backends
- Controlled rebalance during autoscaling of retrieval workers

## Real-world examples

### Amazon Dynamo
- Uses consistent hashing with virtual nodes
- Each node owns multiple token ranges
- Data replicated to N successive nodes
- **DynamoDB** (AWS managed): Automatic partition management using consistent hashing
- See [Big Data Structures](../../00-theory/data-structures/big-data-structures.md) for implementation patterns

### Apache Cassandra
- Token ring based on consistent hashing
- Virtual nodes (vnodes) for better distribution (default: 256 vnodes/node)
- Configurable replication factor (RF=3 common)
- **Gossip protocol** for ring membership
- Wide-column NoSQL database optimized for write-heavy workloads
- Use case: Time-series data, IoT, messaging platforms

### Redis Cluster
- 16,384 hash slots (fixed, not pure hash ring)
- Each node owns a range of slots
- Slots can be moved between nodes for resharding
- **CRC16 hash** of keys maps to slots
- See [Redis](../redis/) for detailed Redis Cluster architecture and deployment patterns

### Nginx
- Consistent hashing for upstream selection
- Used with `hash ... consistent` directive

## Complexity Analysis

| Operation | Time Complexity |
|-----------|-----------------|
| Find server for key | O(log n) with binary search |
| Add server | O(k) where k = vnodes per server |
| Remove server | O(k) where k = vnodes per server |
| Space | O(n * k) for n servers, k vnodes |

## Key Takeaways

1. **Minimal redistribution**: Only K/n keys move when adding/removing nodes (vs almost all with modulo)

2. **Virtual nodes are essential**: 100-200 vnodes per server provides good balance

3. **Used everywhere**: Caching, databases, load balancing all use consistent hashing

4. **Replication friendly**: Easy to replicate to N clockwise neighbors

5. **Consider alternatives**: Jump hash or rendezvous hashing for specific use cases

---

## GenAI Notes

Consistent hashing is useful in LLM systems where request routing and state locality matter:

| GenAI Scenario | Hash Key | Benefit |
|----------------|----------|---------|
| **Inference gateway routing** | tenant_id or model_id | Stable routing reduces cold starts and cache thrash |
| **Conversation memory partitioning** | conversation_id | Keeps context/state lookups localized |
| **Vector retrieval worker assignment** | query hash or index shard id | Minimizes reassignment during autoscaling |

**Design reminder:** in GenAI systems, pair consistent hashing with replication and health-aware routing so failures do not degrade response quality.

## Related Concepts
- [Load Balancing](../load-balancing/) - Consistent hashing for sticky sessions
- [Database Sharding](../database-sharding/) - Partitioning with consistent hashing
- [Caching](../caching/) - Distributing cache across nodes
- [CAP Theorem](../cap-theorem/) - Availability and consistency trade-offs under partition
- [Redis](../redis/) - Redis Cluster uses hash slots (consistent hashing variant)
- [Big Data Structures](../../00-theory/data-structures/big-data-structures.md) - Consistent hashing implementation details
