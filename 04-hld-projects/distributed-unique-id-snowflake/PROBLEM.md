# Distributed Unique ID Generator (Snowflake)

## Problem Statement

Design a distributed unique ID generator that generates 64-bit numerical identifiers at scale in a highly available and low-latency manner. The IDs must be strictly monotonic (time-ordered), collision-free, and sortable by time. The system should be able to withstand clock drift and NTP backward clock shifts.

---

## Requirements and Constraints

### Functional Requirements

1. **Unique IDs:** The system must generate globally unique 64-bit IDs.
2. **Sortable by Time:** IDs must be sortable by generation time (strictly monotonic over time).
3. **Numerical Format:** IDs must be 64-bit integers to fit in standard database index types (`BIGINT`).
4. **Collision-free:** No two nodes or threads can generate the same ID at the same time.
5. **Decentralized Generation:** ID generation should not require a central coordination point for every request.

### Non-Functional Requirements

- **High Availability:** The system should have 99.999% availability. ID generation is a critical path for many downstream systems.
- **Low Latency:** ID generation must take less than 1-2 milliseconds at the tail (P99).
- **High Throughput:** The system must support generating over 10,000 IDs per second per node.
- **Resilience to Clock Drift:** The system must detect and handle backward clock shifts caused by NTP syncs without generating duplicate IDs or blocking indefinitely.
- **Scalability:** The system should support horizontally scaling up to at least 1,024 generator nodes.

### Assumptions and Environment Constraints

- **System Lifespan:** The ID generation system is expected to operate for at least 69 years before epoch exhaustion.
- **Datacenters:** The system will be deployed across multiple datacenters.
- **Dependencies:** ZooKeeper/etcd is available for worker node registration and coordination (but is not on the hot path for ID generation).

---

## Out of Scope

- Storing the generated IDs (the system only generates and returns them).
- Mapping IDs to external entities or payloads.
- Resolving arbitrary logical clocks (we rely on system monotonic clocks + custom epoch).
