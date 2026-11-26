# Ticketing Platform — System Comparison

## Ticketing vs E-commerce Backend

| Concern | Ticketing Platform | E-commerce Backend |
|---|---|---|
| Inventory type | Non-fungible seat IDs | Mostly fungible SKU counts |
| Contention profile | Extreme short bursts | Broad traffic with periodic flash spikes |
| Hold timeout | Minutes | Usually longer cart windows |
| Correctness risk | Double-booking same seat | Overselling count-based inventory |

## Ticketing vs News Feed

| Concern | Ticketing Platform | News Feed |
|---|---|---|
| Consistency need | Strong on booking path | Eventual feed freshness acceptable |
| Primary bottleneck | Write contention during holds | Read fan-out and ranking |
| User perception | Must never sell same seat twice | Slight delay tolerated |

## Ticketing vs Ride Sharing

| Concern | Ticketing Platform | Ride Sharing |
|---|---|---|
| Matching unit | Seat selection | Driver-rider assignment |
| Window sensitivity | Onsale launch window | Continuous real-time matching |
| Critical lock | Seat hold ownership | Driver assignment ownership |

---

## Reuse Guidance

- Reuse queue-admission ideas from large event systems.
- Reuse idempotent orchestration patterns from payments/order systems.
- Reuse optimistic concurrency patterns from high-contention inventory domains.
