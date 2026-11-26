# News Feed — Interview Scoring Rubric

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|---|---|---|
| 1 | Requirements | 10% | Defines feed type(s), freshness targets, and scope |
| 2 | Estimation | 10% | Read/write/fan-out math influences design |
| 3 | API Design | 15% | Cursor pagination and follow/post APIs are coherent |
| 4 | Data Model | 15% | Post graph/feed cache model is explicit |
| 5 | Architecture | 20% | Hybrid fan-out + cache + async pipeline |
| 6 | Deep Dives | 20% | Celebrity handling, ranking, and consistency trade-offs |
| 7 | Trade-offs | 10% | Communicates why choices match product goals |

---

## 1. Requirements

- **1:** Vague "timeline" description, no constraints.
- **3:** Covers core social feed flows and SLOs.
- **5:** Explicitly captures social + news-aggregator variant boundaries and staleness targets.

## 2. Estimation

- **1:** No throughput assumptions.
- **3:** Rough post and feed read QPS.
- **5:** Includes fan-out amplification and high-skew publisher effects.

## 3. API Design

- **1:** Offset-only pagination and incomplete contracts.
- **3:** Basic feed/follow/post endpoints.
- **5:** Cursor semantics, versioned contracts, and error model are clear.

## 4. Data Model

- **1:** No graph or feed cache model.
- **3:** Basic post and follow tables.
- **5:** Distinguishes source content, fanout artifacts, and ranking metadata.

## 5. Architecture

- **1:** Single service box.
- **3:** Layered services with queue/cache mentions.
- **5:** Correctly separates write fan-out, read merge, and ranking.

## 6. Deep Dives

- **1:** No celebrity or hotspot strategy.
- **3:** Mentions hybrid fan-out conceptually.
- **5:** Details thresholding, cache layout, pagination stability, and ranking fallback.

## 7. Trade-offs & Communication

- **1:** Tool list without reasoning.
- **3:** Some alternatives listed.
- **5:** Clear, structured decision rationale tied to feed goals.

---

## Instagram Variant Signals

Strong answers for the Instagram variant should additionally cover:

1. Media metadata and blob-delivery separation.
2. Celebrity and hotspot fan-out strategy.
3. Timeline freshness bounds vs ranking quality trade-off.
4. Clear interaction between feed service and media CDN path.
