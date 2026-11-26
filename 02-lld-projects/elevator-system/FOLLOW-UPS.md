# Elevator System — Follow-Up Questions

Use these variants to drive deeper interview discussion after the baseline design.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md)

---

## 1. How would you optimize for 100+ floors?

- Introduce floor zones and zone-owned elevator pools.
- Add express elevators and optional sky-lobby transfers.
- Keep fallback overflow policy when a zone is saturated.

## 2. How do you model emergency/fire mode?

- Add emergency state transitions with strict override semantics.
- Stop/recall behavior should be deterministic and safe.
- Clear or freeze incoming queues based on policy.

## 3. How would you support VIP/priority requests safely?

- Add request priority and aging guard to avoid starvation.
- Use a priority-aware dispatch strategy, not hard-coded branching.
- Define fairness SLA (for example, maximum allowed wait window).

## 4. How do you handle peak-hour traffic?

- Introduce strategy switching by time and observed traffic profile.
- Lobby-first up-peak mode for morning rush.
- Keep at least one elevator in general mode to prevent full starvation.

## 5. What monitoring would you add?

- Emit events: assignment latency, wait time, trip time, skipped calls.
- Track per-elevator utilization and queue depth.
- Use observer/pub-sub hooks to keep core movement logic decoupled.

## 6. How would you support maintenance with minimal disruption?

- Drain current passengers, mark out-of-service, redistribute requests.
- Rejoin as `IDLE` with controlled warm-up placement.
- Keep maintenance state visible to dispatcher and displays.

---

## Follow-Up Scoring Signals

1. Candidate explains trade-offs, not only feature lists.
2. Candidate preserves API boundaries while extending behavior.
3. Candidate keeps concurrency and safety constraints explicit.

---

## Additional Variants

1. Destination control system (collect destination at lobby kiosk).
2. Group dispatch with per-bank coordination.
3. Carbon/energy-aware dispatch policy.
4. Deterministic replay mode for dispatch debugging and regression testing.

---

## Cross-Links

- Approach flow: [APPROACH](./APPROACH.md)
- Related LLD extension set: [Parking Lot Follow-Ups](../parking-lot/FOLLOW-UPS.md)
- Related state-machine extension set: [Amazon Locker Follow-Ups](../amazon-locker/FOLLOW-UPS.md)
- Related deterministic turn-loop design: [Connect Four Follow-Ups](../connect-four/FOLLOW-UPS.md)
- Pattern library: [01-design-patterns](../../01-design-patterns/README.md)
