# Interview Questions: ZooKeeper

## Basic Questions

### 1. What problem does ZooKeeper solve?
**A**: It solves distributed coordination: leader election, membership, locks, config distribution, and naming.

### 2. What is a znode?
**A**: A small metadata node in ZooKeeper's hierarchical namespace, available as persistent, ephemeral, or sequential.

### 3. Why are ephemeral nodes useful?
**A**: They automatically disappear on session loss, making liveness tracking straightforward.

## Intermediate Questions

### 4. How does leader election work with ZooKeeper?
**A**: Participants create ephemeral-sequential nodes; lowest sequence is leader; others watch predecessor and re-evaluate when it disappears.

### 5. What is a watch, and what is the common mistake?
**A**: A watch is a one-time notification. Common mistake: forgetting to re-register after an event.

### 6. How do reads and writes behave?
**A**: Writes go through leader and quorum commit; reads can come from followers and may be stale unless client sync behavior is used.

## Advanced Questions

### 7. ZooKeeper vs etcd vs Consul?
**A**: ZooKeeper is mature and recipe-rich; etcd is simpler and cloud-native; Consul adds discovery/health tooling and richer service features.

### 8. How do you avoid herd effects in lock/election patterns?
**A**: Watch only the immediate predecessor znode instead of watching the root path.

### 9. What failure metrics matter most?
**A**: Session expiration rate, leader re-election frequency, write latency, outstanding requests, and ensemble quorum health.

## Common Follow-ups

- How many nodes should the ensemble have and why odd counts?
- What data size should each znode hold?
- How do you rotate configuration safely?

## Red Flags to Avoid

- Using ZooKeeper as a large data store.
- Ignoring session timeout tuning.
- Broadcasting watches from a hot root path.

## 30-second Explanation

"ZooKeeper is a strongly consistent coordination service. I use ephemeral and sequential nodes for membership, election, and locks, and I call out quorum commits, watch semantics, and modern alternatives like etcd/Consul."
