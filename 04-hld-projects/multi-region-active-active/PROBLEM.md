# Multi-Region Active-Active Architecture — Problem Statement

## 1. Context

As a theoretical global user base expands, serving all traffic from a single geographic region introduces unacceptable latency for users in distant continents and creates a single point of failure. The goal is to design a multi-region active-active system where users are routed to their closest region (US, EU, APAC) for optimal latency, while data remains globally consistent and available.

This project focuses on the foundational routing, replication, and conflict resolution mechanisms required to make a theoretical active-active deployment work.

## 2. Core User Value
- Consistently low latency (under 50ms) regardless of the user's global location.
- Uninterrupted service during regional cloud provider outages.

## 3. Requirements and Constraints

### Functional Requirements
- **Global Routing:** Route traffic to the geographically closest healthy region.
- **Data Replication:** Replicate mutations across three primary continents (US, EU, APAC) in near real-time.
- **Conflict Resolution:** Safely resolve concurrent mutations to the same entity across different regions.
- **Read-After-Write Consistency:** Users must see their own updates immediately, even if they reconnect to a different region due to failover.
- **Partition Recovery:** Regions must automatically sync and recover gracefully after a network split-brain scenario.

### Non-Functional Requirements
- **Availability:** 99.999% (Five Nines).
- **Read Latency:** < 50ms at p99.
- **Write Latency:** < 200ms at p99 (for cross-region commit or async replication depending on consistency model).
- **Cross-Region Replication Lag:** < 1 second under normal conditions.

## 4. Specific Challenges to Address
1. **Anycast vs. GeoDNS:** Choosing the optimal routing layer for performance and failover speed.
2. **Replication Topologies:** Multi-master replication vs. single-writer with fast read replicas.
3. **Conflict Resolution:** Implementing LWW (Last-Write-Wins) with Hybrid Logical Clocks (HLC), CRDTs, or Spanner-style TrueTime limits.
4. **Session Pinning:** Sticky sessions versus read tokens with version vectors for read-after-write consistency.
5. **Split-Brain Fencing:** Preventing data corruption during complete network partitions.
