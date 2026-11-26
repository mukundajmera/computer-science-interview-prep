# Car Rental System — Follow-Up Questions

Use these variants to drive deeper interview discussion after the baseline design.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. How would you handle high concurrency during peak holiday booking?
- **Model Answer**: Implement a distributed lock mechanism (Redis) on the specific vehicle ID during the booking transaction. For high read volume (searching), use caching layers that are eventually consistent, but strictly validate upon checkout.

## 2. How to implement dynamic/surge pricing?
- **Model Answer**: Use a Rules Engine (Strategy pattern). The engine evaluates parameters (current inventory level, historical demand, local events) to calculate a multiplier on the base rate dynamically.

## 3. How would you support one-way rentals?
- **Model Answer**: Ensure `Reservation` has distinct `PickUpLocationId` and `DropOffLocationId`. Implement a fleet rebalancing algorithm that runs nightly to identify branches with deficits and surpluses to schedule physical transfers.

## 4. How to scale the search functionality for millions of users?
- **Model Answer**: Offload complex availability searches from the primary transactional database to a dedicated search index (like Elasticsearch). Update the index asynchronously via change data capture (CDC).

## 5. How would you handle a car being damaged or requiring maintenance?
- **Model Answer**: Add a `ReportDamage` API that transitions the vehicle state to `InMaintenance`. Any upcoming reservations for that specific vehicle must automatically trigger an event to reassign a different vehicle of the same class to the user.

## 6. How to manage overbooking policies?
- **Model Answer**: If the business allows overbooking, track 'logical' availability separate from 'physical' availability. Introduce an allocation service that handles upgrading customers to a higher class if their reserved class is overbooked.

## 7. How to manage data retention for old rentals?
- **Model Answer**: Run periodic background jobs to archive completed rental records older than 7 years to cold storage (e.g., AWS S3 or Glacier) for compliance, keeping the hot operational database lean.

## 8. What is your strategy for handling late returns?
- **Model Answer**: Run a cron job that sweeps for overdue rentals. Trigger a late fee calculation strategy and emit events to alert branch managers and potentially lock the vehicle remotely (if telematics are supported).

## 9. How to implement real-time inventory tracking (telematics)?
- **Model Answer**: Vehicles emit GPS/telemetry data via IoT protocols (MQTT). Ingest this via a stream processing system (Kafka) to update a real-time dashboard and automatically log exact return times and mileage.

## 10. How would you design the system to support franchising?
- **Model Answer**: Introduce a multi-tenant architecture. Add a `TenantId` or `FranchiseId` to core tables. Ensure role-based access control (RBAC) so franchisees only see and manage their own fleet, while corporate has global visibility.

---

## Follow-Up Scoring Signals

1. Candidate explains trade-offs, not only feature lists.
2. Candidate preserves API boundaries while extending behavior.
3. Candidate keeps concurrency and safety constraints explicit.
