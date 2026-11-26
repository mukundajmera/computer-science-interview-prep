# 🏆 Coach Answer: Ad Click Aggregator — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## 1. Requirements Clarification

### Functional
1. Receive and validate click events (`event_id`, `ad_id`, `user_id`, `timestamp`).
2. Aggregate clicks by `ad_id` over defined time windows (e.g., 1 minute).
3. Handle deduplication of events so that duplicate event IDs affect billing aggregates exactly once.
4. Correctly assign windows based on event time, explicitly handling late and out-of-order events.
5. Provide query capabilities to fetch aggregated counts.

### Non-Functional
- High throughput ingestion.
- Deterministic tests using mocked time, avoiding `sleep()`.
- Standard-library-only implementation.

---

## 2. API Contract & Reference Behavior

Both Java and Python implement identical reference contracts across versions. Tests deterministically cover the following scenarios:

- **Normal Use-Case:** Ingesting valid unique events incrementally increases the counter for the respective time window.
- **Empty/Invalid Input:** Empty input and invalid event payloads fail predictably. For example, missing fields or null events throw `IllegalArgumentException` / `ValueError`.
- **Duplicate Operation:** Duplicate event IDs affect billing aggregates exactly once; probabilistic filters only accelerate an exact deduplication check (e.g., bitset followed by exact set lookup).
- **Time Policies:** Window-boundary, late-event and out-of-order timestamp examples state processing-time/event-time policy. Late events (e.g., arriving 5 minutes past processing time, or outside watermark window) are discarded. Window assignment relies strictly on event-time.

---

## 3. Version-Specific Feature Deltas

### v1-basic (In-Memory Aggregation & Exact Dedup)
Focuses on the core event ingestion, exact deduplication, and windowing.
- **API:**
  - `AdClickAggregator.ingest(event)`
  - `QueryService.getClicksForAd(adId, windowStart)` / `QueryService.get_clicks_for_ad(adId, windowStart)`
- **Behavior:** Tumbling windowing logic is calculated inline. Empty input and invalid event payloads fail predictably. Deduplication falls back to a hash set for exact checking using a `SimpleBloomFilter`.

### v2-extended (Pluggable Strategies)
Abstracts windowing and deduplication into distinct services.
- **API:**
  - `EventDeduplicator.isDuplicate(eventId)` / `EventDeduplicator.is_duplicate(eventId)`
  - `WindowStrategy.getOverlappingWindows(eventTime)` / `WindowStrategy.get_overlapping_windows(eventTime)`
- **Behavior:** Delegates deduplication to `EventDeduplicator` (using bitset + hash set). Window assignment delegates to `WindowStrategy`, which can support sliding windows. Late event policies compare `processingTime` to `eventTime` (events 5 minutes late are discarded). Includes `FraudRule` checks.

### v3-optimized (Sharded State & Concurrency)
Introduces a concurrent ingestion pipeline and explicit watermark management.
- **API:**
  - `ShardedStateStore.increment(key, count)`
  - `LateEventHandler.isLate(event, currentWatermark)` / `LateEventHandler.is_late(event, current_watermark)`
  - `PartitionRouter.getPartition(key)` / `PartitionRouter.get_partition(key)`
- **Behavior:** Uses a `PartitionRouter` to distribute state across multiple thread locks. `LateEventHandler` and `WatermarkManager` manage the dead-letter routing for excessively delayed events based on event-time watermarks.

---

## 4. Core Architecture

| Entity | Responsibility |
|---|---|
| `AdClickAggregator` | Main pipeline orchestrator for ingestion and querying |
| `EventDeduplicator` | Probabilistic filter + exact check to prevent double-counting |
| `WindowStrategy` | Window assignment (event-time based sliding/tumbling windows) |
| `ShardedStateStore` | Thread-safe, partitioned storage of click counts (v3) |
| `WatermarkManager` | Tracks event-time boundaries (v3) |

---

## 5. Design Notes & Complexity

- **Deduplication:** Duplicate event IDs affect billing aggregates exactly once; probabilistic filters only accelerate an exact deduplication check.
- **Time Semantics:** Window-boundary, late-event and out-of-order timestamp examples state processing-time/event-time policy.
- **Error Handling:** Empty input and invalid event payloads fail predictably, returning clear errors rather than silently corrupting state.

### Time & Space Complexity
- **Ingestion:** `O(1)` per event, including constant-time window calculations and hash-based exact dedup.
- **Space:** `O(E + W)` where `E` is the number of distinct event IDs in the deduplication window, and `W` is the number of active aggregation windows.
