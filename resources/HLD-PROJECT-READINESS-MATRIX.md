# HLD Project Readiness Matrix

This matrix separates "folder exists" from "interview-ready design." It is paired with `scripts/check_hld_project_readiness.py`, which checks `DESIGN.md` for placeholder language, concrete APIs, data model detail, capacity assumptions, failure/recovery handling, and strong-answer linkage.

## Status Vocabulary

| Status | Meaning |
|---|---|
| `validated` | The current design passes the readiness checker for its scoped project. |
| `needs-depth-review` | The project passes structural gates but still needs manual editorial depth before release-ready claims. |
| `wave-2-target` | One of the five first-pass projects selected because prior docs were thin or generic. |
| `environment-blocked` | Source looks structurally ready, but diagram rendering or Java validation requires unavailable local tooling. |

## Matrix

| Project | Status | Readiness Gate | Notes |
|---|---|---|---|
| [Ad Click Aggregator](../04-hld-projects/ad-click-aggregator/) | validated | `check_hld_project_readiness.py --only ad-click-aggregator` | Wave 8 adds domain-specific constraints, storage notes, failure paths, and candidate-speakable strong-answer lines. |
| [Bot Detection](../04-hld-projects/bot-detection/) | validated | `check_hld_project_readiness.py --only bot-detection` | Baseline ML/platform variant. |
| [Bot Detection Platform](../04-hld-projects/bot-detection-platform/) | validated | `check_hld_project_readiness.py --only bot-detection-platform` | Advanced variant with inline diagram rationale. |
| [Brokerage Platform](../04-hld-projects/brokerage-platform/) | validated | `check_hld_project_readiness.py --only brokerage-platform` | Requires financial correctness and market-data depth review. |
| [Chat Service](../04-hld-projects/chat-service/) | validated | `check_hld_project_readiness.py --only chat-service` | Existing code and diagram pack; needs readiness pass. |
| [Collaborative Doc Editor](../04-hld-projects/collaborative-doc-editor/) | validated | `check_hld_project_readiness.py --only collaborative-doc-editor` | Requires CRDT/OT and conflict-depth review. |
| [Content Moderation](../04-hld-projects/content-moderation/) | validated | `check_hld_project_readiness.py --only content-moderation` | Baseline moderation system. |
| [Content Moderation Platform](../04-hld-projects/content-moderation-platform/) | validated | `check_hld_project_readiness.py --only content-moderation-platform` | Advanced ML safety platform. |
| [Distributed Cache](../04-hld-projects/distributed-cache/) | validated | `check_hld_project_readiness.py --only distributed-cache` | Requires consistency, eviction, and failure-depth review. |
| [E-commerce Backend](../04-hld-projects/ecommerce-backend/) | validated | `check_hld_project_readiness.py --only ecommerce-backend` | Commerce workflow and contention depth review. |
| [File Storage](../04-hld-projects/file-storage/) | validated | `check_hld_project_readiness.py --only file-storage` | Blob/chunk/metadata path review. |
| [Job Scheduler](../04-hld-projects/job-scheduler/) | validated | `check_hld_project_readiness.py --only job-scheduler` | Wave 8 adds schedule semantics, leases, retries, fairness, timezone policy, and candidate-speakable strong-answer lines. |
| [Live Comments](../04-hld-projects/live-comments/) | validated | `check_hld_project_readiness.py --only live-comments` | First-pass target for real-time fanout and moderation depth. |
| [Metrics Monitoring](../04-hld-projects/metrics-monitoring/) | validated | `check_hld_project_readiness.py --only metrics-monitoring` | Wave 8 adds cardinality, rollup, alert-state, partial-result, and candidate-speakable strong-answer depth. |
| [News Feed](../04-hld-projects/news-feed/) | validated | `check_hld_project_readiness.py --only news-feed` | Feed ranking/fanout readiness review. |
| [Notification Service](../04-hld-projects/notification-service/) | validated | `check_hld_project_readiness.py --only notification-service` | Channel routing, retry, preference depth review. |
| [Online Auction](../04-hld-projects/online-auction/) | validated | `check_hld_project_readiness.py --only online-auction` | First-pass target for bid correctness and anti-sniping depth. |
| [Payment System](../04-hld-projects/payment-system/) | validated | `check_interview_readiness.py --only hld-project:payment-system` | Pilot project already has strong readiness evidence. |
| [Price Tracking Service](../04-hld-projects/price-tracking-service/) | validated | `check_hld_project_readiness.py --only price-tracking-service` | First-pass target for crawl scheduling, SKU dedupe, and alert depth. |
| [Quick Commerce Delivery](../04-hld-projects/quick-commerce-delivery/) | validated | `check_hld_project_readiness.py --only quick-commerce-delivery` | Extracted representative diagram source. |
| [Realtime Metrics Platform](../04-hld-projects/realtime-metrics-platform/) | validated | `check_hld_project_readiness.py --only realtime-metrics-platform` | First-pass target for event-time, rollup, cardinality, and alert depth. |
| [Ride Sharing](../04-hld-projects/ride-sharing/) | validated | `check_hld_project_readiness.py --only ride-sharing` | Matching, geospatial, and surge-depth review. |
| [Social Post Search](../04-hld-projects/social-post-search/) | validated | `check_hld_project_readiness.py --only social-post-search` | First-pass target for indexing, ranking, and privacy-filter depth. |
| [Ticketing Platform](../04-hld-projects/ticketing-platform/) | validated | `check_hld_project_readiness.py --only ticketing-platform` | Seat-hold and contention review. |
| [URL Shortener](../04-hld-projects/url-shortener/) | validated | `check_hld_project_readiness.py --only url-shortener` | Classic HLD route and scale review. |
| [Video Recommendations](../04-hld-projects/video-recommendations/) | validated | `check_hld_project_readiness.py --only video-recommendations` | Ranking, feature, and feedback-loop review. |
| [Video Streaming](../04-hld-projects/video-streaming/) | validated | `check_hld_project_readiness.py --only video-streaming` | CDN/transcode/playback depth review. |
| [Web Crawler](../04-hld-projects/web-crawler/) | validated | `check_hld_project_readiness.py --only web-crawler` | Wave 8 adds crawler scope, robots/politeness, frontier storage, failure paths, and candidate-speakable strong-answer depth. |

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_hld_project_readiness.py --all
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_readability_style.py 04-hld-projects resources/HLD-PROJECT-READINESS-MATRIX.md
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py resources/HLD-PROJECT-READINESS-MATRIX.md 04-hld-projects
```
