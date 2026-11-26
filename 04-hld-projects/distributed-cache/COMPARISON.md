# Distributed Cache — Comparison

## Distributed Cache vs URL Shortener Storage

| Concern | Distributed Cache | URL Shortener Storage |
|---|---|---|
| Durability expectation | Often non-durable | Durable canonical mapping required |
| Consistency target | Eventual acceptable | Stronger correctness for writes |
| Expiry model | TTL/eviction-driven | Business-expiry driven |

## Distributed Cache vs Ride Sharing Location Store

| Concern | Distributed Cache | Ride Sharing |
|---|---|---|
| Key distribution | General key space | Geo-indexed location state |
| Hotspot shape | Hot keys | Hot geo zones/events |
| Recovery behavior | Replica promotion + rebalance | Dispatch continuity + state reconciliation |

## Distributed Cache vs Video Streaming Edge Cache

| Concern | Distributed Cache | Video Streaming |
|---|---|---|
| Data granularity | Key-value objects | Segment/manifests |
| Client behavior | Service-to-service | End-user playback |
| Invalidations | Key-based TTL/invalidation | Content takedown and cache purge |
