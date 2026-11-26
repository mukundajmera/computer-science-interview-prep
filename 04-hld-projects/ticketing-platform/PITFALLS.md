# Ticketing Platform — Common Interview Pitfalls

## 1. Modeling Seats as Simple Inventory Counts

Seat inventory is non-fungible. Missing per-seat identity leads to oversell edge cases.

## 2. Long Database Locks for Entire Checkout

Holding DB transactions for minutes blocks throughput and causes lock contention storms.

## 3. No Hold Expiry Ownership Check

Booking without validating hold owner and hold TTL enables duplicate or stale purchases.

## 4. Missing Idempotency for Booking/Payment

Retries without idempotency create duplicate bookings and payment confusion.

## 5. Ignoring Onsale Admission Control

Without queue/rate control, even healthy downstream services collapse at launch time.

## 6. Coupling Search and Booking Paths

Search traffic spikes should not degrade the correctness-critical booking path.

## 7. No Recovery/Reconciliation Story

Real systems need post-failure reconciliation for partial payment/booking outcomes.

---

## Quick Self-Check

- Did I define seat state transitions?
- Did I isolate high-contention write path?
- Did I include idempotency and retry handling?
- Did I describe degraded mode during spikes?
