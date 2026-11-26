# Quick Commerce Delivery — Common Interview Pitfalls

## 1. Confusing Catalog With Deliverable Inventory

Catalog presence does not guarantee one-hour deliverability from nearby centers.

## 2. Ignoring Geo-Locality in Availability Queries

Without proximity filtering, read latency and relevance degrade quickly.

## 3. No Strong Inventory Commit Strategy

Eventual decrements alone can oversell under concurrent order placement.

## 4. Cache Without Invalidation Discipline

Fast caches become harmful when stale values persist during spikes.

## 5. One Shared Critical Path

Combining read and write bottlenecks causes cascading failures under load.

## 6. Missing Idempotency on Order Creation

Client retries can produce duplicate orders when no idempotency key is enforced.

## 7. No Degraded Strategy

A practical design must state what still works if reservation or geo services are degraded.

---

## Quick Self-Check

- Did I separate read and write consistency requirements?
- Did I model center-level inventory state?
- Did I define lock/OCC behavior for decrements?
- Did I include cache fallback behavior?
