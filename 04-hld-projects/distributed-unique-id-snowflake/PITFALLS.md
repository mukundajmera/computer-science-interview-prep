# Distributed Unique ID Generator (Snowflake) - Common Pitfalls

## Common pitfalls

1. **Ignoring Clock Drift and NTP Syncs**
   - Assuming system time is strictly monotonic.
   - Failing to block or throw an error when the clock moves backward, resulting in duplicate IDs.

2. **Poor Worker ID Management**
   - Hardcoding worker IDs in config files without a scalable way to replace dead nodes or scale up.
   - Allowing nodes to pick random worker IDs, causing potential collisions.

3. **Sequence Exhaustion Mishandling**
   - Failing to realize that if a worker generates > 4096 IDs in a single millisecond, it will overflow into the worker ID bits or reset to 0, causing collisions.
   - Not implementing a thread block/wait until the next millisecond tick.

4. **JavaScript Precision Loss**
   - Returning the 64-bit integer as a raw JSON number, causing JS clients to silently truncate the value due to the 53-bit safe integer limit.

## Why these fail interviews

- **Violation of Requirements:** Returning duplicate IDs directly violates the core "collision-free" requirement.
- **Fragility:** If a single NTP sync can corrupt the primary keys for the entire database cluster, the system is fundamentally unsafe.
- **Operational Complexity:** Manual worker ID management prevents autoscaling in modern cloud environments.

## Mitigations

1. **Explicit Clock Drift Check:** Always store `lastTimestamp` and verify `currentTimestamp >= lastTimestamp`.
2. **Dynamic Leases:** Use ZooKeeper or etcd ephemeral nodes to dynamically lease a worker ID at startup.
3. **Sequence Blocking:** Explicitly loop/sleep until `currentTimestamp > lastTimestamp` if the sequence hits 4095.
4. **String Casting:** Serialize the 64-bit ID as a string at the API boundary.

## Cross-links

- [Problem Statement](./PROBLEM.md)
- [System Design Approach](./APPROACH.md)
- [Detailed Design](./DESIGN.md)
