# 🏆 Coach Answer: Ticketing Platform — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Browse/search events.
2. View seat map availability.
3. Hold seats briefly.
4. Confirm booking with payment.

### Non-Functional

| Metric | Target |
|---|---|
| Search latency | < 500 ms P99 |
| Hold latency | < 250 ms P99 |
| Booking correctness | No double-booking |
| Availability | 99.95%+ |

### Out of Scope

- Fraud engine internals.
- Promoter tooling workflows.

---

## Phase 2 — Capacity (5 min)

- Peak onsale events can exceed 100K seat actions/sec.
- Traffic is burst-heavy and highly skewed by event popularity.
- Reads are dominant except during hold/checkout windows.

---

## Phase 3 — APIs (5 min)

```http
GET /api/v1/events
GET /api/v1/events/{eventId}/seats
POST /api/v1/holds
POST /api/v1/bookings
```

Require idempotency key on booking.

---

## Phase 4 — Data Model (5 min)

- `Seat(event_id, seat_id, state, version)`
- `SeatHold(hold_id, user_id, seat_ids, expires_at)`
- `Booking(booking_id, hold_id, state, amount)`

State machine: `AVAILABLE -> HELD -> BOOKED`, with TTL expiry back to `AVAILABLE`.

---

## Phase 5 — Architecture (10 min)

- API Gateway + admission queue/rate controls.
- Search/Event read services.
- Seat Hold service backed by TTL lock store.
- Booking orchestrator with payment and ticket issuance.
- Async notification/reconciliation pipeline.

---

## Phase 6 — Deep Dives (10 min)

1. **Onsale throttling:** queue admission and fairness.
2. **Hold ownership:** lock granularity and release semantics.
3. **Partial failures:** payment success + booking failure reconciliation.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Hold store | TTL lock cache | Long DB locks | Lower latency, controlled expiry |
| Booking consistency | Strong transition checks | Eventual updates | Prevents duplicate seat sales |
| Surge handling | Admission control | Open flood | Preserves system stability |

### Follow-Up Extensions

1. Resale/transfer lifecycle.
2. Group seating adjacency optimization.
3. Multi-region event partitioning.
