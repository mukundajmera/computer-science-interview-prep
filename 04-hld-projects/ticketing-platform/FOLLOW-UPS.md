# Ticketing Platform — Follow-Up Questions

## 1. How do you handle bot traffic at onsale time?

Add layered bot mitigation: queue token issuance, device fingerprint checks, per-account quotas, and risk scoring before hold creation.

## 2. How would resale marketplace support change design?

Introduce `TicketOwnership` ledger and transfer workflow with anti-duplication checks, transfer windows, and fraud policies.

## 3. What if one user opens multiple sessions and hoards seats?

Add per-user active-hold limits and anti-hoarding heuristics; release oldest holds when thresholds are exceeded.

## 4. How do you support group checkout for adjacent seats?

Add seat-group search service and atomic multi-seat hold semantics with rollback if adjacency constraints fail.

## 5. What changes for multi-region?

Partition events by primary region, replicate read models globally, and keep booking authority region-local per event.

## 6. How do you improve seat-map freshness without overloading storage?

Publish seat-state deltas over lightweight channels and blend client-side map state with periodic server snapshots.
